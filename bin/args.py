import os
import argparse


def get_args():
    """
    Parse command line parameters.

    :return: Arguments with default or user specified values.
    :rtype: dict
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--scils',
                        help='Path to SCiLS .slx file.',
                        required=True,
                        type=str)
    parser.add_argument('--roi',
                        help='Name of the region of interest from the SCiLS region tree.',
                        required=True,
                        type=str)
    parser.add_argument('--label',
                        help='Name of the new Label to be written to the SCiLS file.',
                        required=True,
                        type=str)
    arguments = parser.parse_args()
    return vars(arguments)


def args_check(args):
    """
    Check relevant arguments to ensure user input values are valid.

    :param args: Arguments obtained from get_args().
    type args: dict
    """
    if not os.path.exists(args['scils']):
        raise Exception('SCiLS file does not exist.')
    if not os.path.splitext(args['scils'][1]) != 'slx':
        raise Exception('SCiLS file is not a .slx file.')
