import soundcard as sc
import struct

BLOCKSIZE = 512
NUMFRAMES = 256

mics = sc.all_microphones(include_loopback=True)
mic = mics[5]
print(mic)
recorder = mic.recorder(samplerate=48000, blocksize=BLOCKSIZE)
recorder.__enter__()

spkrs = sc.all_speakers()
spkr = spkrs[0]
print(spkr)
player = spkr.player(samplerate=48000, blocksize=BLOCKSIZE)
player.__enter__()

while True:
    data = recorder.record(numframes=NUMFRAMES)
    player.play(data)

recorder.__exit__()
player.__exit__()
