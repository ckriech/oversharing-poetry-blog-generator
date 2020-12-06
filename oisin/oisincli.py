#! /usr/bin/env python3

# ballad.py:
# import sys
# import oisin
# if __name__ == "__main__":
#     filename = "input/alices.txt"
#     try:
#         filename = sys.argv[1]
#     except IndexError:
#         pass
#     oisin.balladize(
#         oisin.load(filename),
#         meter=oisin.iambic(4, 'aabbccdd'),
#         step=50,
#         order=3)

# makegif.py:
# import sys
# import oisin

# filename = "input/alices.txt"
# nlines = 100
# output = "output/test.gif"
# try:
#     filename = sys.argv[1]
#     nlines = int(sys.argv[2])
#     output = sys.argv[3]
# except IndexError:
#     pass

# oisin.animate(
#     oisin.stepthrough(
#         oisin.load(filename)[:nlines], oisin.sonnet, verbose=True), output)


import argparse

import os
import sys
import oisin

parser = argparse.ArgumentParser("Generate poem with oisin")

parser.add_argument('--meter', '-m', type=str, choices=['sonnet', 'petrarch', 'ottava', 'limerick', 'couplet', 'ballad', 'verse', 'blank'])
parser.add_argument('--beats', '-b', type=int, default=5)
parser.add_argument('--rhyme', '-rs', type=str, default='aabbccdd')
parser.add_argument('--balladize', type=bool, default=False)
parser.add_argument('--step', '-s', type=int, default=50)
parser.add_argument('--order', '-o', type=int, default=3)
parser.add_argument('--refrain', '-r', type=bool, default=False)
parser.add_argument('inputfile', type=str)

meter_dict={'sonnet': oisin.sonnet, 'petrarch': oisin.petrarch, 'ottava': oisin.ottava, 'limerick': oisin.limerick, 'couplet': oisin.couplet, 'ballad': oisin.ballad, 'verse': oisin.verse, 'blank': oisin.blank}

if __name__ == "__main__":
    args = parser.parse_args()
    chosen_meter = args.meter
    beats = args.beats
    rhyme = args.rhyme
    balladize = args.balladize
    step = args.step
    order = args.order
    refrain = args.refrain
    inputfile = args.inputfile

    tokens = oisin.load(inputfile)
    if (chosen_meter == None):
        meter = oisin.iambic(beats, rhyme)
    else:
        meter = meter_dict[chosen_meter]

    if (balladize):
        oisin.balladize(tokens, meter, step, refrain, order)
    else:
        oisin.stepthrough(tokens, meter, order)