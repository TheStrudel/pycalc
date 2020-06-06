import unittest
import math
from pycalc import parse_expression, calculate


class TestPycalc(unittest.TestCase):

    def test_parser(self):
        self.assertEqual(parse_expression('123'), ['123'])
        self.assertEqual(parse_expression('123.123 + .1'), ['123.123', '+', '.1'])
        self.assertEqual(parse_expression('--+- 1 -- 1'), ['-', '-', '+', '-', '1', '-', '-', '1'])
        self.assertEqual(parse_expression('1*2/3//4%5^6'), ['1', '*', '2', '/', '3', '//', '4', '%', '5', '^', '6'])
        self.assertEqual(parse_expression('1>2<3>=4<=5!=6==7'), ['1', '>', '2', '<', '3', '>=', '4', '<=', '5',
                                                                 '!=', '6', '==', '7'])
        self.assertEqual(parse_expression('-(1+(2*(3)^4))'), ['-', '(', '1', '+', '(', '2', '*', '(', '3', ')',
                                                              '^', '4', ')', ')'])
        self.assertEqual(parse_expression('tau - e'), ['tau', '-', 'e'])
        self.assertEqual(parse_expression('cos(hypot(1, 2))'), ['cos', '(', 'hypot', '(', '1', ',', '2', ')', ')'])
        self.assertEqual(parse_expression('-+ - abs (1+log(2^3*4.5))'), ['-', '+', '-', 'abs', '(', '1', '+', 'log',
                                                                         '(', '2', '^', '3', '*', '4.5', ')', ')'])

    def test_unary_operations(self):
        self.assertEqual(calculate('+1'), 1)
        self.assertEqual(calculate('-1'), -1)
        self.assertEqual(calculate('++1'), ++1)
        self.assertEqual(calculate('+--1'), +--1)
        self.assertEqual(calculate('-+--1'), -+--1)
        self.assertEqual(calculate('(-1)'), (-1))
        self.assertEqual(calculate('1*-2'), 1*-2)
        self.assertEqual(calculate('2^-3'), 2 ** -3)

    def test_binary_operations(self):
        self.assertEqual(calculate('1+1'), 1 + 1)
        self.assertEqual(calculate('1-2'), 1 - 2)
        self.assertEqual(calculate('2*2'), 2 * 2)
        self.assertEqual(calculate('4/5'), 4 / 5)
        self.assertEqual(calculate('5%4'), 5 % 4)
        self.assertEqual(calculate('5//4'), 5 // 4)
        self.assertEqual(calculate('2^4'), 2 ** 4)

    def test_precedence(self):
        self.assertEqual(calculate('2-3+4'), 2 - 3 + 4)
        self.assertEqual(calculate('2/3*4//5%6'), 2 / 3 * 4 // 5 % 6)
        self.assertEqual(calculate('2^3^4'), 2 ** 3 ** 4)
        self.assertEqual(calculate('2*3+4^5'), 2 * 3 + 4 ** 5)

    def test_brackets(self):
        self.assertEqual(calculate('(1)'), (1))
        self.assertEqual(calculate('2*(3+4)'), 2*(3+4))
        self.assertEqual(calculate('(2-(3-(4+5)))'), (2 - (3 - (4 + 5))))
        self.assertEqual(calculate('(((2+3)))'), (((2 + 3))))

    def test_constants(self):
        self.assertEqual(calculate('pi+tau*e'), math.pi + math.tau * math.e)
        self.assertEqual(calculate('inf'), math.inf)

    def test_functions(self):
        self.assertEqual(calculate('sin(1)'), math.sin(1))
        self.assertEqual(calculate('cos(sin(exp(3)))'), math.cos(math.sin(math.exp(3))))
        self.assertEqual(calculate('hypot(3, 4)'), math.hypot(3, 4))
        self.assertEqual(calculate('atan2(log10(123), expm1(4))'), math.atan2(math.log10(123), math.expm1(4)))

    def test_comparison(self):
        self.assertTrue(calculate('1-2*3==1-2*3'))
        self.assertTrue(calculate('2*4>1'))
        self.assertTrue(calculate('3<log(4)*4'))
        self.assertTrue(calculate('pi>=e'))
        self.assertTrue(calculate('4>=4'))
        self.assertTrue(calculate('3<=4'))
        self.assertTrue(calculate('pi<=pi'))
        self.assertTrue(calculate('4!=5-4'))
        self.assertFalse(calculate('1==2'))
        self.assertFalse(calculate('0>1'))
        self.assertFalse(calculate('5<4'))
        self.assertFalse(calculate('4>=5'))
        self.assertFalse(calculate('5<=4'))
        self.assertFalse(calculate('4!=4'))

    def test_general_expressions(self):
        self.assertEqual(calculate('.123'), .123)
        self.assertEqual(calculate('pi*(12.34+.234)'), math.pi * (12.34 + .234))
        self.assertEqual(calculate('123-2+4%5'), 123 - 2 + 4 % 5)
        self.assertEqual(calculate('(1234*34567+1)^2'), (1234 * 34567 + 1) ** 2)
        self.assertEqual(calculate('--+-(234*e/pi+(3-2)^2)'), --+-(234 * math.e / math.pi + (3 - 2) ** 2))
        self.assertEqual(calculate('pi*(12.34+.234)'), math.pi * (12.34 + .234))
        self.assertEqual(calculate('2^-5==2'), 2 ** -5 == 2)
        self.assertEqual(calculate('12.345 - 12 + 9.0'), 12.345 - 12 + 9.0)
        self.assertEqual(calculate('cos(3^2)-hypot(tau, log(12))'), math.cos(3 ** 2)-math.hypot(math.tau, math.log(12)))
        self.assertEqual(calculate('-+--23+--3.45*-e'), -+--23+--3.45 * -math.e)
        self.assertEqual(calculate('5^0-45*(3.45-(-cos(4)/3))'), 5 ** 0 - 45 * (3.45 - (-math.cos(4) / 3)))
        self.assertEqual(calculate('log(cos(round(abs(-3456))))'), math.log(math.cos(round(abs(-3456)))))

    def test_errors(self):
        self.assertRaises(Exception, calculate, '')
        self.assertRaises(Exception, calculate, '1/0')
        self.assertRaises(Exception, calculate, '     ')
        self.assertRaises(Exception, calculate, '-++--')
        self.assertRaises(Exception, calculate, 'pi.123')
        self.assertRaises(Exception, calculate, '123==')
        self.assertRaises(Exception, calculate, '123-')
        self.assertRaises(Exception, calculate, '2**3')
        self.assertRaises(Exception, calculate, '4 / / 3')
        self.assertRaises(Exception, calculate, '1+2 3')
        self.assertRaises(Exception, calculate, 'qwerty')
        self.assertRaises(Exception, calculate, 'abs()')
        self.assertRaises(Exception, calculate, 'abs 3')
        self.assertRaises(Exception, calculate, 'hypot(2, 3, 4)')
        self.assertRaises(Exception, calculate, '(123')
        self.assertRaises(Exception, calculate, '2=2')
        self.assertRaises(Exception, calculate, '1+(3*4')
