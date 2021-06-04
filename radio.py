from enum import Enum
from fuzzywuzzy import fuzz

import soundcard as sc
import logging
import numpy
from prometheus_client import start_http_server, Gauge, REGISTRY

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

SPEAKER_NAME = "Audio Adapter (Unitek Y-247A) Digital Stereo (IEC958)"
MIC_NAME = "USB PnP Sound Device"
LOOPBACK_NAME = "Loopback Monitor of Null Output"

levels = Gauge('tire_pressure', 'Tire pressure', ['channel', ])


class Inputs(Enum):
    CHANNEL1 = 1
    CHANNEL2 = 2
    OPENDSH = 3


def is_silent(data, channel=""):
    val = abs(numpy.amax(data))
    levels.labels(channel).set(val)
    if abs(numpy.amax(data)) > SILENCE:
        return False
    return True


def speaker_name_matcher(spkr):
    r = fuzz.ratio(SPEAKER_NAME, spkr.name)
    pr = fuzz.partial_ratio(SPEAKER_NAME, spkr.name)
    logging.debug("{} : {} {}".format(spkr.name, r, pr))
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
    (speaker1, ) = filter(speaker_name_matcher, all_speakers)

    output1 = speaker1.player(samplerate=SAMPLERATE, blocksize=BLOCKSIZE)
    output1.__enter__()

    all_inputs = sc.all_microphones()
    (mic1, mic2) = filter(mic_name_matcher, all_inputs)

    input1 = mic1.recorder(samplerate=SAMPLERATE, blocksize=BLOCKSIZE)
    input1.__enter__()
    input2 = mic1.recorder(samplerate=SAMPLERATE, blocksize=BLOCKSIZE)
    input2.__enter__()

    all_inputs = sc.all_microphones(include_loopback=True)
    (loopback,) = filter(loopback_name_matcher, all_inputs)

    opendsh = loopback.recorder(samplerate=SAMPLERATE, blocksize=BLOCKSIZE)
    opendsh.__enter__()

    player = None
    playing_count = 0

    while True:

        playing = None

        i1 = input1.record(numframes=NUMFRAMES)
        i2 = input2.record(numframes=NUMFRAMES)
        od = opendsh.record(numframes=NUMFRAMES)

        if player == Inputs.CHANNEL1 and playing_count > MIN_PLAYING_COUNT:
            output1.play(i1)
            playing = Inputs.CHANNEL1
        elif player == Inputs.CHANNEL2 and playing_count > MIN_PLAYING_COUNT:
            output1.play(i2)
            playing = Inputs.CHANNEL2

        elif not is_silent(i1, "channel1"):
            output1.play(i1)
            playing = Inputs.CHANNEL1
        elif not is_silent(i2, "channel2"):
            output1.play(i2)
            playing = Inputs.CHANNEL2

        else:
            output1.play(od)
            playing = Inputs.OPENDSH

        if playing != player:
            logger.debug("switching to source: {} after {} iterations".format(playing, playing_count))
            player = playing
            playing_count = 0
        else:
            playing_count += 1

    # input1.__exit__()
    # input2.__exit__()
    # opendsh.__exit__()
    # output1.__exit__()


if __name__ == "__main__":
    start_http_server(8082)
    start_mixer()
