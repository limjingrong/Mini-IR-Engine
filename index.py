import collections
from decimal import Decimal
import getopt
import math
import os
import sys

import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

import xml.etree.ElementTree as ET


__author__ = 'Jing Rong, Jia Le, Nelson'


# Python script for indexing

term_to_docfreq = {}    # Dictionary to map [term.field : document frequency]
term_to_docposting = collections.defaultdict(list) # Dictionary to map [term.field : list[document posting]]
termdocname_to_termfreq = {}  # Dictionary to map [(term.field, doc name) : term frequency]
stemmer = PorterStemmer()
terms = []
terms_to_startptr = {}

# To conduct XML parsing for PatSnap corpus
def corpus_xml_parsing(corpus_doc, corpus_directory): # corpus_doc is the document file (XML file)

    filename = os.path.join(corpus_directory, corpus_doc) # filename is the name of the file in the directory

    tree = ET.parse(filename)
    root = tree.getroot()

    # For each subheading in the XML file
    for child in root:

        # If the subheading is the title or the abstract
        if child.attrib['name'] == 'Title' or child.attrib['name'] == 'Abstract':
            child_tokens = set(nltk.word_tokenize(child.text))   # Tokenize the title / abstract # Put in a set to count for doc freq
            child_tokens_no_stopwords = [w for w in child_tokens if not w in stopwords.words('english')]    # Remove stopwords
            
            for token in child_tokens_no_stopwords:
                token = stemmer.stem(token)   # Stem the word
                term = token + "." + child.attrib['name'].lower()    # No case-folding for the word # Change the child.tag to abstract / title

                # If term exists within the term dictionary
                if term in term_to_docfreq:
                    term_to_docfreq[term] += 1  # Add one to the frequency
                # Else instantiate one copy of it
                else:
                    term_to_docfreq.setdefault(term, 1)
                    terms.append(term)
                    
                # If the document does not exist in the postings dictionary
                if corpus_doc not in term_to_docposting[term]:
                    term_to_docposting[term].append(corpus_doc) # Add this document to the postings list

                termdocname = (token, corpus_doc)   # Store the document name as a tuple (token.field, document name)
                if termdocname not in termdocname_to_termfreq:  # If it does not exist in the data structure
                    termdocname_to_termfreq.setdefault(termdocname, 1)  # Add to data structure
                else:
                    termdocname_to_termfreq[termdocname] += 1   # Else add one to the frequency

    # Need to write to dictionary.txt
    
    
# Indexing the corpus into dictionary.txt
def corpus_indexing(corpus_path, dictionary_output, postings_output):

    corpus_list = os.listdir(corpus_path)  # Getting the directory of the corpus

    for each_file in corpus_list:
        corpus_xml_parsing(each_file, corpus_path)    # Parse each XML document

    # sort the terms
    terms = sorted(terms)
 
    with open(postings_output, "w+") as p:
        for term in terms:
            # to keep track of the start pointer
            startptr = p.tell()
            terms_to_startptr[term] = startptr
 
            list_of_docid = term_to_docposting[term]  # list_of_docid is the list of names of the XML file in the corpus
            
            for posting in list_of_docid:
                termDocId = (term, posting)
                text = str(posting) + " " + str(termsDocId_to_freq[termDocId] * docId_to_cosnormalisation[posting]) + " " # format: docID normalisedtf
                p.write(text)
            p.write('\n')

def indexDictAndPosting(inPath, outDictionary, outPostings):

    getList = {}
    allWords = []
    allFiles = []

    # To store document length for length normalization
    documentLength = {}

    # Dictionary to store term -> documentID -> Term frequency
    termToDictToTermFreq = {}

    # NLTK porter stemmer
    porterStem = PorterStemmer()
    directory = os.listdir(inPath)
    #print(directory)

    # Open directory
    for f in directory:
        #filename is each file in the directory
        print("current file: ")
        print(f)

        # Ignore hidden files
        if (not f.startswith('.')):
            allFiles.append(int(f))
            # Content now stores each line
            filename = os.path.join(inPath, f)
            with open(filename) as fileObj:
                content = fileObj.readlines()

            # Iterating through each line
            for sentence in content:

                sentence = sentence.decode('ascii', 'ignore')
                # tokens store array of words
                tokens = nltk.word_tokenize(sentence)

                for word in tokens:
                    # Stem / lower case
                    word = porterStem.stem(word)

                    # Check if word already exist
                    # Case 1 : Word exist
                    if word in allWords:
                        if int(f) not in getList[word]:
                            getList[word].append(int(f))
                            termToDictToTermFreq[word][int(f)] = 1
                        else:
                            termToDictToTermFreq[word][int(f)] = termToDictToTermFreq[word][int(f)] + 1

                    # Case 2 : Word does not exist
                    else:
                        # puts docID into an array, and point the 'word' as a key to it
                        getList[word] = []
                        getList[word].append(int(f))
                        termToDictToTermFreq[word] = {}
                        termToDictToTermFreq[word][int(f)] = 1
                        # Record the word
                        allWords.append(word)

            totalTemp = 0.0
            for eachWord in allWords:
                if int(f) in termToDictToTermFreq[eachWord]:
                    if termToDictToTermFreq[eachWord][int(f)] > 0:
                        termFreqWeight = 1 + math.log(termToDictToTermFreq[eachWord][int(f)],10)
                        totalTemp = totalTemp + math.pow(termFreqWeight, 2)

            fileDocumentLength = math.sqrt(totalTemp)
            documentLength[int(f)] = fileDocumentLength


    # All words are now finished indexing on machine's data structure, time to write them into files
    # Sort by terms then docID.

    # Sort the word
    allWords.sort()

    dictionaryOutput = open(outDictionary, 'w')
    postingOutput = open(outPostings, 'w')
    for eachWord in allWords:
        # Write into dictionary file

        # Write word
        dictionaryOutput.write(eachWord)
        dictionaryOutput.write(' ')
        # Write document frequency
        dictionaryOutput.write(str(len(getList[eachWord])))
        # Write file cursor/pointer position
        dictionaryOutput.write(' ')
        dictionaryOutput.write(str(postingOutput.tell()))

        # Sort docID
        getList[eachWord].sort()

        #Write into postings file
        for eachID in getList[eachWord]:
            postingOutput.write('%s' % eachID)
            postingOutput.write(',')
            postingOutput.write(str(termToDictToTermFreq[eachWord][int(eachID)]))
            postingOutput.write(' ')
        # New line to seperate word/postings
        postingOutput.write('\n')
        dictionaryOutput.write('\n')

    #stubs
    dictionaryOutput.write('_ ')
    dictionaryOutput.write('_ ')
    dictionaryOutput.write(str(postingOutput.tell()))

    allFiles.sort()
    for eachFile in allFiles:
        postingOutput.write(str(eachFile))

        # Writing document length of each document....
        postingOutput.write(',')
        postingOutput.write(str(Decimal.from_float(documentLength[int(eachFile)])))
        postingOutput.write(' ')

def usage():
    print "usage: " + sys.argv[0] + " -i path-of-file-for-indexing -d output-dictionary -p output-posting"

indexingPath = output_file_p = output_file_d = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == '-i':
        indexingPath = a
    elif o == '-d':
        output_file_d = a
    elif o == '-p':
        output_file_p = a
    else:
        assert False, "unhandled option"
if indexingPath == None or output_file_p == None or output_file_d == None:
    usage()
    sys.exit(2)

dictionaryFileName = output_file_d
postingFileName = output_file_p
corpus_indexing(indexingPath, output_file_d, output_file_p)
#indexDictAndPosting(indexingPath, dictionaryFileName, postingFileName)