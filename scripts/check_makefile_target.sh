#!/bin/bash

# Script to check if a target exists in a Makefile
# Usage: check_makefile_target.sh <target_name> [makefile_path]

set -euo pipefail

TARGET_NAME="${1:-}"
MAKEFILE_PATH="${2:-Makefile}"

if [ -z "$TARGET_NAME" ]; then
    echo "Error: Target name is required" >&2
    echo "Usage: $0 <target_name> [makefile_path]" >&2
    exit 1
fi

if [ ! -f "$MAKEFILE_PATH" ]; then
    echo "Error: Makefile not found at '$MAKEFILE_PATH'" >&2
    exit 1
fi

# Check if the target exists in the Makefile
# Matches lines like "target:" or "target: dependencies"
if grep -qE "^${TARGET_NAME}:" "$MAKEFILE_PATH"; then
    echo "Target '$TARGET_NAME' exists in $MAKEFILE_PATH"
    exit 0
else
    echo "Target '$TARGET_NAME' not found in $MAKEFILE_PATH" >&2
    exit 1
fi
