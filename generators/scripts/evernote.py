#! /usr/bin/env python3

import xml.etree.ElementTree as ET
import sys
import argparse
import urllib.parse


#https://gist.github.com/xiaoganghan/3186646
#http://www.hanxiaogang.com/writing/parsing-evernote-export-file-enex-using-python/
def parse_enex(xmlFile):
    tree = ET.parse(xmlFile)
    root = tree.getroot()
    notes = []
    for note in root:
        note_dict = {}
        for elem in note:
            if (elem.tag == 'content'):
                note_dict[elem.tag] = urllib.parse.quote_plus(parse_content(elem.text))
            if (elem.tag == 'title' or elem.tag == 'created' or elem.tag == 'updated'):
                note_dict[elem.tag] = elem.text
        notes.append(note_dict)
    return notes

def parse_content(note):
    root = ET.fromstring(note)
    content = ""
    for elem in root:
        if elem.text != None:
            content = content + "\n" + elem.text
    return content


parser = argparse.ArgumentParser("extract notes from ENEX as json-ish")
parser.add_argument("input_file")
parser.add_argument("output_dir")
if __name__ == '__main__':
    args = parser.parse_args()
    print(f"input: {args.input_file}")
    print(f"output: {args.output_dir}")
    notes = parse_enex(args.input_file)
    print(len(notes))
    output_name = args.input_file.split("/")[-1].split(".")[0]
    print(output_name)
    itemMapping = lambda item: f"\"{item[0]}\":\"{item[1]}\"" # item -> field
    noteMapping = lambda note: "{" + ','.join(map(itemMapping, note.items())) + "}" # note -> {items}
    json = "[" + ','.join(map(noteMapping, notes)) + "]" # notes -> [note] 
    with open(args.output_dir + output_name, "w") as f:
        f.write(json)
