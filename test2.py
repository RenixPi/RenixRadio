import soundcard as sc
import struct

BLOCKSIZE = 512
NUMFRAMES = 256

speakers = sc.all_speakers()
s = speakers[0]
print(s)

mics = sc.all_microphones(include_loopback=True)
#print(mics)
m = mics[5]
print(m)

def has_audio(data):
    for d in data:
        if abs(d) > 0.05:
            return True

with m.recorder(blocksize=BLOCKSIZE,  samplerate=48000) as mic, s.player(blocksize=BLOCKSIZE, samplerate=48000) as sp:

    print(type(mic))
    print(type(sp))

    while True:
        data = mic.record(numframes=NUMFRAMES)
        sp.play(data)

#for _ in range(1000):
#    data = m.record(samplerate=48000, numframes=48000)
#    speaker = s.play(data, samplerate=48000)

