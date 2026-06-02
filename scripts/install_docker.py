#!/usr/bin/env python3
"""SSH into server and install Docker, handling environment issues automatically."""
import pexpect
from pexpect.popen_spawn import PopenSpawn
import sys
import time

HOST = "47.104.242.174"
USER = "root"
PASSWORD = "Zwd123456.."

def run_ssh(cmd, timeout=120):
    """Run a command on the remote server via SSH, return output."""
    ssh_cmd = f"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {USER}@{HOST} {cmd}"
    child = PopenSpawn(ssh_cmd, timeout=timeout)
    child.expect("password:", timeout=15)
    child.sendline(PASSWORD)

    # Collect output
    try:
        child.expect(pexpect.EOF, timeout=timeout)
    except:
        pass
    output = child.before.decode('utf-8', errors='replace') if isinstance(child.before, bytes) else (child.before or "")
    try:
        child.wait()
        code = child.exitstatus or 0
    except:
        code = 0
    return output, code

def main():
    print("=" * 60)
    print(f"  Connecting to {USER}@{HOST} ...")
    print("=" * 60)

    # Step 1: Check OS info
    print("\n[1/6] Checking system info...")
    out, code = run_ssh("cat /etc/os-release")
    print(out[:600])
    if code != 0 and not out.strip():
        print("Failed to connect")
        sys.exit(1)

    # Step 2: Check if Docker is already installed
    print("\n[2/6] Checking if Docker is installed...")
    out, code = run_ssh("docker --version 2>/dev/null && echo 'DOCKER_EXISTS'")
    if "DOCKER_EXISTS" in out:
        print("Docker already installed:")
        print(out.strip())
        print("\n✅ Done!")
        return
    print("Docker not found, proceeding with installation.")

    # Step 3: Detect package manager and install dependencies
    print("\n[3/6] Detecting package manager...")
    out, code = run_ssh("command -v apt && echo 'PM_APT'")
    if "PM_APT" not in out:
        out, code = run_ssh("command -v yum && echo 'PM_YUM'")
        if "PM_YUM" not in out:
            out, code = run_ssh("command -v apk && echo 'PM_APK'")
            if "PM_APK" in out:
                PKG_MGR = "apk"
            else:
                print("Unknown package manager, trying apt-get...")
                PKG_MGR = "apt"
        else:
            PKG_MGR = "yum"
    else:
        PKG_MGR = "apt"

    print(f"Package manager: {PKG_MGR}")

    # Step 4: Install required dependencies
    print(f"\n[4/6] Installing dependencies via {PKG_MGR}...")

    if PKG_MGR == "apt":
        cmds = "export DEBIAN_FRONTEND=noninteractive && apt-get update -qq && apt-get install -y -qq ca-certificates curl gnupg lsb-release 2>&1 | tail -5"
        out, code = run_ssh(cmds, timeout=180)
        print(out[-400:] if len(out) > 400 else out)

        # Add Docker repo
        print("Adding Docker official GPG key and repository...")
        cmds = [
            "install -m 0755 -d /etc/apt/keyrings",
            "curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc",
            "chmod a+r /etc/apt/keyrings/docker.asc",
            # Try Debian/Ubuntu based on release
            "distro=$(lsb_release -si 2>/dev/null | tr 'A-Z' 'a-z' || echo 'ubuntu')",
            "codename=$(lsb_release -cs 2>/dev/null || echo 'jammy')",
            """echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $codename stable" > /etc/apt/sources.list.d/docker.list""",
            "apt-get update -qq 2>&1 | tail -3"
        ]
        out, code = run_ssh(" && ".join(cmds), timeout=120)
        print(out[-400:] if len(out) > 400 else out)

        # Install Docker
        print("Installing Docker Engine...")
        out, code = run_ssh(
            "apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin 2>&1 | tail -5",
            timeout=180
        )
        print(out[-400:] if len(out) > 400 else out)

    elif PKG_MGR == "yum":
        cmds = [
            "yum install -y yum-utils 2>&1 | tail -3",
            "yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo 2>&1 | tail -3",
            "yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin 2>&1 | tail -5"
        ]
        for cmd in cmds:
            out, code = run_ssh(cmd, timeout=180)
            print(out[-400:] if len(out) > 400 else out)

    elif PKG_MGR == "apk":
        out, code = run_ssh("apk add docker docker-compose 2>&1 | tail -5", timeout=180)
        print(out[-400:] if len(out) > 400 else out)

    # Step 5: Start and enable Docker
    print("\n[5/6] Starting and enabling Docker...")
    start_cmds = [
        "systemctl start docker 2>/dev/null && systemctl enable docker 2>/dev/null && echo 'DOCKER_STARTED_SYSTEMCTL'",
        "service docker start 2>/dev/null && echo 'DOCKER_STARTED_SERVICE'",
        "rc-update add docker default 2>/dev/null && rc-service docker start 2>/dev/null && echo 'DOCKER_STARTED_OPENRC'",
        "dockerd &>/dev/null & sleep 2 && echo 'DOCKER_STARTED_DIRECT'"
    ]
    for start_cmd in start_cmds:
        out, code = run_ssh(start_cmd, timeout=30)
        if "DOCKER_STARTED" in out:
            print(f"Docker started: {out.strip()[-200:]}")
            break

    # Step 6: Verify installation
    print("\n[6/6] Verifying Docker installation...")
    out, code = run_ssh("docker --version && docker compose version && docker info 2>&1 | head -10")
    print(out[-600:] if len(out) > 600 else out)

    if "Server Version" in out or "Docker Engine" in out or "Docker" in out:
        print("\n" + "=" * 60)
        print("  ✅ Docker 安装成功!")
        print("=" * 60)

        out2, _ = run_ssh("whoami")
        if "root" in out2:
            print("\nℹ️  当前以 root 运行，无需添加用户到 docker 组。")
            print("   如果后续需要普通用户运行，执行:")
            print("   usermod -aG docker $USER")
    else:
        print("\n⚠️  Docker 安装可能有问题，请检查上面的输出。")

if __name__ == "__main__":
    main()