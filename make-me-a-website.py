#! /usr/bin/env python3

from generators import oisincli 

import chevron
import argparse
import os, shutil
import sys
import json
import xml.etree.ElementTree as ET
import urllib.parse

###### Input parsing

##### level 0 - start
def start_input_parsing(input_path):
    print("input parsing: ###### START ######\n")
    results = parse_input_path(input_path)
    return results

##### level 1 - files and folders
def parse_input_path(input_path):
    print(f"input parsing: PATH: {input_path}")
    if os.path.isdir(input_path):
        return parse_input_folder(input_path)
    else:
        return parse_input_file(input_path)
        
def parse_input_folder(input_dir):
    print(f"input parsing: FOLDER: ${input_dir}")
    return start_recurse(map(parse_input_path, os.listdir(input_dir)))

def parse_input_file(input_file):
    print(f"input parsing: FILE: ${input_file}")
    with open(input_file, "r") as f:
        content = f.read()
    if is_enex(input_file):
        return parse_enex(content)
    elif is_json(content):
        return parse_json(content)
    else: #assume the contents are 'contents' and the file name is the 'name'
        return start_recurse({ 'name':os.path.basename(input_file), 'content': content })

##### level 2 - file content

### json
def is_json(myjson):
  try:
    json.loads(myjson)
  except ValueError as e:
    return False
  return True

def parse_json(json_string):
    print(f"input parsing: CONTENTS -- JSON: ${json_string[1:100]}")
    return start_recurse(json.load(json_string))

### .enex
def is_enex(file_name):
    whatisthis = file_name.split(".")[-1].lower()
    print(f"WHAT IS THIS {whatisthis}")
    return file_name.split(".")[-1].lower() == "enex"

#https://gist.github.com/xiaoganghan/3186646
#http://www.hanxiaogang.com/writing/parsing-evernote-export-file-enex-using-python/
def parse_enex(xml):
    print(f"input parsing: CONTENTS -- ENEX: ${xml[1:100]}")
    root = ET.fromstring(xml)
    notes = []
    for note in root:
        note_dict = {}
        for elem in note:
            if elem.tag == 'content':
                note_dict['content'] = parse_enex_content(elem.text)
            if elem.tag == 'title':
                note_dict['name'] = elem.text
            if elem.tag == 'created' or elem.tag == 'updated':
                note_dict[elem.tag] = elem.text
        notes.append(note_dict)
    return start_recurse(notes)

def parse_enex_content(note):
    root = ET.fromstring(note)
    content = ""
    for elem in root:
        if elem.text != None:
            content = content + "\n" + elem.text
    return content

##### level 3 - python classes/types

def start_recurse(parsed):
    print(f"input parsing: DATA -- START")
    recursed = recurse(parsed)
    print(f"input parsing: DATA -- END len={len(recursed)}")
    print(f"input parsing: DATA -- END recursed={type(recursed).__name__}")
    # print(recursed[0])
    # filtered = [filter(lambda item: item != None, recursed)]
    filtered=[]
    for r in recursed:
        if r != None:
            filtered+=[r]
    print(f"input parsing: DATA -- FILTERED len={len(filtered)}")
    squashed = manipulate_input(filtered)
    print(f"input parsing: DATA -- SQUASHED len={len(squashed)}")
    return squashed

def recurse(parsed):
    if isinstance(parsed, list):
        print(f"input parsing: DATA -- LIST LEN={len(parsed)}")
        mapped = [map(lambda item: recurse(item), parsed)]
        print(f"input parsing: DATA -- MAPPED LEN={len(mapped)}")
        # https://stackoverflow.com/questions/952914/how-to-make-a-flat-list-out-of-list-of-lists
        flatten = [item for sublist in mapped for item in sublist]
        flatten = [item for sublist in flatten for item in sublist]
        print(f"input parsing: DATA -- FLATTEN LEN={len(flatten)}")
        return flatten
    if isinstance(parsed, dict):
        print(f"input parsing: DATA -- DICT")
        if not 'content' in parsed or parsed['content'] == "":
            print(f"input parsing: DATA -- DICT ##### NO CONTENT")
            return [None]
        else:
            #parsed['content'] = treat_content_string(parsed['content'])
            return [parsed]
    elif isinstance(parsed, str):
        print(f"input parsing: DATA -- STR {parsed[1:100]}")
        #this shouldn't be possible with current flow but who knows
        recurse({ 'content': parsed })
    else:
        print(f"input parsing: I don't know what to do with this {parsed[1:100]}")
        return [None]

def treat_content_string(content):
    return urllib.parse.quote(content)

### level 4 - manipulating the input for more randomness and to work better with Oisin

# Ideas:
#  - combine short entries into one long one

# arbitrary squash threshold
squash_threshold = 5000
def manipulate_input(input):
    #squash
    currentCount = 0
    squashed = []
    to_be_squashed = []
    for i in input:
        count=len(i['content'])
        print(count)
        currentCount+=len(i['content'])
        print('cc=' + str(currentCount))
        if currentCount < 5000:
            print('no squash (yet)')
            to_be_squashed+=[i]
        else:
            print('squash!')
            squashed+=[squash_dicts(to_be_squashed)]
            currentCount = 0
    if len(to_be_squashed) > 0:
        print('squash! (end)')
        squashed+=[squash_dicts(to_be_squashed)]
    return squashed

def squash_dicts(input):
    return {
        'content': "\n".join(map(lambda i: i['content'], input)),
        'name': input[0]['name']
    }
### Generating the actual website

def generate_poetry(sources):
    poems=[]
    print("Generating poetry..... (this step takes awhile)")
    for source in sources:
        print(f"SOURCE len={len(source['content'])}")
        tokens = oisincli.get_tokens(source['content'], None)
        print(f"TOKENS len={len(tokens)}")
        meter = oisincli.choose_meter('limerick', None, None)
        results = oisincli.make_poem(True, tokens, meter, 3, False, 10, True)
        print(results)
        treatment = lambda frag: '<p>' + '<br>'.join(frag.split('\n')) + '</p>'
        content=""
        for section in results:
            content = content + treatment(section)
        print(content)
        poems+= [{'title':source['name'], 'text': content }]
    print(f"poem type={type(poems[0]).__name__}")
    return poems

image_dict = {
    "deepBlue": "bg_deepBlue.jpg",
    "diamonds": "bg_diamonds.png",
    "dustyTome": "bg_dustyTome.jpg",
    "fingerlessGloves": "bg_fingerlessGloves.png",
    "hikingShoes": "bg_hikingShoes.png",
    "purplePaper": "bg_purplePaper.png",
    "springSweetheart": "bg_springSweetheart.jpg",
    "weatherbeaten": "bg_weatherbeaten.gif",
    "y2k": "bg_y2k.png"
}
def copy_style(theme_name, dst):
    source = "generators/templates/zonelet-themepack"

    style = source + "/style/" + theme_name + ".css"
    shutil.copy2(style, dst + "/style/style.css")

    image = "/images/" + image_dict[theme_name]
    shutil.copy2(source + image, dst + image)

def assemble_posts(poems, dst):
    with open("generators/templates/zonelet-post-template.mo", 'r') as f:
        template = f.read()
    for poem in poems:
        print(f"type of poem={type(poem).__name__}")
        title = "/posts/" + poem['title_lower_hyphenated'] + ".html"
        with open(dst + title, "w") as f:
            f.write(chevron.render(template, poem))
        
# from https://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth/31039095
# .......ish
def copy_template(data, src, dst):
    #make dst if if doesn't exist
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copy_template(data, s, d)
        else:
            sourcename = os.path.basename(s)
            print("sourcename=" + sourcename)
            #always process and copy over .mo files
            if sourcename.split('.')[-1] == 'mo':
                print("mo found!")
                with open(s, 'r') as sf:
                    filled_in_template = chevron.render(sf, data)
                actual_d=os.path.join(os.path.dirname(d), '.'.join(os.path.basename(d).split('.')[:-1]))
                with open(actual_d, 'w') as df:
                    df.write(filled_in_template)
            else:
                #hypothetically this means copy file if d doesn't exist or is different than s
                if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                    #split into second if for brevity
                    if sourcename != 'temp':
                        shutil.copy2(s, d)



################################################################################################


parser = argparse.ArgumentParser("Generate a blog that you wrote (basically)")

parser.add_argument("--input", default="input/", help="A folder or file that represents the input. File can by anything, but json or .enex will get parsed correctly")
parser.add_argument("blogtitle", help="The title of blog. Leave empty to have one chosen for you")
parser.add_argument("theme", choices=['deepBlue', 'dustyTome', 'fingerlessGloves', 'hikingShoes', 'nude', 'purplePaper', 'springSweetheart', 'weatherbeaten', 'y2k'], help="A zonelet theme that best fits your creative mood. Leave blank to have this choice made for you.")
parser.add_argument("--author", help="The name of the website author. Probably you, leave empty to keep it mysterious (anonymous)")
#todo: add arg for cleaning up generated files beforehand

def clean_up_dicts(results):
    return map(clean_up_dict, results)

def clean_up_dict(d):
    if not 'title' in d:
        d['title'] = 'FILL IN TITLE'
    d['title_lower_hyphenated'] = "-".join(d['title'].lower().split(" "))
    return d

if __name__ == "__main__":
    args = parser.parse_args()

    processed_input = start_input_parsing(args.input)
    poems = generate_poetry(processed_input)
    poems = clean_up_dicts(poems)
    data = {
        'blog_title':args.blogtitle,
        'poems': poems #the files for posts will be generated next step
        #, 'author':args.author
    }
    dst = f'generated-files/{args.blogtitle}'
    copy_template(data, 'generators/templates/zonelet-template', dst)
    copy_style(args.theme, dst)
    assemble_posts(poems, dst)

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