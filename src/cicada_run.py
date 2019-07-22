"""
    To use to run using command line 'python cicada_run.py'
"""

"""
    The argparse module makes it easy to write user-friendly command-line interfaces. 
    The program defines what arguments it requires, and argparse will figure out how 
    to parse those out of sys.argv. 
    The argparse module also automatically generates help and usage messages and 
    issues errors when users give the program invalid arguments.
    https://docs.python.org/3.6/library/argparse.html
"""

import argparse
import os

if __name__ == '__main__':
    # Parse args
	parser = argparse.ArgumentParser(description="Run CICADA")
    args = parser.parse_args()
    parser.add_argument('--use_gui')

    # Default parameter values
    #TODO: read a yaml files with the default parameter values

    data = args.data

    # Set defaults
    if args.use_gui:
        use_gui = True
    else:
        use_gui = False

    # function to run
    # TODO: to implement
