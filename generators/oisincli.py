#! /usr/bin/env python3

import argparse
import os
import sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

import oisin

parser = argparse.ArgumentParser("Generate poem with oisin")

parser.add_argument("--outputfile", "-of", type=str)
parser.add_argument('--template', type=bool, default=False)
parser.add_argument('--meter', '-m', type=str, choices=['sonnet', 'petrarch', 'ottava', 'limerick', 'couplet', 'ballad', 'verse', 'blank'])
parser.add_argument('--beats', '-b', type=int, default=5)
parser.add_argument('--rhyme', '-rs', type=str, default='aabbccdd')
parser.add_argument('--balladize', type=bool, default=False)
parser.add_argument('--step', '-s', type=int, default=50)
parser.add_argument('--order', '-o', type=int, default=3)
parser.add_argument('--refrain', '-r', type=bool, default=False)
parser.add_argument('--verbose', '-v', type=bool, default=True)
parser.add_argument('--tokenlimit', '-t', type=int)
parser.add_argument('inputfile', type=str)

meter_dict={'sonnet': oisin.sonnet, 'petrarch': oisin.petrarch, 'ottava': oisin.ottava, 'limerick': oisin.limerick, 'couplet': oisin.couplet, 'ballad': oisin.ballad, 'verse': oisin.verse, 'blank': oisin.blank}

# required, optional
def get_tokens_from_file(inputfile, tokenlimit):
    tokens = oisin.load(inputfile)
    if (tokenlimit != None):
        tokens = tokens[:tokenlimit]
    return tokens

def get_tokens(content, tokenlimit):
    tokens = oisin.corpus.tokenize(content)
    if (tokenlimit != None):
        tokens = tokens[:tokenlimit]
    return tokens

# optional, optional, optional
# (either chosen_meter OR beats + rhyme need to be present)
def choose_meter(chosen_meter, beats, rhyme):
    if (chosen_meter == None):
        meter = oisin.iambic(beats, rhyme)
    else:
        meter = meter_dict[chosen_meter]
    return meter

# required, required, required, optional*, optional*, required, required 
# *required if balladize == true
def make_poem(balladize, tokens, meter, step, refrain, order, verbose):
    if (balladize):
        results = oisin.balladize(tokens, meter, step, refrain, order, verbose)
    else:
        results = oisin.stepthrough(tokens, meter, order, verbose)
    return results

# required, required, required
def write_file(results, template, outputfile):
    treatment = lambda frag: frag + '\n\n'
    #not real html tbh, used with template generator
    if (template):            
        treatment = lambda frag: '<p>' + '<br>'.join(frag.split('\n')) + '</p>'
        content=""
        for section in results:
            content = content + treatment(section)
        with open(outputfile, "w") as f:
            f.write('export CONTENT="'+ content + '"\n' +
                    'export TITLE="My Drac Poem!"')
    else:
        with open(outputfile, "w") as f:
            for section in results:
                f.write(treatment(section))

if __name__ == "__main__":
    args = parser.parse_args()

    tokens = get_tokens(args.inputfile, args.tokenlimit)
    meter = choose_meter(args.meter, args.beats, args.rhyme)
    results = make_poem(args.balladize, tokens, meter, args.step, args.refrain, args.order, args.verbose)
    write_file(results, args.template, args.outputfile)
