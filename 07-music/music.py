import sys
import numpy
import wave
import struct
import math


def get_tone(base, freq):
    note_names = [
        'C', 'Cis', 'D',
        'Es', 'E', 'F',
        'Fis', 'G', 'Gis',
        'A', 'Bes', 'B'
    ]

    base_log = base
    base_log *= pow(2, -(len(note_names) + 9) / len(note_names))
    distance = len(note_names) * (math.log2(freq) - math.log2(base_log))
    cents = distance % 1
    cents *= 100
    cents = int(round(float(cents)))
    tones_diff, octaves_diff  = int(distance % len(note_names)), int(distance // len(note_names))

    if cents >= 50:
        tones_diff += 1
        cents = - (100 - cents)

    if tones_diff >= 12:
        tones_diff -= 12
        octaves_diff += 1

    if octaves_diff < 0:
        return '{}{:+d}'.format(note_names[tones_diff] + (',' * (-1 * octaves_diff)), cents)
    else:
        return '{}{:+d}'.format(note_names[tones_diff].lower() + ("'" * octaves_diff), cents)


def main():
    if len(sys.argv) >= 2:
        base_freq = int(sys.argv[1])
    else:
        print('You have to specify a base frequency as a first argument.')
        return

    if len(sys.argv) >= 3:
        input_filename = sys.argv[2]
    else:
        print('You have to specify an input filename as a second argument.')
        return

    wave_reader = wave.open(input_filename, 'rb')
    sample_width = wave_reader.getsampwidth()
    channels = wave_reader.getnchannels()
    framerate = wave_reader.getframerate()

    frame_count = wave_reader.getnframes()
    total_data_bytes = wave_reader.readframes(frame_count)
    format = "%ih" % (channels * frame_count)
    total_data = [x for x in struct.unpack(format, total_data_bytes)]

    sample_size = int(framerate/10)

    window = []
    outputs = []
    start = 0.0
    end = 0.1
    while total_data:
        frames = total_data[:sample_size]
        del total_data[:sample_size]
        if len(frames) == sample_size:
            decoded = frames

            if channels == 2:
                fft_input = []
                for i in range(0, len(decoded), 2):
                    chunk = decoded[i:i + 2]
                    fft_input.append((chunk[0] + chunk[1])/2.0)
            else:
                fft_input = decoded

            window += fft_input

            if len(window) < framerate:
                continue

            while len(window) > framerate:
                del window[:sample_size]

            rfft_result = numpy.fft.rfft(window)
            average_amplitude = sum([numpy.abs(bucket) for bucket in rfft_result])/len(rfft_result)

            peaks = []
            for frequency_bucket, amplitude in enumerate(rfft_result):
                if numpy.abs(amplitude) >= average_amplitude * 20:
                    peaks.append((frequency_bucket, numpy.abs(amplitude)))

            clusters = []
            current_cluster = []
            for peak in peaks:
                if not current_cluster:
                    current_cluster.append(peak)

                if abs(current_cluster[-1][0] - peak[0]) <= 1:
                    current_cluster.append(peak)
                else:
                    clusters.append(current_cluster)
                    current_cluster = [peak]
            if current_cluster:
                clusters.append(current_cluster)

            cluster_peaks = []
            for cluster in clusters:
                highest_amplitude = sorted(cluster, key=lambda k: -k[1])
                cluster_peaks.append(highest_amplitude[0])

            output_raw = []
            for index, peak in enumerate(sorted(cluster_peaks, key=lambda k: -k[1])):
                if index > 2:
                    break
                output_raw.append(peak)

            output = []
            for peak in sorted(output_raw, key=lambda k: k[0]):
                output.append(get_tone(base_freq, peak[0]))
                
            outputs.append((start, end, output))
            start += 0.1
            end += 0.1

    # merge outputs
    current_peaks = []
    current_start = 0.0
    current_end = 0.0
    for output in outputs:
        if not current_peaks:
            current_start = output[0]
            current_end = output[1]
            current_peaks = output[2]

        if sorted(current_peaks) != sorted(output[2]):
            print('%.1f-%.1f %s' % (current_start, current_end, " ".join(current_peaks)))
            current_start = output[0]
            current_end = output[1]
            current_peaks = output[2]
        else:
            current_end = output[1]
    if current_peaks:
        print('%.1f-%.1f %s' % (current_start, current_end, " ".join(current_peaks)))


if __name__ == '__main__':
    main()
