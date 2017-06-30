from queue import Queue, Empty
import threading
from datetime import datetime
import logging
import numpy
import wave
import os, sys
import pyaudio

MIN_MIC_AMPLITUDE = 700
MIN_VOICE_THRESHOLD = 6000
BLOCKING_TIMEOUT = 2
MIN_SEGMENT_DURATION = 0.5 #1 sec min de speech to analyze
RATE = 44100
SECOND_INTERVALS = 0.5 #medio segundo
CHUNK = int(RATE*SECOND_INTERVALS)
WIDTH = 2
CHANNELS = 1
FORMAT = pyaudio.paInt16

logger = logging.getLogger('AudioAnalyzer')
logger.setLevel(logging.DEBUG)


def to_flac(filename, delete_wav_file=False):
    os.system("flac -f "+filename) #Create a flac file
    filename_flac =  filename.split(".")[0]+".flac"
    logger.debug("Created %s", filename_flac)
    if delete_wav_file:
        os.remove(filename)
    #TODO send to google


def save_record(frames, filename="result.wav"):
    print("Save ", filename)
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(2)
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def analyze_voice_segment(voice_segment, start_time):
    logger.info("New voice segment at %s to analyze", str(start_time))
    logger.info("Len of voice segment: %d", len(voice_segment))
    if len(voice_segment) > MIN_SEGMENT_DURATION/SECOND_INTERVALS:
        filename = str(start_time)+".wav"
        save_record(voice_segment, filename)
        logger.debug("Created %s", filename)
        to_flac(filename, True)
        # threading.Thread(target=to_flac, args=(filename, True)).start()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) < 2:
        print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
        sys.exit(-1)
    print(sys.argv)
    wf = wave.open(sys.argv[1], 'rb')
    data = wf.readframes(CHUNK)
    chunk_start = 0
    segment = []
    start_time_segment = None
    while len(data) > 0:
        amplitude = numpy.fromstring(data, numpy.int16)
        m = max(abs(amplitude))
        logger.debug("length of segment: %d ,max amplitud %d", len(amplitude), m)
        if m > MIN_VOICE_THRESHOLD:
            if segment == []:
                start_time_segment = chunk_start
            segment.append(data)
        else:
            if segment != []:
                analyze_voice_segment(segment, start_time_segment)
                segment = []
                start_time_segment = None
        data = wf.readframes(CHUNK)
        chunk_start += SECOND_INTERVALS
    if segment != []:
        analyze_voice_segment(segment, start_time_segment)

    logger.info("*Done processing*")
