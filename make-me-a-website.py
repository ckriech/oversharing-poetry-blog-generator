#! /usr/bin/env python3

from generators import oisincli 

import chevron
import argparse
import os, shutil

parser = argparse.ArgumentParser("Generate a blog that you wrote (basically)")

parser.add_argument("--input", default="input/", help="The folder that contains the source material. The essence of the blog, if you will. Default location is 'input/")
parser.add_argument("blogtitle", help="The title of blog. Leave empty to have one chosen for you")
parser.add_argument("theme", choices=['deepBlue', 'dustyTome', 'fingerlessGloves', 'hikingShoes', 'nude', 'purplePaper', 'springSweetheart', 'weatherbeaten', 'y2k'], help="A zonelet theme that best fits your creative mood. Leave blank to have this choice made for you.")
parser.add_argument("--author", help="The name of the website author. Probably you, leave empty to keep it mysterious (anonymous)")

def generate_poetry(sources):
    poems=[]
    for source in sources:
        tokens = oisincli.get_tokens(source, None)
        meter = oisincli.choose_meter('sonnet', None, None)
        results = oisincli.make_poem(True, tokens, meter, 3, False, 250, True)

        treatment = lambda frag: '<p>' + '<br>'.join(frag.split('\n')) + '</p>'
        content=""
        for section in results:
            content = content + treatment(section)
        poems+= { 'title':'temp title', 'text': content }
    return poems

# from https://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth/31039095
# .......ish
def copyTemplate(data, src, dst):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copyTemplate(data, s, d)
        else:
            if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                sourcename = os.path.basename(s)
                if sourcename.split('.')[:-1] == 'mo':
                    with open(s, 'r') as sf:
                        filled_in_template = chevron.render(sf, data)
                    with open(d, 'w') as df:
                        df.write(filled_in_template)
                elif not sourcename == 'temp':
                    shutil.copy2(s, d)

if __name__ == "__main__":
    args = parser.parse_args()

    # sources = os.listdir(args.input)
    # poems = generate_poetry(sources)
    
    poems = [{'title':'temp title', 'text':'hello I am text whoooooo'}]
    data = {
        'blog_title':args.blogtitle,
        'poems': poems #the files for posts will be generated later
        #, 'author':args.author
    }

    copyTemplate(data, 'generators/templates/zonelet-template', 'generated-files/oh-no-what-am-I-doing')

    print("Website made! All done")



# For now, cli. Steps involved:
# 1. Collect or generate:
#   a. Blog title
#   b. Zonelet theme
#   c. Author name (optional)
#   d. Poems (see step 2)
# 2. Create poetry:
#   a. Create poems using content from input/
#   b. will start very simply and can be made more complicated and random later
#   c. For each file in input/
#       1. create a ballad with a random meter type
#       2. Generate a title
#       3. Get a date from somewhere
# 3. Put website together:
#   a. assemble json:
#   b. blog title, zonelet theme, [poems (content, title, date)]
#   c. Use mustache to assemble into working website
#       1. Copy over basic details
#       2. copy correct background image and style
#       3. create posts with array of poems
#       4. add titles to script.js so they are listed on the front page
#   e. Put everything in generated-files/blog-title