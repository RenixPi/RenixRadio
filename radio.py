from enum import Enum
from fuzzywuzzy import fuzz

import soundcard as sc
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

try:
    from systemd import journal
except ImportError:
    pass
else:
    logger.addHandler(journal.JournaldLogHandler())


SAMPLERATE = 48000
BLOCKSIZE = 512
NUMFRAMES = 256

FUZZ_MATCHING = 70
MIN_PLAYING_COUNT = 500
SILENCE = 0.01

SPEAKER_NAME = "USB PnP Sound Device Analog Stereo"
MIC_NAME = "USB PnP Sound Device"
LOOPBACK_NAME = "Loopback Monitor of Null Output"


class Inputs(Enum):
    CHANNEL1 = 1
    CHANNEL2 = 2
    OPENDSH = 3


def speaker_name_matcher(spkr):
    r = fuzz.ratio(SPEAKER_NAME, spkr.name)
    pr = fuzz.partial_ratio(SPEAKER_NAME, spkr.name)
    return r > FUZZ_MATCHING and pr > FUZZ_MATCHING


def mic_name_matcher(mic):
    r = fuzz.ratio(MIC_NAME, mic.name)
    pr = fuzz.partial_ratio(MIC_NAME, mic.name)
    logging.debug("{} : {} {}".format(mic.name, r, pr))
    return r > FUZZ_MATCHING and pr > FUZZ_MATCHING


def loopback_name_matcher(lb):
    r = fuzz.ratio(LOOPBACK_NAME, lb.name)
    pr = fuzz.partial_ratio(LOOPBACK_NAME, lb.name)
    return r > FUZZ_MATCHING and pr > FUZZ_MATCHING


def start_mixer():

    all_speakers = sc.all_speakers()
    (spkr,) = filter(speaker_name_matcher, all_speakers)

    # spkrs = sc.all_speakers()
    # spkr = spkrs[0]
    # print(spkr)
    output1 = spkr.player(samplerate=SAMPLERATE, blocksize=BLOCKSIZE)
    output1.__enter__()

    all_inputs = sc.all_microphones()
    print(all_inputs)
    (mic1,) = filter(mic_name_matcher, all_inputs)

    all_inputs = sc.all_microphones(include_loopback=True)
    (loopback,) = filter(loopback_name_matcher, all_inputs)

    # mics = sc.all_microphones(include_loopback=True)
    # mic = mics[5]
    # print(mic)
    opendsh = loopback.recorder(samplerate=SAMPLERATE, blocksize=BLOCKSIZE)
    opendsh.__enter__()

    while True:
        data = opendsh.record(numframes=NUMFRAMES)
        output1.play(data)

    opendsh.__exit__()
    output1.__exit__()


if __name__ == "__main__":
    start_mixer()