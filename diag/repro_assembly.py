"""Re-run the failing final xfade assembly from the 5:33 PM run with -loglevel info, watching RSS.
Kills ffmpeg at 2.5 GB RSS so it can't trigger the global OOM killer again (other renders share the box)."""
import glob, os, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import trailer as T
B = T.BUILD
segs = [os.path.join(B, 'seg00_title.mp4')] + sorted(glob.glob(os.path.join(B, 'p*_*/segment.mp4'))) + [os.path.join(B, 'seg_stats.mp4'), os.path.join(B, 'seg99_end.mp4')]
durs = [T.dur(s) for s in segs]
trans = ['fade', 'smoothleft', 'fadeblack', 'smoothup', 'circleopen', 'smoothright', 'dissolve', 'wipeleft']
inputs = sum([['-i', s] for s in segs], [])
fc, last, acc = [], '[0:v]', durs[0]
for i in range(1, len(segs)):
    off = acc - T.XF; tr = 'fade' if i in (1, len(segs) - 1) else trans[i % len(trans)]
    fc.append(f'{last}[{i}:v]xfade=transition={tr}:duration={T.XF}:offset={off:.3f}[x{i}]'); last = f'[x{i}]'; acc = off + durs[i]
fc.append(f'{last}format=yuv420p[v]')
out = '/tmp/repro_video.mp4'
cmd = ['ffmpeg', '-y', '-loglevel', 'info'] + inputs + ['-filter_complex', ';'.join(fc), '-map', '[v]', '-r', '30', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', out]
log = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'repro_assembly.log'), 'w')
log.write(f'{len(segs)} inputs, expected total {acc:.2f}s\n'); log.flush()
p = subprocess.Popen(cmd, stderr=log, stdout=log)
t0 = time.time(); peak = 0; samples = []
while p.poll() is None:
    try:
        rss = int(open(f'/proc/{p.pid}/status').read().split('VmRSS:')[1].split()[0]) // 1024
    except Exception:
        rss = 0
    peak = max(peak, rss); samples.append((round(time.time() - t0, 1), rss))
    if rss > 2500 or time.time() - t0 > 150:
        p.kill(); p.wait(); break
    time.sleep(1)
summary = f'\n== exit {p.returncode}; peak RSS {peak} MB after {time.time()-t0:.0f}s; samples (s, MB): {samples[::5]}\n'
log.write(summary); print(summary)
