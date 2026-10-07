import glob, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import trailer as T
B = T.BUILD
segs = [('Title', os.path.join(B, 'seg00_title.mp4'))] + [(x, x) for x in sorted(glob.glob(os.path.join(B, 'p*_*/segment.mp4')))] + [('Stats', os.path.join(B, 'seg_stats.mp4')), ('End', os.path.join(B, 'seg99_end.mp4'))]
t = time.time()
frames = [T.vinfo(s)['frames'] for _, s in segs]
print('frames', frames)
starts, total = T.assemble(segs, frames, '/tmp/test_video.mp4')
print('total', total, 'starts', [round(x, 2) for x in starts], 'took', round(time.time() - t))
