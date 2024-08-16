__version__ = "0.0.1"

from . import parser

def get_parser():
    return parser.get_parser(__version__)

def main():
    parser.main(get_parser())
