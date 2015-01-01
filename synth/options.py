import math

class Options(object):
    def __init__(self):

        # Sample and byte rate
        self.sample_rate     = 44100
        self.byte_rate       = 2    # gives 2 ^ (8 * DEFAULT_BYTE_RATE) levels
        self.max_value       = 2 ** (self.byte_rate * 8 - 1) - 1
        
        # See the Python struct module documentation
        STRUCT_PACK_FORMAT = {1: 'b', 2: 'h', 4: 'i', 8: 'q'} 
        self.struct_pack_format = STRUCT_PACK_FORMAT[self.byte_rate]

        # Frequencies
        self.pitch_standard  = 440.0  # pitch of A4
        self.frequency_table = FrequencyTable(self)

        self.two_pi = 2 * math.pi
        self.two_pi_divided_by_sample_rate = self.two_pi / self.sample_rate

        self.bpm = 204
        self.buffer_size = 10000
       
    def get_frequency_table(self):
        return self.frequency_table

class FrequencyTable(object):
    def __init__(self, options):
        self.midi_frequencies = {} # 69 corresponds with a4
        self.initialize_midi_frequencies(options.pitch_standard)
    def initialize_midi_frequencies(self, pitch_standard):
        for i in range(70):
            freq = pitch_standard * 2 ** -(i / 12.0)
            self.midi_frequencies[69 - i] = freq
        for i in range(70):
            freq = pitch_standard * 2 ** (i / 12.0)
            self.midi_frequencies[69 + i] = freq

