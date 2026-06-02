#!/bin/bash
# Local dev workflow: sync code to server, rebuild, run tests
# Usage: bash deploy_test.sh

set -e
SERVER="root@47.104.242.174"
SSH_OPTS="-o StrictHostKeyChecking=no -o ConnectTimeout=10"

echo "=== 1. Syncing code to server ==="
rsync -avz --exclude '.git' --exclude '__pycache__' --exclude '*.pyc' \
    --exclude 'node_modules' --exclude '.next' --exclude 'venv' \
    --exclude 'test_local.py' --exclude 'deploy_test.sh' \
    -e "ssh $SSH_OPTS" \
    ./ "$SERVER:/opt/multimorag/"

echo "=== 2. Rebuilding Docker ==="
ssh $SSH_OPTS "$SERVER" "cd /opt/multimorag && docker compose up -d --build 2>&1 | tail -5"

echo "=== 3. Waiting for services ==="
sleep 5

echo "=== 4. Running E2E tests ==="
ssh $SSH_OPTS "$SERVER" 'bash /tmp/e2e.sh'

echo "=== Done ==="
