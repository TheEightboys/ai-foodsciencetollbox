#!/usr/bin/env bash
set -euo pipefail

# Upload local dist/ to SiteGround via rsync over SSH.
# Usage (preferred):
# SITEGROUND_HOST=example.com SITEGROUND_USER=me SITEGROUND_PATH=/home/me/public_html/ai SITEGROUND_SSH_KEY=~/.ssh/id_rsa ./scripts/deploy_siteground.sh
# Or set env vars in your shell/session.

: "${SITEGROUND_HOST:?Set SITEGROUND_HOST}"
: "${SITEGROUND_USER:?Set SITEGROUND_USER}"
: "${SITEGROUND_PATH:?Set SITEGROUND_PATH}"

SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

if [[ -n "${SITEGROUND_SSH_KEY:-}" ]]; then
  echo "Using provided SSH key"
  SSH_COMMAND="ssh -i ${SITEGROUND_SSH_KEY} ${SSH_OPTS}"
else
  echo "Using default SSH agent / key from ssh-agent"
  SSH_COMMAND="ssh ${SSH_OPTS}"
fi

if [[ ! -d dist ]]; then
  echo "dist/ not found — please run 'npm run build' first"
  exit 1
fi

echo "Deploying dist/ → ${SITEGROUND_USER}@${SITEGROUND_HOST}:${SITEGROUND_PATH}"
rsync -avz --delete -e "${SSH_COMMAND}" dist/ "${SITEGROUND_USER}@${SITEGROUND_HOST}:${SITEGROUND_PATH}"

echo "Deployment finished. Verify https://ai.foodsciencetoolbox.com/"
