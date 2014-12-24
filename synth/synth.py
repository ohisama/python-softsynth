#!/usr/bin/env python
import pyaudio
import struct
import math
import time
from mingus.midi import midi_file_in
import multiprocessing
import sys
import cProfile
import wave
from options import Options
from waves import SineWave, SquareWave, RandomWave, Adder
from envelopes import ConstantFrequencyEnvelope, BendFrequencyEnvelope,\
                      ConstantAmplitudeEnvelope, ADSRAmplitudeEnvelope
from note_envelopes import ConstantNoteEnvelope, ArpeggioNoteEnvelope, TrackNoteEnvelope
from instruments import OvertoneInstrument, PercussionInstrument


class Synth(object):
    def __init__(self):
        self.instruments = []

    def add_instrument(self, instrument):
        self.instruments.append(instrument)

    def get_amplitude(self, options, t):
        value = 0
        playing = 0
        for i in self.instruments:
            v = i.get_amplitude(options, t)
            if v != 0.0:
                value += v
                playing += 1
        if playing == 0:
            return 0
        return value / playing

class WaveWriter(object):

    def __init__(self, options, filename):
        self.options = options
        self.filename = filename

    def open(self):
        self.data = []

    def write(self, elem):
        sample = struct.pack(self.options.struct_pack_format, int(elem))
        self.data.append(sample)

    def close(self):
        w = wave.open(self.filename, "w")
        w.setnchannels(1)
        w.setsampwidth(self.options.byte_rate)
        w.setframerate(self.options.sample_rate)
        w.writeframes(''.join(self.data))
        w.close()
        print "Written", self.filename

options = Options()
freq_table = options.get_frequency_table()
amplitude_generator = None
GLOBAL_TIME = 0

def callback(in_data, frame_count, time_info, status):
    global GLOBAL_TIME, options
    data = []
    for t_frame in xrange(frame_count):
        sample = struct.pack(options.struct_pack_format, 
            int(amplitude_generator.get_amplitude(options, int(GLOBAL_TIME + t_frame))))
        data.append(sample)
    GLOBAL_TIME += frame_count
    return ''.join(data), pyaudio.paContinue

def profile_call():
    global amplitude_generator
    map(lambda i: amplitude_generator.get_amplitude(options, i), xrange(44100))

def profile():
    if "--profile" in sys.argv:
        cProfile.run('profile_call()')
        sys.exit(0)

def create_synth_from_midi_tracks(tracks):
    synth = Synth()
    for t in tracks:
        instr = OvertoneInstrument
        for b in t.bars:
            for nc in b.bar:
                for n in nc[2]:
                    if hasattr(n, "channel"):
                        if n.channel == 9:
                            instr = PercussionInstrument
                        break
        instrument = instr(freq_table, TrackNoteEnvelope(options, t))
        synth.add_instrument(instrument)
    return synth

def use_default_synth():
    global amplitude_generator
    instrument = OvertoneInstrument(freq_table, ArpeggioNoteEnvelope())
    amplitude_generator = instrument

def process_midi_files():
    global amplitude_generator
    use_default_synth()
    for f in sys.argv:
        if ".mid" in f:
            (composition, bpm) = midi_file_in.MIDI_to_Composition(sys.argv[1])
            tracks = filter(lambda t: len(t.bars) != 1, composition.tracks)
            synth = create_synth_from_midi_tracks(tracks)
            amplitude_generator = synth
            break

def main():
    process_midi_files()
    profile()
    output = pyaudio.PyAudio()
    stream = output.open(format=pyaudio.paInt16, channels=1, 
            rate= 44100, output=True, stream_callback=callback)
    stream.start_stream()
    while stream.is_active():
        time.sleep(0.1)
    stream.stop_stream()
    stream.close()

if __name__ == '__main__':
    main()