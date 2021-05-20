import soundcard as sc
import struct

mics = sc.all_microphones(include_loopback=True)
spkrs = sc.all_speakers()

for count, value in enumerate(mics):
    print("{} : {}".format(count, value))

for count, value in enumerate(spkrs):
    print("{} : {}".format(count, value))
