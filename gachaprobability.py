# -*- coding: utf-8 -*-

from fractions import Fraction
from decimal import *


def can2float(str_n):
    try:
        if float(str_n):
            return True
    except Exception as e:
        return False


def str2num(str_n):
    if can2float(str_n):
        num_n = Decimal(str_n)
    elif str_n.endswith('%'):
        str_n = str_n.rstrip('%')
        num_n = Decimal(str_n) / 100
    return Decimal(num_n)


def pn(n):
    flag = 0
    border = 1
    prints = (70, 75, 80, 85, 90, 95, 99)
    count = int(n)
    p = (1 - 1/n) ** n
    print('Start: %5d  p: %f' % (count, 1-p))
    while True:
        if flag < border and 1-p >= border/100:
            if border in prints:
                print('%d> n: %5d  p: %f' % (border, count, 1-p))
            flag = border
            border += 1
        if border > 99:
            break
        p *= (1 - 1/n)
        count += 1


def main(str_n):
    print('P:', str_n)
    num_n = str2num(str_n)
    n = 1/Fraction(num_n)
    pn(n)


if __name__ == '__main__':
    str_n = '0.3%'
    main(str_n)
