import argparse
import gzip
import codecs
import math
import numpy
import re
import sys

from copy import deepcopy

isNumber = re.compile(r'\d+.*')
def norm_word(word):
  if isNumber.search(word):
    return '---num---'
  elif re.sub(r'\W+', '', word) == '':
    return '---punc---'
  else:
    return word

''' Read all the word vectors and normalize them '''
def read_word_vecs(filename):
  wordVectors = {}
  if filename.endswith('.gz'):
      gzObject = gzip.open(filename, mode="rb")
      reader = codecs.getreader("utf8")
      fileObject = reader(gzObject, errors="ignore")
  else:
      fileObject = codecs.open(filename, mode='r', encoding="utf8", errors="ignore")
  
  is_start = True
  for line in fileObject:
    line = line.rstrip()
    # for the word2vec format
    if len(line.split(" ")) == 2 and is_start:
        is_start = False
        continue
    word = line.split(" ")[0]
    if word == "":
        continue
    wordVectors[word] = numpy.zeros(len(line.split(" "))-1, dtype=float)
    for index, vecVal in enumerate(line.split(" ")[1:]):
      wordVectors[word][index] = float(vecVal)
    ''' normalize weight vector '''
    wordVectors[word] /= math.sqrt((wordVectors[word]**2).sum() + 1e-6)
    
  sys.stderr.write("Vectors read from: "+filename+" \n")
  return wordVectors

''' Write word vectors to file '''
def print_word_vecs(wordVectors, outFileName):
  sys.stderr.write('\nWriting down the vectors in '+outFileName+'\n')
  outFile = codecs.open(outFileName, mode="w", encoding="utf8", errors="ignore")  
  for word, values in wordVectors.items():
    outFile.write(word+' ')
    for val in wordVectors[word]:
      outFile.write('%.4f' %(val)+' ')
    outFile.write('\n')      
  outFile.close()

''' Read Wikipedia categories '''
def read_lexicon(filename, wordVecs):
  categories = []
  word2category = {}
  with codecs.open(filename, mode="r", encoding="utf8", errors="ignore") as f_in:
    for line in f_in:
      line = line.strip()
      words = [word for word in line.rstrip().split() if word in wordVecs]
      if len(words) < 2:
          continue
      categories.append(words)
      for word in words:
        if word not in word2category:
          word2category[word] = []
        word2category[word].append(len(categories) - 1)
  return categories, word2category
  
''' Retrofit word vectors to a lexicon '''
def retrofit(wordVecs, filename, numIters):
  newWordVecs = deepcopy(wordVecs)
  wvVocab = set(newWordVecs.keys())
  # read Wikipedia categories
  categories, word2category = read_lexicon(filename, wordVecs)
  for it in range(numIters):
    # loop through every node also in ontology (else just use data estimate)
    for word in word2category.keys():
      print(word)
      wordNeighbours = set()
      for cid in word2category[word]:
        for neighbour in categories[cid]:
          if neighbour == word:
            continue
          wordNeighbours.add(neighbour)
      numNeighbours = len(wordNeighbours)
      # the weight of the data estimate if the number of neighbours
      newVec = numNeighbours * wordVecs[word]
      # loop over neighbours and add to new vector (currently with weight 1)
      for ppWord in wordNeighbours:
        newVec += newWordVecs[ppWord]
      newWordVecs[word] = newVec/(2*numNeighbours)
  return newWordVecs

if __name__=='__main__':

  parser = argparse.ArgumentParser()
  parser.add_argument("-i", "--input", type=str, default=None, help="Input word vecs")
  parser.add_argument("-l", "--lexicon", type=str, default=None, help="Lexicon file name")
  parser.add_argument("-o", "--output", type=str, help="Output word vecs")
  parser.add_argument("-n", "--numiter", type=int, default=10, help="Num iterations")
  args = parser.parse_args()

  wordVecs = read_word_vecs(args.input)
  numIter = int(args.numiter)
  outFileName = args.output
  
  ''' Enrich the word vectors using ppdb and print the enriched vectors '''
  print_word_vecs(retrofit(wordVecs, args.lexicon, numIter), outFileName) 
