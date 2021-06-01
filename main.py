import soundcard as sc
from fuzzywuzzy import fuzz

import struct
from enum import Enum
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

try:
    from systemd import journal
except ImportError:
    pass
else:
    logger.addHandler(journal.JournaldLogHandler())



# speakers = sc.all_speakers()
# print(speakers)
# s = speakers[0]
# print(s)
#
# mics = sc.all_microphones()
# print(mics)
# m0 = mics[0]
# m1 = mics[1]
# #print(m)

SAMPLE_RATE = 48000
BLOCK_SIZE = 512
NUM_FRAMES = 256

SPEAKER_NAME = "Speaker Built-in Audio Stereo"
INPUT_NAME = "Microphone USB PnP Sound Device Multichannel"
LOOPBACK_NAME = "loopback device"

MIN_PLAYING_COUNT = 500


class Inputs(Enum):
    CHANNEL1 = 1
    CHANNEL2 = 2
    OPENDSH = 3


def is_silent(data):
    for d in data:
        if abs(d) > 0.01:
            return False
    return True


def find_speaker_port(name):

    for s in sc.all_speakers():
        r = fuzz.ratio(name, s.name)
        pr = fuzz.partial_ratio(name, s.name)

        if r > 0.5 and pr > 0.5:
            return s

    return False


def find_loopback_port():

    for m in sc.all_microphones(include_loopback=True):
        r = fuzz.ratio(LOOPBACK_NAME, m.name)
        pr = fuzz.ratio(LOOPBACK_NAME, m.name)

        if r > 0.5 and pr > 0.5:
            return m

    return None


def start_mixer():

    speaker = find_speaker_port(SPEAKER_NAME)

    mics = sc.all_microphones()
    lb = find_loopback_port()

    with mics[0].recorder(samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE) as channel1, \
            mics[1].recorder(samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE) as channel2, \
            lb.recorder(samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE) as opendsh:

        player = None
        playing_count = 0

        while True:

            playing = None

            c1 = channel1.record(numframes=NUM_FRAMES)
            c2 = channel2.record(numframes=NUM_FRAMES)
            od = opendsh.record(numframes=NUM_FRAMES)

            if player == Inputs.CHANNEL1 and playing_count < MIN_PLAYING_COUNT:
                speaker.play(c1)
            elif player == Inputs.CHANNEL2 and playing_count < MIN_PLAYING_COUNT:
                speaker.play(c2)
            elif player == Inputs.OPENDSH and playing_count < MIN_PLAYING_COUNT:
                speaker.play(opendsh)
            elif not is_silent(c1):
                speaker.play(c1)
                playing = Inputs.CHANNEL1
            elif not is_silent(c2):
                speaker.play(c2)
                playing = Inputs.CHANNEL2
            else:
                speaker.play(od)
                playing = Inputs.OPENDSH

            if playing != player:
                logger.debug("switching to player: {}".format(playing))
                player = playing
                playing_count = 0
            else:
                playing_count += 1












# bs = 512
#
# channel = None
#
# with m0.recorder(samplerate=48000, blocksize=bs) as mic0, \
#      m1.recorder(samplerate=48000, blocksize=bs) as mic1, \
#      s.player(samplerate=48000, blocksize=bs) as sp:
#
#     for _ in range(10000):
#         d0 = mic0.record(numframes=256)
#         d1 = mic1.record(numframes=256)
#
#         cur = None
#         if is_silent(d1):
#             cur = 1
#             sp.play(d0)
#         else:
#             cur = 2
#             sp.play(d1)
#
#         if channel != cur:
#             print("channel {}".format(cur))
#             channel = cur



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


if __file__ == "main":

    start_mixer()

