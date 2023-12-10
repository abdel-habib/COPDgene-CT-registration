import sys
import pprint as pp
from loguru import logger

PPRINT = pp.PrettyPrinter(indent=4)

# Custom log format
fmt = "{message}"
config = {
    "handlers": [
        {"sink": sys.stderr, "format": fmt},
    ],
}
logger.configure(**config)

def pprint(*arg):
    '''
    Print large and indented objects clearly.

    Args:
        *arg: Variable number of arguments to print.
    '''
    PPRINT.pprint(arg)