import csv
import json
import sys
import math
from datetime import datetime, date

import numpy


def main():
    if len(sys.argv) >= 2:
        input_filename = sys.argv[1]
    else:
        print('You have to specify an input filename as a first argument.')
        return

    if len(sys.argv) >= 3:
        input_id = sys.argv[2]
    else:
        print('You have to specify student id as a second argument.')
        return

    with open(input_filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        # for row in reader:
        #     print(row)

        input_data = None

        if input_id == 'average':
            points_sum = {}
            count = {}
            for row in reader:
                for key, value in row.items():
                    if key == 'student':
                        continue

                    if key not in points_sum:
                        points_sum[key] = 0.0
                    points_sum[key] += float(value)

                    if key not in count:
                        count[key] = 0
                    count[key] += 1

            input_data = {}
            for key, value in points_sum.items():
                input_data[key] = value/count[key]
            input_data['student'] = 'average'

            #print(input_data)
        else:
            for row in reader:
                if row['student'] != input_id:
                    continue
                else:
                    input_data = row

        raw_points = []
        points_by_date = []

        raw_data_exercise = {}
        raw_points_per_date = {}

        for key, value in input_data.items():
            if key == 'student':
                continue
            else:
                parsed = key.strip().replace(' ', '').split('/')
                # print(parsed)

                output_key = parsed[1]

                if output_key not in raw_data_exercise:
                    raw_data_exercise[output_key] = 0

                raw_data_exercise[output_key] += float(value)

                if parsed[0] not in raw_points_per_date:
                    raw_points_per_date[parsed[0]] = 0

                raw_points_per_date[parsed[0]] += float(value)

        for key, value in raw_data_exercise.items():
            raw_points.append(value)

        for key, points in raw_points_per_date.items():
            points_by_date.append((key, points))

        # print(points_by_date)

        dates = []
        points = []
        for key, value in sorted(points_by_date, key=lambda k: k[0]):
            dates.append(datetime.strptime(key, '%Y-%m-%d').date().toordinal())
            points.append(value)

        for i in range(1, len(points)):
            points[i] = points[i - 1] + points[i]

        start_date = datetime.strptime('2018-9-17', '%Y-%m-%d').date().toordinal()
        dates = numpy.array([date - start_date for date in dates])

        # print(dates, points)

        regression_slope = numpy.linalg.lstsq([[date] for date in dates], points, rcond=-1)[0][0]

        output = {
            'passed': numpy.count_nonzero(numpy.array(raw_points)),
            'median': numpy.median(numpy.array(raw_points)),
            'mean': numpy.mean(numpy.array(raw_points)),
            'total': sum(raw_points),
            'regression slope': regression_slope,

        }
        if regression_slope != 0:
            output['date 16'] = date.fromordinal(math.floor((16.0 / regression_slope) + start_date)).__str__()
            output['date 20'] = date.fromordinal(math.floor((20.0 / regression_slope) + start_date)).__str__()

        print(json.dumps(output, indent=4))


if __name__ == '__main__':
    main()
