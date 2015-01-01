from synth.interfaces import SampleGenerator
import numpy


class Delay(SampleGenerator):

    def __init__(self, options, delay_nr_of_samples = 4):
        super(Delay, self).__init__(options)
        self.source = None
        self.delay_nr_of_samples = delay_nr_of_samples
        self.delayed = numpy.array([])

    def set_source(self, source):
        self.source = source
        
    def get_samples(self, nr_of_samples, phase, release = None):
        if self.source is None:
            return numpy.zeros(nr_of_samples)
        samples = self.source.get_samples(nr_of_samples, phase, release)
        new_delayed = samples[-self.delay_nr_of_samples:].copy()

        if self.delay_nr_of_samples > nr_of_samples:
            if phase + nr_of_samples > self.delay_nr_of_samples:
                if phase > self.delay_nr_of_samples:
                    start_index = 0
                else:
                    start_index = self.delay_nr_of_samples - phase
                length = nr_of_samples - start_index
                samples[start_index:] = samples[start_index:] + self.delayed[:length]
                samples[start_index:] /= 2.0
                self.delayed = self.delayed[length:]
            self.delayed = numpy.concatenate((self.delayed, new_delayed))
        else:
            delayed = samples[:-self.delay_nr_of_samples]
            samples[self.delay_nr_of_samples:] = samples[self.delay_nr_of_samples:] + delayed
            if phase > 0:
                samples[:self.delay_nr_of_samples] = samples[:self.delay_nr_of_samples] + self.delayed
                samples /= 2.0
            else:
                samples[self.delay_nr_of_samples:] /= 2.0
            self.delayed = new_delayed
        return samples
