#!/usr/bin/env bash
# ==============================================================================
# Root deploy launcher for hr-agent
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${SCRIPT_DIR}/hr-agent/deploy.sh" "$@"
