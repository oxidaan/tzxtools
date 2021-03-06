#!/usr/bin/env python3
#
# tzxtools - a collection for processing tzx files
#
# Copyright (C) 2016 Richard "Shred" Körber
#   https://github.com/shred/tzxtools
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import argparse
import io
import sys
import textwrap

from tzxlib.tapfile import TapHeader, TapFile
from tzxlib.tzxfile import TzxFile

def main():
    parser = argparse.ArgumentParser(description='List the contents of a TZX file')
    parser.add_argument('file',
                nargs=argparse.REMAINDER,
                type=argparse.FileType('rb'),
                help='TZX files, stdin if omitted')
    parser.add_argument('-s', '--short',
                dest='short',
                action='store_true',
                help='list only the ZX Spectrum header names')
    parser.add_argument('-v', '--verbose',
                dest='verbose',
                action='store_true',
                help='show content of information blocks')
    parser.add_argument('-w', '--wide',
                dest='printwide',
                action='store_true',
                help='output horizontal, comma separated')
    parser.add_argument('-X', '--hexdump',
                dest='hexdump',
                action='store_true',
                help='Show 16 byte sample hexdump after block data')
    args = parser.parse_args()
    TapFile.showHexSample = args.hexdump

    files = list(args.file)
    if not sys.stdin.isatty() and len(files) == 0:
        files.append(sys.stdin.buffer)

    if len(files) == 0:
        parser.print_help(sys.stderr)
        sys.exit(1)

    for f in files:
        if len(files) > 1:
            name = f.name if hasattr(f, 'name') else f
            print('\n%s:' % (name))
        tzx = TzxFile()
        tzx.read(f)

        cnt = 0
        sep = ""     # endmarker either \n or ,
        for b in tzx.blocks:
            if args.short:
                if hasattr(b, 'tap') and isinstance(b.tap, TapHeader):
                    print('%s%s: %s (%s)' % (sep, b.tap.type(), b.tap.name().strip(), b.tap.length() ), end="")
            else:
                print('%s%3d  %-27s %s' % (sep, cnt, b.type, str(b)), end="")
            if args.verbose:
                info = b.info()
                if info is not None:
                    print(textwrap.indent(info.strip(), '\t'), end="")
            cnt += 1
            if args.printwide:
                sep = ", "
            else: 
                sep = "\n"     # endmarker either \n or ,
        print("")              # extra \n