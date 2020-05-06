# Retrofitting for Wikipedia Categories

This code can extract category links between titles in the xml formatted wikipedia dump file and retrofit word vectors based on these links.
This code is build on the original code [mfaruqui/retrofitting](https://github.com/mfaruqui/retrofitting) of Faruqui et al., 2015 in NAACL-HLT.

This tool is used to post-process word vectors to incorporate
knowledge from semantic lexicons. As shown in Faruqui et al, 2015
these word vectors are generally better in performance on semantic
tasks than the original word vectors. This tool can be used for
word vectors obtained from any vector training model.

Note that different to the original implementation, words are not lowercased in `retrofit.py`.

## Requirements

1. Python 3

## Data you need
1. Word vector file
2. Wikipedia dump file (example: jawiki-20191201-pages-articles.xml.bz2)

Each vector file should have one word vector per line as follows (space delimited):-

```the -1.0 2.4 -0.3 ...```

## Running the program

You can get a lexicon file throught the command:
```
python extract_wp_category_links.py --input_path articles.xml.bz2 --vector_path word_vec_file --output_path lexicon_file
```
You can retrofit word vectors through the command:
```
python retrofit.py -i word_vec_file -l lexicon_file -n num_iter -n 10 -o out_vec_file
```
where, 'n' is an integer which specifies the number of iterations for which the
optimization is to be performed.

## Output
File: ```out_vec.txt```
