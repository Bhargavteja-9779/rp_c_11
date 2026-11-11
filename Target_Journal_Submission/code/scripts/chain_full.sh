#!/usr/bin/env bash
# Wait for a running E1 process (if any), then run all remaining full experiments (resumable).
cd "$(dirname "$0")/.."
while pgrep -f "run_all.py --mode full --only E1" > /dev/null; do sleep 30; done
python3 run_all.py --mode full >> logs/full_all.log 2>&1
echo "CHAIN DONE $(date -u +%FT%T)" >> logs/full_all.log
