#!/usr/bin/env bash
# Convenience entry point: delegates to the canonical installer.
set -euo pipefail
exec "$(dirname "$0")/scripts/install/install.sh" "$@"
