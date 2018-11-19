import csv
import json
import sys

import numpy


def main():
    if len(sys.argv) >= 2:
        input_filename = sys.argv[1]
    else:
        print('You have to specify an input filename as a first argument.')
        return

    if len(sys.argv) >= 3:
        input_mode = sys.argv[2]
    else:
        print('You have to specify mode as a second argument.')
        return

    with open(input_filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        # for row in reader:
        #     print(row)

        raw_data = {}

        for row in reader:
            student_data = {}

            for key, value in row.items():
                if key == 'student':
                    continue
                else:
                    parsed = key.strip().replace(' ', '').split('/')
                    # print(parsed)

                    if input_mode == 'dates':
                        output_key = parsed[0]
                    elif input_mode == 'deadlines':
                        output_key = '/'.join(parsed)
                    else:
                        output_key = parsed[1]

                    if output_key not in student_data:
                        student_data[output_key] = 0

                    student_data[output_key] += float(value)

            for key, value in student_data.items():
                if key not in raw_data:
                    raw_data[key] = []

                raw_data[key].append(value)

        # print(raw_data)
        output = {}
        for key, values in raw_data.items():
            #print(key, sorted(values))
            output[key] = {
                'passed': numpy.count_nonzero(numpy.array(values)),
                'first': numpy.percentile(numpy.array(values), 25),
                'last': numpy.percentile(numpy.array(values), 75),
                'median': numpy.median(numpy.array(values)),
                'mean': numpy.mean(numpy.array(values)),
            }

        print(json.dumps(output, indent=4))


if __name__ == '__main__':
    main()
