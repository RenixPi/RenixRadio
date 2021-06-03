import soundcard as sc
from fuzzywuzzy import fuzz

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

SAMPLE_RATE = 48000
BLOCK_SIZE = 512
NUM_FRAMES = 256

SPEAKER_NAME = "Speaker USB PnP Sound Device"
INPUT_NAME = "Microphone USB PnP Sound Device"
LOOPBACK_NAME = "Loopback Monitor of Null Output"

FUZZ_MATCHING = 50
MIN_PLAYING_COUNT = 500
SILENCE = 0.01


class Inputs(Enum):
    CHANNEL1 = 1
    CHANNEL2 = 2
    OPENDSH = 3


def is_silent(data):
    for d in data:
        if abs(d) > SILENCE:
            return False
    return True


def speaker_name_matcher(spkr):
    r = fuzz.ratio(SPEAKER_NAME, spkr.name)
    pr = fuzz.partial_ratio(SPEAKER_NAME, spkr.name)
    return r > FUZZ_MATCHING and pr > FUZZ_MATCHING


def mic_name_matcher(mic):
    r = fuzz.ratio(INPUT_NAME, mic.name)
    pr = fuzz.partial_ratio(INPUT_NAME, mic.name)
    return r > FUZZ_MATCHING and pr > FUZZ_MATCHING


def find_loopback_port():
    r, pr = 0.0, 0.0
    for m in sc.all_microphones(include_loopback=True):
        r = fuzz.ratio(LOOPBACK_NAME, m.name)
        pr = fuzz.ratio(LOOPBACK_NAME, m.name)
        print("{} : {} {}".format(m.name, r, pr))
        if r > FUZZ_MATCHING and pr > FUZZ_MATCHING:
            return m

    logger.warning("could not find loopback port: {} {}".format(r, pr))
    return None


def start_mixer():

    all_speakers = sc.all_speakers()
    (spkr1, spkr2) = filter(speaker_name_matcher, all_speakers)

    all_inputs = sc.all_microphones()
    (mic1, mic2) = filter(mic_name_matcher, all_inputs)

    input1 = mic1.recorder(samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE)
    input1.__enter__()

    input2 = mic2.recorder(samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE)
    input2.__enter__()

    lb = find_loopback_port()
    opendsh = lb.recorder(samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE)
    opendsh.__enter__()

    output1 = spkr1.player(samplerate=SAMPLE_RATE)
    output1.__enter__()

    output2 = spkr2.player(samplerate=SAMPLE_RATE)
    output2.__enter__()

    player = None
    playing_count = 0

    while True:

        playing = None

        i1 = input1.record(numframes=NUM_FRAMES)
        i2 = input2.record(numframes=NUM_FRAMES)
        od = opendsh.record(numframes=NUM_FRAMES)

        if player == Inputs.CHANNEL1 and playing_count < MIN_PLAYING_COUNT:
            output1.play(i1)
            output2.play(i1)
            playing = Inputs.CHANNEL1
        elif player == Inputs.CHANNEL2 and playing_count < MIN_PLAYING_COUNT:
            output1.play(i2)
            output2.play(i2)
            playing = Inputs.CHANNEL2
        elif player == Inputs.OPENDSH and playing_count < MIN_PLAYING_COUNT:
            output1.play(od)
            output2.play(od)
            playing = Inputs.OPENDSH
        elif not is_silent(i1):
            output1.play(i1)
            output2.play(i1)
            playing = Inputs.CHANNEL1
        elif not is_silent(i2):
            output1.play(i2)
            output2.play(i2)
            playing = Inputs.CHANNEL2
        else:
            output1.play(od)
            output2.play(od)
            playing = Inputs.OPENDSH

        if playing != player:
            logger.debug("switching to player: {}".format(playing))
            player = playing
            playing_count = 0
        else:
            playing_count += 1

print(__name__)
print(__file__)
if __name__ == "__main__":

    start_mixer()
