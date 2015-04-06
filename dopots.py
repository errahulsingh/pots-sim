#!/usr/bin/env python
from __future__ import absolute_import, division, print_function

import sys
import argparse

import potsim

def main():
    parser = argparse.ArgumentParser(description='Run an audio file through '
        'a simulated POTS line')

    parser.add_argument('infile', type=str,
        help='Input file.  Type inferred from extension.')
    parser.add_argument('-o', '--outtype', choices=['wav', 'txt'],
        help='Override output type')
    parser.add_argument('-r', '--seed', type=int,
        help='Fixed random seed if provided; integer')
    parser.add_argument('-s', '--snr', type=float, default=30,
        help='Approximate signal to noise radio in dB; float. Default: 30')

    args = parser.parse_args()

    try:
        pfilt = potsim.POTSFilter(filename=args.infile)
    except TypeError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    pfilt.process(seed=args.seed, snr=args.snr)

    if args.outtype:
        pfilt.dtype = args.outtype

    with open(pfilt.suggested_name(), 'wb') as outstream:
        pfilt.dump(outstream)

if __name__ == '__main__':
    sys.exit(main())
