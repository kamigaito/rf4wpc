"""
Generate wikipedia cateogory links between words in the given word vector.
The output format is following https://github.com/mfaruqui/retrofitting.
"""

import sys
import argparse
import bz2
import codecs
import xml.etree.ElementTree as ET
import re

def options():
    # Option list
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", type=str, help="Input path of bz2 compressed wikipedia dump that includes articles. Example: jawiki-YYYYMMDD-pages-articles.xml.bz2")
    parser.add_argument("--output_path", type=str, help="Output path of the generated lexicon.")
    parser.add_argument("--vector_path", type=str, help="Path to the word vector file. This file should follow the word2vec format. ")
    parser.add_argument("--include_multi_sense", action='store_true', help="Include a word which has multiple senses. (I identify them based on the exsistence of the brackets in the words)")
    args = parser.parse_args()
    return args

def get_page(wiki_file):
    '''
    extract subtree from <page> to </page>
    '''
    page_lines = []
    page_started, page_ended = False, False
    
    # gathering lines in the subtree
    while not page_started:
        line = wiki_file.readline().rstrip()
        if line == "":
            return False
        if line.find("<page>") != -1:
            page_started = True
            line = line.rstrip()
            page_lines.append(line)
    # post process
    while not page_ended:
        line = wiki_file.readline()
        if line.find('</page>') != -1:
            page_ended = True
        line = line.rstrip()
        page_lines.append(line)

    return '\n'.join(page_lines)

def extract_vocabulary(opts):
    vocab = {}
    with codecs.open(opts.vector_path, mode="r", encoding="utf8", errors="ignore") as f_vec:
        is_first = True
        for line in f_vec:
            line = line.rstrip()
            cols = line.split(" ")
            # for the word2vec format
            if len(cols) == 2 and is_first:
                is_first = False
                continue
            # for checking the format of this line
            vector = [ float(col) for col in cols[1:] ]
            # add the token to the vocabulary
            vocab[cols[0]] = True
    return vocab

def extract_categories(opts):
    # open bz2 formattted file
    vocab = extract_vocabulary(opts)
    bz2_file = bz2.open(opts.input_path,"rb")
    reader = codecs.getreader(encoding="utf8")
    wiki_file = reader(bz2_file, errors="ignore")
    # wiki_file = bz2.open(opts.input_path,"rt")
    categories = {}
    while True:
        # each page
        page_str = get_page(wiki_file)
        if not page_str:
            break

        # parse the tree (XML)
        root = ET.fromstring(page_str)

        # article title
        title = root.find('title').text
        # skip functional titles
        if ":" in title:
            continue
        # skip ambiguos words
        if opts.include_multi_sense == False and ("(" in title or ")" in title):
            continue
        if title not in vocab:
            continue
        # article body
        body = root.find('./revision/text', {'xml:space': 'preserve'}).text
        pattern = re.compile(u'\[\[[Cc]ategory:([^\[\]]+)\]\]', re.MULTILINE | re.DOTALL)
        for match in pattern.finditer(body):
            category = match.group(1)
            if category not in categories:
                categories[category] = []
            categories[category].append(title)
    return categories

def output_lexicon(opts, categories):
    with codecs.open(opts.output_path, mode="w", encoding="utf8") as f_lex:
        for category, titles in categories.items():
            if  len(titles) > 1:
                f_lex.write(" ".join(titles) + "\n")

def main():
    # Options
    opts = options()
    # Titles for each category
    categories = extract_categories(opts)
    # Output
    output_lexicon(opts, categories)

if __name__ == '__main__':
    main()
