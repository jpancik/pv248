import re
import sys
import numpy


def main():
    if len(sys.argv) >= 2:
        input_filename = sys.argv[1]
    else:
        print('You have to specify an input filename as a first argument.')
        return

    # input_coefficients[line_number][letter] = coefficient
    input_coefficients = dict()
    input_dependent_variables = []
    line_count = 0

    for line_number, line in enumerate(open(input_filename, 'r')):
        input_coefficients[line_number] = dict()
        line_count = line_number + 1

        no_spaces = line.replace(' ', '')
        # print(no_spaces)
        for index, part in enumerate(re.findall(r'([+\-=]?[0-9a-z]+)', no_spaces)):
            match = re.match(r'^([+\-=])?(\d*)(\w*)$', part)

            sign = match.group(1)
            if not sign:
                sign = '+'

            coefficient = match.group(2)
            if coefficient:
                coefficient = coefficient
            else:
                coefficient = '1'

            letter = match.group(3)

            # print(sign, coefficient, letter, part)

            if sign == '=':
                input_dependent_variables.append(int(coefficient))
            else:
                input_coefficients[line_number][letter] = int('%s%s' % (sign, coefficient))

    #print(input_coefficients, input_dependent_variables)

    variables = set()
    for row_index, coefficients in input_coefficients.items():
        for letter, coefficient in coefficients.items():
            if letter not in variables:
                variables.add(letter)
    # print(variables)

    coefficient_matrix = []
    for i in range(line_count):
        out = []

        for variable in sorted(list(variables)):
            if i in input_coefficients and variable in input_coefficients[i]:
                out.append(input_coefficients[i][variable])
            else:
                out.append(0)

        coefficient_matrix.append(out)

    augmented_matrix = [row.copy() for row in coefficient_matrix]
    for index, number in enumerate(input_dependent_variables):
        augmented_matrix[index].append(number)

    coefficient_matrix_rank = numpy.linalg.matrix_rank(numpy.array(coefficient_matrix))
    augmented_matrix_rank = numpy.linalg.matrix_rank(numpy.array(augmented_matrix))

    # print(coefficient_matrix_rank, coefficient_matrix)
    # print(augmented_matrix_rank, augmented_matrix)

    if augmented_matrix_rank == coefficient_matrix_rank:
        try:
            # print(coefficient_matrix, input_dependent_variables)
            solutions = numpy.linalg.solve(numpy.array(coefficient_matrix), numpy.array(input_dependent_variables))
            solutions_strings = []
            for variable, solution in zip(sorted(list(variables)), solutions):
                solutions_strings.append('%s = %s' % (variable, solution))
            print('solution: %s' % ", ".join(solutions_strings))
        except:
            solution_space = len(variables) - coefficient_matrix_rank
            print('solution space dimension: %s' % solution_space)
    else:
        print('no solution')


if __name__ == '__main__':
    main()
