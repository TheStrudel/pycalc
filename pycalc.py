import argparse
from numbers import Number
from inspect import getmembers
import re
import math
from operator import (add, sub, truediv, floordiv, mul, mod, pow,
                      eq, ne, lt, gt, le, ge)


module_constants = {item[0]: item[1] for item in getmembers(math) if isinstance(item[1], Number)}
module_functions = {item[0]: item[1] for item in getmembers(math) if callable(item[1])}
module_functions.update({'abs': abs, 'round': round})

priorities = {'==': 0, '!=': 0, '<': 0, '>': 0, '<=': 0, '>=': 0, '(': 0, ')': 0,
              '+': 1, '-': 1, '*': 2, '/': 2, '//': 2, '%': 2, '^': 3, '-u': 4}
arithmetical_operations = {'+': add, '-': sub, '*': mul, '/': truediv, '//': floordiv, '%': mod, '^': pow, '-u': 0}
comparison_operations = {'==': eq, '!=': ne, '<': lt, '>': gt, '<=': le, '>=': ge}


def parse_expression(expression: str) -> list:
    converted_string = re.split(re.compile(r'([\s(),<>+%*^-]|/{1,2}|[!><=]=)'), expression)
    return list(filter(None, [item.replace(' ', '') for item in converted_string]))


def process_negative_numbers(expression: list) -> list:
    index = 0
    minus_counter = 0
    sign_counter = 0
    while index < len(expression):
        if expression[index] == '-':
            minus_counter += 1
            sign_counter += 1
        elif expression[index] == '+':
            sign_counter += 1
        elif sign_counter != 0:
            expression = expression[:index + 1 - sign_counter] + expression[index:]
            index -= sign_counter
            if minus_counter % 2 == 0:
                expression[index] = '+'
            else:
                expression[index] = '-'
            if index - 1 < 0 or expression[index - 1] in arithmetical_operations or \
                    expression[index - 1] == '(' or expression[index - 1] == ',':
                if expression[index] == '-':
                    expression[index] = '-u'
                else:
                    expression = expression[:index] + expression[index + 1:]
            sign_counter = 0
            minus_counter = 0
        index += 1
    return expression


def expression_to_rpn(expression: list):
    result_stack = []
    operator_stack = []

    for index, token in enumerate(expression):
        try:
            result_stack.append(float(token))
            continue
        except (OverflowError, ValueError):
            pass

        if token in arithmetical_operations:
            while operator_stack and priorities[operator_stack[-1]] >= priorities[token]:
                result_stack.append(operator_stack.pop())
            operator_stack.append(token)
        elif token in comparison_operations:
            while operator_stack and operator_stack[-1] != '(' and operator_stack[-1] != ',':
                result_stack.append(operator_stack.pop())
            operator_stack.append(token)
        elif token in module_constants:
            result_stack.append(getattr(math, token))
        elif token in module_functions:
            if expression[index+1] != '(':
                print("ERROR: no opening bracket after function")
                return
            else:
                operator_stack.append([token, 1])
        elif token == '(':
            operator_stack.append(token)
            continue
        elif token == ')':
            while operator_stack and operator_stack[-1] != '(':
                result_stack.append(operator_stack.pop())
            if not operator_stack:
                print("ERROR: incorrect brackets")
                return
            operator_stack.pop()
            if operator_stack and operator_stack[-1][0] in module_functions:
                result_stack.append(operator_stack.pop())
        elif token == ',':
            while operator_stack and operator_stack[-1] != '(':
                result_stack.append(operator_stack.pop())
            last_function_index = 1
            while operator_stack and type(operator_stack[-last_function_index]) is not list:
                last_function_index += 1
            operator_stack[-last_function_index][1] += 1
        else:
            print("ERROR: unknown operation", token)
            return

    result_stack.extend(reversed(operator_stack))
    return result_stack


def calculate_rpn_expression(rpn_expression: list):
    index = 0
    while len(rpn_expression) > 1:
        if type(rpn_expression[index]) is list:
            operation = module_functions[rpn_expression[index][0]]
            function_arguments = []
            number_of_arguments = rpn_expression[index][1]
            ind = number_of_arguments
            while ind > 0:
                function_arguments.append(rpn_expression[index - ind])
                ind -= 1
            result_of_operation = operation(*function_arguments)
            rpn_expression = rpn_expression[:index-rpn_expression[index][1]] \
                             + [result_of_operation] + rpn_expression[index + 1:]
            index = index - number_of_arguments
        elif rpn_expression[index] == '-u':
            rpn_expression[index - 1] = -rpn_expression[index - 1]
            rpn_expression = rpn_expression[:index] + rpn_expression[index + 1:]
            index -= 1
        elif rpn_expression[index] in arithmetical_operations:
            operation = arithmetical_operations[rpn_expression[index]]
            result_of_operation = operation(rpn_expression[index-2], rpn_expression[index-1])
            rpn_expression = rpn_expression[:index - 2] + [result_of_operation] + rpn_expression[index + 1:]
            index -= 2
        elif rpn_expression[index] in comparison_operations:
            operation = comparison_operations[rpn_expression[index]]
            result_of_operation = operation(rpn_expression[index-2], rpn_expression[index-1])
            rpn_expression = rpn_expression[:index - 2] + [result_of_operation] + rpn_expression[index + 1:]
            index -= 2
        else:
            index += 1

    return rpn_expression.pop()


def main():
    parser = argparse.ArgumentParser(description='Pure-python command line calculator')
    parser.add_argument("EXPRESSION", help="expression to be processed")
    args = parser.parse_args()

    string_from_command_line = args.expression

    list_expression = parse_expression(string_from_command_line)
    list_expression = process_negative_numbers(list_expression)

    print(calculate_rpn_expression(expression_to_rpn(list_expression)))


main()
