import re
import random
import itertools
import warnings
warnings.filterwarnings('ignore')

# numpy, pandas
import numpy as np
import pandas as pd
from numpy.linalg import norm

# nltk
import nltk
from nltk.corpus import wordnet as wn
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer,PorterStemmer
from nltk.corpus import stopwords

# spacy
import spacy

# gensim
from gensim.models.word2vec import Word2Vec
import gensim.downloader as api

# parrot, pytorch
from parrot import Parrot
import torch


nltk.download('wordnet')
nltk.download('omw-1.4')
glovemodel = api.load("glove-wiki-gigaword-100")
spacymodel = spacy.load("en_core_web_sm")


class Preprocessor:
    def __init__(self, note):
        if not note: raise ValueError("Error: Input is invalid. It should be a string.")
        self.note = note

    def __call__(self):
        tokenizer = RegexpTokenizer(r'\w+')
        re_strip = re.compile('<.*?>')

        self.note = self.note.lower()
        self.note = re.sub(re_strip, '', self.note)
        self.note = re.sub('[0-9]+', '', self.note)
        self.note = " ".join(tokenizer.tokenize(self.note))

        return self.noteo

class Synonymizer:
    def __init__(self, note):
        self.preprocessor = Preprocessor(note)
        self.note = self.preprocessor()
        self.glovemodel = api.load("glove-wiki-gigaword-100")
        self.spacymodel = spacy.load("en_core_web_sm")
        self.posmap = {'VERB':'v', 'NOUN':'n', 'PRON':'n', 'PROPN':'n', 'ADJ':'a', 'ADV':'r'}

    def __call__(self):
        '''return dictionary of words : synonym(s) pairs.
        '''
        # NOTE current version removes n grams.
        d = {}

        for word in self.note.split():
            synonyms = self.synonyms_by_word(word)

            if synonyms: synonyms = list(set([synonym
                                     for synonym in synonyms
                                     if len(synonym.split("_"))==1]))

            if synonyms: d[word] = synonyms

        return d

    def pos_by_word(self, word):
        for w in nlp(self.note):
            if str(w)==word: return w.pos_

    def similarities_by_word(self, word, synonyms):
        def cosinesim(v1, v2):
            return (np.dot(v1, v2 / (norm(v1) * norm(v2))))

        def embed(vector, model):
            try:
                vec = self.glovemodel.get_vector(vector)
            except:
                return np.empty(0)
            return vec

        sims = {word: 1.0}
        ref  = embed(word, self.glovemodel)

        for s in synonyms:
            vec = embed(s, self.glovemodel)
            if vec.any():
                sim     = cosinesim(ref, vec)
                sims[s] = sim

        return sims

    def print_similarities(self, similarities):
        for synonym, similarity in similarities.items():
            print(f"word: {synonym}, cosine similarity: {similarity}")

    def synonyms_by_word(self, word):
        pos = self.pos_by_word(word)

        if pos not in ['VERB', 'NOUN', 'PRON', 'PROPN', 'ADJ', 'ADV']: return

        # get full set of synonyms
        synonyms = set(list(itertools.chain([synonym
                                             for synset in wn.synsets(word, pos=self.posmap[pos])
                                             for synonym in synset.lemma_names()
                                             if len(word)>1])))

        # filter this set using cosine similarities
        similarities = self.similarities_by_word(word, synonyms)

        return [synonym
                for synonym, similarity in similarities.items()
                if similarity>=0.60]

class UttGen:
    def __init__(self, note, with_gpu=False):
        self.preprocessor = Preprocessor(note)
        self.synonymizer = Synonymizer(note)
        self.parrot = Parrot(model_tag="prithivida/parrot_paraphraser_on_T5")
        self.note = self.preprocessor()
        self.synonyms = self.synonymizer()
        self.gpu = with_gpu
        self.phrasebank = [['do i need to', 'must i', 'is it required that i', 'will i need to'],
                        ['how often do i need', 'what is the timeframe for'],
                        ['when is', 'on what date is'],
                        ['is this covered or will i have to pay', 'will my insurance cover', 'will insurance cover', 'do i need to pay', 'how much will i pay for', ],
                        ['where is', 'where can i find', 'how can i find', 'i cant find', 'what is the location for',
            'can i have the location for'],
                        ['what can i', 'is there anything i can', 'can i'],
                        ['how do i prepare for', 'how can i get ready for', 'what should i bring for'],
                        ['what if i forgot', 'i forgot to', 'is it ok if i forgot'],
                        ['what is', 'tell me what is', 'describe', 'i want to understand']]
        self.paraphrases = []

    def __call__(self):
        '''return list of generated utterances for the input utterance.
        '''
        self.transformer_phrases()
        self.synonym_phrases()
        random.shuffle(self.paraphrases)
        return self.paraphrases

    def transformer_phrases(self):
        paraphrases = []
        for i in range(20):
            p = parrot.augment(input_phrase=self.note, use_gpu=self.gpu)
            if p: paraphrases.extend([t[0] for t in p])
        self.paraphrases.extend(list(set(paraphrases)))

    def add_phrases(self):
        genlist = []
        paraphrases  = []

        for plist in self.phrasebank:
            for phrase in plist:
                if phrase in self.note:
                    for i in range(len(plist)-1):
                        if plist[i]!=phrase:
                            copy = self.note
                            paraphrases.append(copy.replace(phrase, plist[i]))

        self.paraphrases.extend(paraphrases)

    def synonym_phrases(self):
        genlist = []
        paraphrases = []
        prev = 0

        for word in self.note.split():
            if word in self.synonyms:
                paraphrases.append(list(itertools.chain(*[[word], self.synonyms[word]])))
            else:
                paraphrases.append([word])

        for i in range(len(paraphrases)):
            word  = paraphrases[i][0]
            slist = paraphrases[i]

            for j in range(len(slist)):
                start = self.note.find(word, prev)
                end   = start + len(word)
                gen   = self.note[:start] + slist[j] + self.note[end:]
                genlist.append(gen)

            prev = end

        self.paraphrases.extend(list(set(genlist)))
