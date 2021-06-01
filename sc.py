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

# microphone = None
# speaker = None

print(type(s))
print(type(m))


with m.recorder(samplerate=48000) as mic, s.player(samplerate=48000) as sp:
    data = mic.record(numframes=1024)
    sp.play(data)

    print(type(mic))
    print(type(sp))


for _ in range(1000):
    data = m.record(samplerate=48000, numframes=1024)
    speaker = s.play(data, samplerate=48000)
#
# print(type(microphone))
# print(type(speaker))
#
# data = microphone.record(numframes=1024)
# speaker.play(data)

# mic = m.recorder(samplerate=48000)
# mic.__enter__()
# data = mic.record(numframes=1024)
# mic.__exit__()

