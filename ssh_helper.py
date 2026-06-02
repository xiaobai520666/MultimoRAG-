"""SSH helper for connecting to the deployment server."""
import sys
import paramiko

HOST = "47.104.242.174"
USER = "root"
PASSWORD = "Zwd123456.."

def run(host=None, user=None, password=None, cmd="hostname"):
    """Execute command on remote server via SSH with password auth."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            hostname=host or HOST,
            username=user or USER,
            password=password or PASSWORD,
            timeout=30,
        )
        stdin, stdout, stderr = client.exec_command(cmd)
        out = stdout.read().decode()
        err = stderr.read().decode()
        exit_code = stdout.channel.recv_exit_status()
        return exit_code, out, err
    finally:
        client.close()

if __name__ == "__main__":
    cmd = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "hostname && uptime"
    ec, out, err = run(cmd=cmd)
    print(f"EXIT: {ec}")
    if out:
        print(out)
    if err:
        print(f"STDERR: {err}")
