import re
import sys
import numpy
import wave
import struct


def main():
    if len(sys.argv) >= 2:
        input_filename = sys.argv[1]
    else:
        print('You have to specify an input filename as a first argument.')
        return

    wave_reader = wave.open(input_filename, 'rb')
    sample_width = wave_reader.getsampwidth()
    channels = wave_reader.getnchannels()
    framerate = wave_reader.getframerate()

    lowest_peak_set = False
    lowest_peak = -1

    highest_peak_set = False
    highest_peak = -1

    format = '<' + ('h' * channels * framerate)
    while wave_reader.tell() < wave_reader.getnframes():
        frames = wave_reader.readframes(framerate)
        if len(frames) == channels * framerate * sample_width:
            decoded = struct.unpack(format, frames)

            fft_input = []
            for i in range(0, len(decoded), 2):
                chunk = decoded[i:i + 2]
                fft_input.append((chunk[0] + chunk[1])/2.0)

            rfft_result = numpy.fft.rfft(fft_input)
            average_amplitude = sum([numpy.abs(bucket) for bucket in rfft_result])/len(rfft_result)
            #print(average_amplitude)

            for frequency_bucket, amplitude in enumerate(rfft_result):
                if numpy.abs(amplitude) >= average_amplitude * 20:
                    if not lowest_peak_set or frequency_bucket < lowest_peak:
                        lowest_peak_set = True
                        lowest_peak = frequency_bucket
                    if not highest_peak_set or frequency_bucket > highest_peak:
                        highest_peak_set = True
                        highest_peak = frequency_bucket
                    # print(frequency_bucket, numpy.abs(amplitude))

    if lowest_peak_set and highest_peak_set:
        print('low = %s, high = %s' % (lowest_peak, highest_peak))
    else:
        print('no peaks')


if __name__ == '__main__':
    main()
