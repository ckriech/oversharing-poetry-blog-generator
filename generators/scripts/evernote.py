#! /usr/bin/env python3

import xml.etree.ElementTree as ET
import sys

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
                print('content!')
                note_dict[elem.tag] = parse_content(elem.text)
            if (elem.tag == 'title' or elem.tag == 'created' or elem.tag == 'updated'):
                print('title or whatever!')
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


#Script assumes the given file name is located input/ at the root of the project
if __name__ == '__main__':
    input_path = "../../input"

    file = sys.argv[1]
    notes = parse_enex(input_path + file)
    print(len(notes))
    output_name = input_path + file.split(".")[0]
    with open(output_name, "w") as f:
        for note in notes:
            #f.write(note['title'] + '\n')
            f.write(note['content'])
            #f.write('\n')
