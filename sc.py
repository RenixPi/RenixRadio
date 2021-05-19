import soundcard as sc
import struct

speakers = sc.all_speakers()
print(speakers)
s = speakers[0]
print(s)

mics = sc.all_microphones()
print(mics)
m = mics[0]
print(m)

def has_audio(data):
    for d in data:
        if abs(d) > 0.05:
            return True

with m.recorder(samplerate=48000) as mic, s.player(samplerate=48000) as sp:
    for _ in range(10000):
        data = mic.record(numframes=1024)
        sp.play(data)
