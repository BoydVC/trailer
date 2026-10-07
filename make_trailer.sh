#!/usr/bin/env bash
# Re-render the Build Night trailer. Re-scans /workspace/tokenmax/*/ so any project that now has a
# README.md and screenshots/ gets its own segment, and re-measures every stat and usage.json.
#   ./make_trailer.sh           full render -> out/build-night-trailer-1080p.mp4, out/build-night-trailer-720p.gif,
#                               out/contact-sheet.png, out/manifest.json
#   ./make_trailer.sh --scan    just list which projects, screenshots and pitches would be used
set -euo pipefail
cd "$(dirname "$0")"
for t in ffmpeg ffprobe sox python3; do command -v "$t" >/dev/null || { echo "missing $t"; exit 1; }; done
python3 trailer.py "$@"
[ "${1:-}" = "--scan" ] || ls -la out/
