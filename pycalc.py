import argparse
import re
import math
from operator import add, sub, truediv, floordiv, mul, mod, pow, eq, ne, lt, gt, le, ge
from inspect import getmembers

MODULE_CONSTANTS = {item[0]: item[1] for item in getmembers(math) if isinstance(item[1], (float, int))}
MODULE_FUNCTIONS = {item[0]: item[1] for item in getmembers(math) if callable(item[1])}
MODULE_FUNCTIONS.update({'abs': abs, 'round': round})

PRECEDENCE = {
    '==': 0, '!=': 0, '<': 0, '>': 0,
    '<=': 0, '>=': 0, '(': 0, ')': 0,
    '+': 1, '-': 1, '*': 2, '/': 2,
    '//': 2, '%': 2, '^': 3, '-u': 4
}
ARITHMETICAL_OPERATIONS = {
    '+': add, '-': sub, '*': mul, '/': truediv,
    '//': floordiv, '%': mod, '^': pow, '-u': 0
}
COMPARISON_OPERATIONS = {
    '==': eq, '!=': ne, '<': lt,
    '>': gt, '<=': le, '>=': ge
}
RIGHT_ASSOCIATIVE = {'^'}


def parse_expression(expression: str) -> list:
    """ Parse input string via regular expressions, then remove blank spaces and empty elements left by re.split """
    if not expression:
        raise Exception('Empty expression')
    converted_string = re.split(re.compile(r'([!><=]=|[\s(),<>+%*^-]|/{1,2})'), expression)
    return list(filter(None, [item.replace(' ', '') for item in converted_string]))


def process_negative_numbers(expression: list) -> list:
    """ Remove unnecessary sign tokens and replace unary minuses with '-u' token """
    index = 0
    minus_counter = 0
    sign_counter = 0
    while index < len(expression):
        if expression[index] == '-':
            # Number of minuses and total number of signs encountered before token
            minus_counter += 1
            sign_counter += 1
        elif expression[index] == '+':
            sign_counter += 1
        elif sign_counter != 0:
            # Cut unnecessary signs from expression, leaving only one sign to later be edited ('--+-' -> '-')
            expression = expression[:index - sign_counter + 1] + expression[index:]
            index -= sign_counter
            if minus_counter % 2 == 0:  # if number of minuses is even, replace remaining sign with plus
                expression[index] = '+'
            else:  # Remaining sign could be +, so replace it with '-'
                expression[index] = '-'
            # If there is an arithmetical operation, comma or a bracket before minus, change it to unary
            if not index or expression[index-1] in ARITHMETICAL_OPERATIONS or \
                    expression[index-1] == '(' or expression[index-1] == ',':
                if expression[index] == '-':
                    expression[index] = '-u'
                else:  # If expression[index] is not minus, than it is an unnecessary plus, e.g. in pow(+1, +2^+2)
                    del expression[index]
            sign_counter = 0
            minus_counter = 0
        index += 1
    return expression


def expression_to_rpn(expression: list) -> list:
    """ Convert infix to reverse polish (postfix) notation using shunting-yard algorithm """
    result_stack = []
    operator_stack = []

    for index, token in enumerate(expression):
        try:  # Check if token is number by attempting to convert it and append to result
            result_stack.append(float(token))
            continue
        except (OverflowError, ValueError):
            pass

        if token in ARITHMETICAL_OPERATIONS:
            while operator_stack:
                if (token in RIGHT_ASSOCIATIVE and not PRECEDENCE[operator_stack[-1]] > PRECEDENCE[token]) or\
                        not PRECEDENCE[operator_stack[-1]] >= PRECEDENCE[token]:
                    break
                else:
                    result_stack.append(operator_stack.pop())
            operator_stack.append(token)
        elif token in COMPARISON_OPERATIONS:
            while operator_stack and operator_stack[-1] != '(' and operator_stack[-1] != ',':
                result_stack.append(operator_stack.pop())
            operator_stack.append(token)
        elif token in MODULE_CONSTANTS:
            result_stack.append(MODULE_CONSTANTS[token])
        elif token in MODULE_FUNCTIONS:
            if expression[index+1] != '(':
                raise Exception("ERROR: no opening bracket after function")
            else:
                # Functions are stored in lists, first element - function name, second - number of arguments
                operator_stack.append([token, 1])  # by default number of arguments equals 1
        elif token == '(':
            operator_stack.append(token)
            continue
        elif token == ')':
            while operator_stack and operator_stack[-1] != '(':
                result_stack.append(operator_stack.pop())
            if not operator_stack:
                raise Exception("ERROR: incorrect brackets")
            operator_stack.pop()
            if operator_stack and isinstance(operator_stack[-1], list):  # check if there is a function before ')'
                result_stack.append(operator_stack.pop())
        elif token == ',':
            # If token is comma, find the last function in operator stack and increase number of its arguments by 1
            while operator_stack and operator_stack[-1] != '(':
                result_stack.append(operator_stack.pop())
            last_function_index = -1
            while operator_stack and not isinstance(operator_stack[last_function_index], list):
                last_function_index -= 1
            operator_stack[last_function_index][1] += 1
        else:
            raise Exception("ERROR: unknown operation", token)

    result_stack.extend(reversed(operator_stack))
    return result_stack


def calculate_rpn_expression(rpn_expression: list) -> (float, bool, int):
    """ Calculate an expression in reverse polish notation """
    index = 0
    while len(rpn_expression) > 1:
        if isinstance(rpn_expression[index], list):  # process functions
            try:
                # Add arguments to list and pass them to function
                operation = MODULE_FUNCTIONS[rpn_expression[index][0]]
                number_of_arguments = rpn_expression[index][1]
                argument_index = number_of_arguments
                function_arguments = []
                while argument_index > 0:
                    function_arguments.append(rpn_expression[index - argument_index])
                    argument_index -= 1
                result_of_operation = operation(*function_arguments)
                # Remove function arguments from stack and put result in their place
                rpn_expression = rpn_expression[:index - number_of_arguments] + [result_of_operation] \
                    + rpn_expression[index+1:]
                index -= number_of_arguments
            except Exception:
                raise Exception('Incorrect arguments for function')
        elif rpn_expression[index] == '-u':  # process unary minuses
            try:
                rpn_expression[index-1] = -rpn_expression[index-1]
                del rpn_expression[index]
                index -= 1
            except Exception:
                raise Exception('Unary operation failure')
        elif rpn_expression[index] in ARITHMETICAL_OPERATIONS or rpn_expression[index] in COMPARISON_OPERATIONS:
            # Find operation corresponding to token and apply it to operands, then cut it and operands from stack
            try:
                if rpn_expression[index] in ARITHMETICAL_OPERATIONS:
                    operation = ARITHMETICAL_OPERATIONS[rpn_expression[index]]
                else:
                    operation = COMPARISON_OPERATIONS[rpn_expression[index]]
                operation_arguments = (rpn_expression[index-2], rpn_expression[index-1])
                result_of_operation = operation(*operation_arguments)
                rpn_expression = rpn_expression[:index-2] + [result_of_operation] + rpn_expression[index+1:]
                index -= 2  # Two operands and operation are replaced with result, so index is decreased by 2
            except Exception:
                raise Exception('Incorrect operands for operation')
        else:
            index += 1

    if not isinstance(rpn_expression[0], (float, bool, int)):
        raise Exception('Incorrect expression')
    return rpn_expression.pop()


def calculate(string_from_command_line: str):
    list_expression = parse_expression(string_from_command_line)
    list_expression = process_negative_numbers(list_expression)
    return calculate_rpn_expression(expression_to_rpn(list_expression))


def main():
    try:
        parser = argparse.ArgumentParser(description='Pure-python command line calculator')
        parser.add_argument("EXPRESSION", type=str, help="expression to be processed")
        args = parser.parse_args()
        string_from_command_line = args.EXPRESSION
        print(calculate(string_from_command_line))
    except Exception as e:
        print('ERROR: {}'.format(e))


if __name__ == '__main__':
    main()