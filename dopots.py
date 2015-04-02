#!/usr/bin/env python
from __future__ import absolute_import, division, print_function

import sys
import argparse
import shutil

import aio
import filters

def main():
    parser = argparse.ArgumentParser(description='thing.')

    parser.add_argument('infile')

    args = parser.parse_args()

    filename = args.infile
    fext = filename.split('.')[-1]

    try:
        with open(filename, 'rb') as f:
            data = aio.load(f, ext=fext)
    except ValueError as e:
        print(str(e), file=sys.stderr)

    data = filters.pots(data)
    buf, mimetype = aio.dump(data, ext=fext)


    parts = filename.split('.')
    parts.insert(-1, 'pots-filtered')
    newname = '.'.join(parts)

    with open(newname, 'wb') as f:
        shutil.copyfileobj(buf, f)

if __name__ == '__main__':
    sys.exit(main())
