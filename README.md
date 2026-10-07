# Build Night Trailer

A cinematic 60–90 s trailer of everything TokenMax built on Oct 7, 2026 from Boyd's leftover Grok Bot usage.

| Output | Path |
|---|---|
| 1080p30 H.264 + AAC MP4 | `out/build-night-trailer-1080p.mp4` |
| 720p H.264 + AAC MP4 for sharing in chat (kept under 20 MB) | `out/build-night-trailer-720p.mp4` |
| 720p GIF (kept under 15 MB) | `out/build-night-trailer-720p.gif` |
| Contact sheet, one frame per segment | `out/contact-sheet.png` |
| What went in: projects, screenshots, pitches, stats, timeline | `out/manifest.json` |

## Re-render at the end of the night
```bash
./make_trailer.sh --scan   # preview which projects, screenshots and pitches would be used
./make_trailer.sh          # full render (10–30 min, depending on how busy the box is)
```
Each render re-scans `/workspace/tokenmax/*/`. Any folder with a `README.md` **and** at least one image in `screenshots/` gets its own segment, so projects that finish later are picked up automatically. Stats are re-measured and `usage.json` is re-read on every render. **Refresh `usage.json` before the final render**, because the gauge shows whatever that file says.

## Structure
1. **Title card:** "TokenMax presents: Build Night, Oct 7, 2026" over a generated starfield with a slow push-in.
2. **One segment per project,** 5–8 s, scaled so the whole trailer lands near 76 s. Each segment has:
   - 2–3 screenshots with Ken Burns moves (ffmpeg `zoompan` on 3× upscaled frames for smooth motion) and an `xfade` between them.
   - The project name and a one-line pitch taken from the start of its README. Long pitches are trimmed at a clause and end in "…".
   - A meta line with that project's measured lines of code, screenshots and test files.
   - `drawtext` for the "03 / 13" counter and the "TOKENMAX · BUILD NIGHT" tag.

   Projects appear in the order they were finished (newest README or screenshot last), with the Hub at the end.
   **When there are too many projects for 5 s each within 90 s** (more than about 17), the 90 s cap wins: the title, stats and end cards get shorter (4.0 / 6.5 / 4.0 s) and every project gets an equal share. Past about 24 projects the cards shrink again (3.6 / 6.0 / 3.6 s) and the per-project share can drop to 2.6 s (2 screenshots at 3.0 s or more, 1 below that), so the trailer never runs past 90 s. `out/manifest.json` records this in `fit_note`.
3. **The night in numbers:** projects, files, lines of code, screenshots and test files counting up, plus the usage gauge from `usage.json`.
4. **End card:** "Built before the reset."

All segments are joined with `xfade` transitions.

## How the render stays reliable on a busy box
The first version joined all ~25 segments in one ffmpeg `xfade` graph. That opened every decoder at once; on Oct 7 at 5:43 PM it reached 4.3 GB and the kernel OOM killer stopped it (`command failed: ffmpeg`, with no ffmpeg error because the process was SIGKILLed). Re-running that step at `-loglevel info` (`diag/repro_assembly.py`, log in `diag/repro_assembly.log`) passed 2.5 GB within 5 seconds, before writing a single frame.

The render now works like this:
- **Two jobs at a time** (`TRAILER_JOBS`, default 2), each ffmpeg capped at 3 encoder threads (`TRAILER_FF_THREADS`).
- **Pairwise assembly:** each transition piece decodes only two segments (the previous segment's last 0.7 s and the current segment). Every piece is encoded the same way and normalized to TV-range yuv420p.
- **Verified pieces:** before the join, ffprobe checks each piece's codec, size, pixel format, frame rate and exact frame count. A piece that fails is re-rendered.
- **Lossless join:** the concat demuxer joins the pieces without re-encoding, then the total frame count is checked again.
- **Retries:** every ffmpeg/sox step is retried up to 3 times with backoff (`TRAILER_RETRIES`). Each attempt's full `-loglevel info` output is in `build/logs/`, and an OOM kill is reported as such.
- **Staging:** outputs are rendered to `build/stage/`, verified (duration 55–91 s, audio stream present), then moved into `out/`. A failed render never replaces the last good trailer.

**Screenshot picks:** the README's first embedded screenshot comes first, then the most visually rich ones (colour plus edge density). The picker skips near-duplicates by name family and skips offline/snapshot/sources/outage/empty frames.

**Music:** synthesized with sox. Pads are an Am–F–C–G progression of triangle and sine voices with lowpass, chorus and reverb. The beat is a soft sine kick, a band-passed noise tick and hats at 84 BPM. It comes in after the title and drops out for the end card. Loudness is normalized quietly (`loudnorm` I=−24 LUFS, true peak −3 dB).

## How the stats are measured (never typed in)
- **Projects:** folders that qualify, as above.
- **Files:** every file in those folders except `node_modules`, `.venv`, `venv`, `vendor*`, `__pycache__`, `.git` and `.cache`.
- **Lines of code:** non-blank lines in `.py .js .mjs .cjs .ts .html .css .sh`. Excluded: `dist/`, `data/`, bundles and minified files (average line over 300 chars, or files over 1 MB), and vendored libraries.
- **Screenshots:** image files in each `screenshots/` folder.
- **Test files:** code files in each `tests/` folder.
- **Usage gauge:** `used_pct`, `checked_at` and `reset_date` from `/workspace/tokenmax/usage.json`, shown as-is.

## Files
`make_trailer.sh` (entry point), `trailer.py` (scan, art, ffmpeg/sox pipeline), `build/` (intermediates and per-step logs, recreated each run), `out/` (deliverables), `diag/` (OOM reproduction and test scripts).

The 720p MP4 is encoded from the 1080p master with CRF 24 plus a VBV cap sized from the duration, so it lands under 20 MB. If it doesn't, it retries at a higher CRF. The GIF holds one still per screenshot on the same timeline. If it is still over 15 MB, it steps down through fewer stills per project and smaller palettes, and only then to 960 px wide; the settings used are in `manifest.json`.

## Final render (Oct 7, 6:48 PM ET)
Rendered with:
`TRAILER_OUT=$PWD/out_new2 TRAILER_JOBS=3 TRAILER_EXCLUDE=slack-pulse,docket-pilot,trip-kit TRAILER_SHOT_OVERRIDE=fleet-funnies=08-build-night-special.png python3 trailer.py`
After it passed verification, it was swapped into `out/`. The 5:54 PM render is kept in `out-prev-0554pm/`.
- `TRAILER_OUT` sets the output folder. `TRAILER_EXCLUDE` takes comma-separated slugs to leave out. Slack Pulse and Docket Pilot hold work data, and every Trip Kit screenshot shows the flight confirmation code in its header.
- `TRAILER_SHOT_OVERRIDE` takes `slug=file.png` and forces that screenshot first.
- Trailing parentheticals in project names, such as "(TokenMax build night, Oct 7 2026)", are now dropped so each name fits on one line.


---
## Repo notes
- **Built:** Oct 7, 2026, by TokenMax (Boyd's Grok Bot) on the Grok Bot box.
- **Run:** See the notes above; mostly docs/data.
- Imported from `/workspace/tokenmax/trailer` on Oct 23, 2026. node_modules, virtualenvs, logs and files over 20 MB were left out.
