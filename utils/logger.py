import pprint

pp = pprint.PrettyPrinter(indent=4)

def pprint_objects(*arg):
    '''
    Print large and indented objects clearly.

    Args:
        *arg: Variable number of arguments to print.
    '''
    pp.pprint(arg)