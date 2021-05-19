import soundcard as sc
import struct

speakers = sc.all_speakers()
print(speakers)
s = speakers[0]
print(s)

mics = sc.all_microphones()
print(mics)
m0 = mics[0]
m1 = mics[1]
#print(m)

def is_silent(data):
    for d in data:
        if abs(d) > 0.01:
            return False
    return True

bs = 512

channel = None

with m0.recorder(samplerate=48000, blocksize=bs) as mic0, \
     m1.recorder(samplerate=48000, blocksize=bs) as mic1, \
     s.player(samplerate=48000, blocksize=bs) as sp:

    for _ in range(10000):
        d0 = mic0.record(numframes=256)
        d1 = mic1.record(numframes=256)

        cur = None
        if is_silent(d1):
            cur = 1
            sp.play(d0)
        else:
            cur = 2
            sp.play(d1)

        if channel != cur:
            print("channel {}".format(cur))
            channel = cur



#with m.recorder(samplerate=48000) as mic, s.player(samplerate=48000) as sp:
#    for _ in range(10000):
#        data = mic.record(numframes=1024)

        #samples = len(data)/2  # each sample is a short (16-bit)44
        #values = struct.unpack('<%dh' % samples, data)

        #for v in data:
        #    print(v)
#        if has_audio(data):
#            print("receiving loud and clear")

#        sp.play(data)
