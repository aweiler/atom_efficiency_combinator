#! /usr/bin/env python

"""
atom efficiency combinator
"""

__author__ = "A.Weiler"
__version__ = "0.1"


import logging
import yaml
import argparse 

if __name__ == "__main__":
    parser = argparse.ArgumentParser( 
                description='Atom efficiency combinator: Combines atom yaml files.')
    parser.add_argument('-f', action='append', dest='inputfileList',
                    default=[],
                    help='Add all input files. E.g. -f file1.yml -f file2.yml etc.',
                    )
    parser.add_argument("-o", "--output", dest="outfilename", default=[],
                       help="write Atom Limit output to file", metavar="EFFCOMBINATION")
    args = parser.parse_args()

    print args.inputfileList

    # logging.info('Reading Atom file <' + args.inputfile + ">...")    