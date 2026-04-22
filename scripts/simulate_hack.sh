#!/bin/bash
# H7: work on a temporary copy — never mutate the tracked plan file
set -euo pipefail

PLAN="infrastructure/tfplan.binary"
if [ ! -f "$PLAN" ]; then
  echo "No plan file found. Run 'terraform plan -out=infrastructure/tfplan.binary' first."
  exit 1
fi

TAMPERED=$(mktemp /tmp/tfplan_tampered.XXXXXX)
cp "$PLAN" "$TAMPERED"
echo " " >> "$TAMPERED"

python scripts/tf_guard.py verify "$TAMPERED"
EXIT_CODE=$?

rm -f "$TAMPERED"

if [ "$EXIT_CODE" -ne 0 ]; then
  echo "PASS: tampered plan was correctly rejected"
else
  echo "FAIL: tampered plan was accepted — security gate is broken"
  exit 1
fi
