import argparse


def get_args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r',
                        '--restart',
                        choices=['yes', 'no', 'ask'],
                        default='ask',
                        help='set restart parametr')
    return parser
