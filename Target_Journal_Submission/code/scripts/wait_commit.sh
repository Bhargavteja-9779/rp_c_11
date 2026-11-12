#!/usr/bin/env bash
# Wait up to $2 seconds for file $1 to contain "chunk exit", then commit a results snapshot. Prints progress.
f="$1"; t="${2:-560}"
timeout "$t" bash -c "until grep -q 'chunk exit' '$f' 2>/dev/null; do sleep 20; done"
cd /home/user/rp_c_11 || exit 0
git add -A >/dev/null 2>&1 && git commit -q -m "Experiment progress snapshot

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_014QNVznXtAFXYiRvcTCpx9a" >/dev/null 2>&1 && git push -q origin claude/bold-brown-51gr77 >/dev/null 2>&1
echo "$(date -u +%T) chunk_done=$(grep -c 'chunk exit' "$f" 2>/dev/null) | $(tail -1 Target_Journal_Submission/code/logs/full_all.log | cut -c1-90)"
for x in Target_Journal_Submission/code/results/full/*/raw_results.csv; do echo -n "$(basename $(dirname $x)):$(($(wc -l < $x)-1)) "; done; echo
