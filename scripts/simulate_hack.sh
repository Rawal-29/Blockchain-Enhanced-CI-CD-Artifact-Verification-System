#!/bin/bash
PLAN="infrastructure/tfplan.binary"
if [ ! -f "$PLAN" ]; then exit 1; fi
echo " " >> $PLAN
python scripts/tf_guard.py verify $PLAN
if [ $? -ne 0 ]; then echo "✅ Blocked"; else echo "❌ Failed"; fi