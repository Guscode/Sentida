# -*- coding: utf-8 -*-
# Author: CINeMa - SOHa and E. KranC

'''
Sentida().sentida(text,
                    output = ["mean", "total", "by_sentence_mean", "by_sentence_total"],
                    normal=True,
                    speed = ["normal", "fast"])

Outputs the sentiment value of the Danish input text.
Define the output to your liking based on the input and desired output.
Set normal to true if you want values between -1 and 1.
Define the speed if you want _speed_
'''

#################
### LIBRARIES ###
#################

import os
import re
from collections import namedtuple
from inspect import getsourcefile

import nltk
import numpy as np
import pandas as pd
from nltk.stem import SnowballStemmer

#################
### CONSTANTS ###
#################

SENSTRUCT = namedtuple("SENSTRUCT", """B_INCR, B_DECR, C_INCR, N_SCALAR,
                       QM_MULT, QM_SUCC_MULT, EX_INTENSITY, UP_INTENSITY,
                       BUT_INTENSITY, N_TRIGGER, NEGATE, ADD, BUT_DICT,
                       BOOSTER_DICT, SENTIMENT_LADEN_IDIOMS, SPECIAL_CASE_IDIOMS
                       """)
SENSTRUCT.B_INCR = 0.293
SENSTRUCT.B_DECR = -0.293
SENSTRUCT.C_INCR = 0.733
SENSTRUCT.N_SCALAR = -0.74
SENSTRUCT.QM_MULT = 0.94
SENSTRUCT.QM_SUCC_MULT = 0.18
SENSTRUCT.EX_INTENSITY = [1.291, 1.215, 1.208]
SENSTRUCT.UP_INTENSITY = 1.733
SENSTRUCT.BUT_INTENSITY = [0.5, 1.5]
SENSTRUCT.N_TRIGGER = "no"
SENSTRUCT.NEGATE = \
    ['ikke', 'ik', 'ikk', 'ik\'', 'aldrig', 'ingen']
SENSTRUCT.ADD = \
    ['og', 'eller']
SENSTRUCT.BUT_DICT = \
    ['men', 'dog']
SENSTRUCT.BOOSTER_DICT = \
    {"temmelig": 0.1, "meget": 0.2, "mega": 0.4, "lidt": -0.2, "ekstremt": 0.4,
     "totalt": 0.2, "utrolig": 0.3, "rimelig": 0.1, "seriøst": 0.3}
SENSTRUCT.SENTIMENT_LADEN_IDIOMS = {}
SENSTRUCT.SPECIAL_CASE_IDIOMS = {}

#####################
### DOCUMENTATION ###
#####################

"""
sentida(
        text = string,                      Text to analyze
        output = ['mean',                   Returns as complete text mean
                  'total',                  Returns as complete text total
                                              Calculated by sentence and summed
                  'by_sentence_mean',       Returns list of mean sentiment by sentence
                  'by_sentence_total'],     Returns list of total sentiment by sentence
        normal = True,                      Normalize sentiment score (-1 to 1)
        speed = ['normal', 'fast']          If you want to compensate precision for speed
        )


USAGE EXAMPLES:
Define the class:
    SEN = Sentida()

Single sentence:
    SEN.sentida(
            text = 'Lad der blive fred.',
            output = 'mean',
            normal = False)

    Output:
        # 2.0

Multiple sentences normalized:
    SEN.sentida(
            text = 'Lad der bliver fred. Det går dårligt!',
            output = 'by_sentence_total',
            normal = True)

    Output:
        # [0.4, -0.895429]

"""

##############################
### CUSTOM IMPLEMENTATIONS ###
###     STATIC METHODS     ###
##############################

class Sentida():

    # def get_script_path(self):
    #     return os.path.dirname(os.path.realpath(sys.argv[0]))

    def __init__(self, lexicon_file="aarup.csv", intensifier_file = "intensifier.csv"):
        # Reading the sentiment dictionary files and fixing the encoding
        _this_module_file_path_ = os.path.abspath(getsourcefile(lambda: 0))
        # _this_module_file_path_ = self.get_script_path()
        self.aarup = pd.read_csv(os.path.join(os.path.dirname(_this_module_file_path_), lexicon_file), encoding='ISO-8859-1')
        self.intensifier = pd.read_csv(os.path.join(os.path.dirname(_this_module_file_path_), intensifier_file), encoding='ISO-8859-1')
        self.intensifier['stem'] = self.fix_unicode(self.intensifier['stem'])

    # Function for working around the unicode problem - shoutout to /jry
    def fix_unicode(self, df_col):
        return df_col.apply(lambda x: x.encode('raw_unicode_escape').decode('utf-8'))

    # Returns multiplier by amount of exclamation marks in input
    def exclamation_modifier(self, sentence):
        ex_counter = sentence.count('!')
        value = 1
        if ex_counter == 0:
            return 1
        for idx, m in enumerate(SENSTRUCT.EX_INTENSITY):
            if idx <= ex_counter:
                value *= m
        return value

    # Returns amount of question marks in input
    def question_identifier(self, text):
        return text.count('?')

    # Returns input without punctuation
    def punct_cleaner(self, text):
        table = str.maketrans('!?-+_#.,;:\'\"', 12*' ')
        return text.translate(table)

    # Function for removing punctuation from a sentence and turning it into a
    # list of words
    def clean_words_upper(self, sentence):
        return self.punct_cleaner(sentence).split()

    # Function for removing punctuation from a sentence, making the letters lower
    # case, and turning it into a list of words
    def clean_words_lower(self, text):
        return self.punct_cleaner(text).lower().split()

    # Function for getting the positions of words that are written in upper case:

    def caps_identifier(self, words):
        positions = []
        for word in words:
            if word.upper() == word:
                positions.append(words.index(word))
        return positions

    # Function for modifing the sentiment score of words that are written in
    # upper case:

    def caps_modifier(self, sentiments, words):
        positions = self.caps_identifier(words)
        for i in range(len(sentiments)):
            if i in positions:
                sentiments[i] *= SENSTRUCT.UP_INTENSITY
        return sentiments

    # Function for identifying negations in a list of words. Returns list of
    # positions affected by negator.

    def get_negator_affected(self, words):
        positions = []

        for word in words:
            if word in SENSTRUCT.NEGATE:
                neg_pos = words.index(word)
                positions.append(neg_pos)
                positions.append(neg_pos + 1)
                positions.append(neg_pos - 1)
                positions.append(neg_pos + 2)
                positions.append(neg_pos + 3)
        return positions

    # Get all intensifiers
    def get_intensifier(self, sentiments, word_list):
        intensifiers_df = self.intensifier.loc[self.intensifier['stem'].isin(word_list)]
        intensifiers = intensifiers_df['stem'].tolist()
        scores = intensifiers_df['score'].tolist()
        position = []

        for word in word_list:
            if word in intensifiers:
                inten_pos = word_list.index(word)

                if inten_pos + 1 not in position:
                    position.append(inten_pos + 1)
                    if inten_pos + 1 < len(sentiments):
                        sentiments[inten_pos +
                                   1] *= scores[intensifiers.index(word)]

                if inten_pos - 1 not in position:
                    position.append(inten_pos - 1)
                    if inten_pos - 1 > 0:
                        sentiments[inten_pos -
                                   1] *= scores[intensifiers.index(word)]

                if inten_pos + 2 not in position:
                    position.append(inten_pos + 2)
                    if inten_pos + 2 < len(sentiments):
                        sentiments[inten_pos +
                                   2] *= scores[intensifiers.index(word)]

                if inten_pos + 3 not in position:
                    position.append(inten_pos + 3)
                    if inten_pos + 3 < len(sentiments):
                        sentiments[inten_pos +
                                   3] *= scores[intensifiers.index(word)]

        return sentiments

    # Locates 'men' (but) in a list of words:

    def men_identifier(self, words):
        position = 0
        for word in words:
            if word == 'men':
                position = words.index(word)
        return position

    # Modifies sentiment of words before or after 'men' (but) in list of words

    def men_sentiment(self, sentiments, words):
        for i in range(len(sentiments)):
            if i < self.men_identifier(words):
                sentiments[i] *= SENSTRUCT.BUT_INTENSITY[0]
            else:
                sentiments[i] *= SENSTRUCT.BUT_INTENSITY[1]

        return sentiments
    # Need empirically tested weights for the part before and after the 'men's'

    # Stems words of sentence

    def stemming(self, words):
        stemmer = SnowballStemmer('danish')
        return [stemmer.stem(word) for word in words]
    # Snowball has limited Danish stemmer

    # Returns sentiment scores of input list by the aarup dictionary

    def get_sentiment(self, word_list):
        sentiment_df = self.aarup.loc[self.aarup['stem'].isin(word_list)]
        words = sentiment_df['stem'].tolist()
        scores = sentiment_df['score'].tolist()
        senti_scores = []

        for i in word_list:
            if i in words:
                senti_scores.append(scores[words.index(i)])
            else:
                senti_scores.append(0)

        return senti_scores

    def sentida(self, text, output = ["mean", "total", "by_sentence_mean", "by_sentence_total"], normal = True, speed = ["normal", "fast"]):

        if speed  == "fast":
            sents = filter(None, re.split("[.:;?!]", text))

            senti_words = np.array([self.get_sentiment(self.stemming(re.sub('\/|\,|\'|\"', '', string.lower()).split())) for string in sents])
            if output == "mean":
                senti = np.sum([np.sum(words) / len(words) for words in senti_words]) / len(senti_words)
            elif output == "total":
                senti = np.sum([np.sum(words) for words in senti_words])
            elif output == "by_sentence_mean":
                senti = [(np.sum(words) / len(words)) for words in senti_words]
            else: # by_sentence_total
                senti = [np.sum(words) for words in senti_words]
            if normal == True:
                senti = np.multiply(senti, [0.2] * len(list(senti)))
                senti = np.where(senti < -1, -1.0, np.where(senti > 1, 1.0, senti))
            return senti
        else:
            '''
            Turns text input into a sentiment score.

            Method works as follows:
                output - mean:
                    Analyzes the text as a single sentence
                output - total || by_sentence_mean || by_sentence_total
                    Splits into sentences to analyze each as a single sentence
                    Splits branch into output branches
            '''
            # Goes into sentence splitting if it's not the global mean output
            if output == "by_sentence_mean" or output == "by_sentence_total" or output == "total":
                sentences = nltk.sent_tokenize(text)
                # The tokenizer splits !!! into two sentences if at the end of the text
                # Remove problem by analyzing, appending, and removing
                if sentences[-1] == "!":
                    sentences[-2] = sentences[-2] + "!"
                    del sentences[-1]
                sentences_output = []

                # Sentence splitting branch
                for sent in sentences:
                    words_upper = self.clean_words_upper(sent)
                    words_lower = self.clean_words_lower(sent)
                    stemmed = self.stemming(words_lower)
                    sentiments = self.get_sentiment(stemmed)

                    if self.men_identifier(words_lower) > 0:
                        sentiments = self.men_sentiment(sentiments, words_lower)

                    sentiments = self.get_intensifier(sentiments, stemmed)
                    sentiments = self.caps_modifier(sentiments, words_upper)

                    if self.question_identifier(sent) == 0:
                        for i in set(self.get_negator_affected(words_lower)):
                            if i < len(sentiments) and i >= 0:
                                sentiments[i] *= -1

                    if len(words_lower) == 0:
                        sentences_output.append(0)

                    ex_mod = self.exclamation_modifier(sent)
                    sentiments[:] = [sentiment *
                                    ex_mod for sentiment in sentiments if sentiment != 0]

                    if normal:
                        sentiments = np.multiply(
                            [float(i) for i in sentiments], ([0.2]*len(sentiments)))
                        sentiments = np.where(
                            sentiments < -1, -1, np.where(sentiments > 1, 1, sentiments))

                    total_sentiment = sum(sentiments)
                    if output == "total" or output == "by_sentence_total":
                        sentences_output.append(total_sentiment)
                    elif output == "by_sentence_mean" and len(sentiments) != 0:
                        sentences_output.append(total_sentiment / len(sentiments))
                    else:
                        sentences_output.append(0)

                if output == "by_sentence_mean" or output == "by_sentence_total":
                    if len(sentences_output) <= 1:
                        return sentences_output[0]
                    return sentences_output
                elif output == "total":
                    return sum(sentences_output)
                else:
                    return sentences_output

            else:
                words_upper = self.clean_words_upper(text)
                words_lower = self.clean_words_lower(text)
                stemmed = self.stemming(words_lower)
                sentiments = self.get_sentiment(stemmed)

                if self.men_identifier(words_lower) > 0:
                    sentiments = self.men_sentiment(sentiments, words_lower)

                sentiments = self.get_intensifier(sentiments, stemmed)
                sentiments = self.caps_modifier(sentiments, words_upper)

                if self.question_identifier(text) == 0:
                    for i in set(self.get_negator_affected(words_lower)):
                        if i < len(sentiments) and i >= 0:
                            sentiments[i] *= -1

                if len(words_lower) == 0:
                    sentences_output.append(0)

                ex_mod = self.exclamation_modifier(text)
                sentiments[:] = [sentiment *
                                ex_mod for sentiment in sentiments if sentiment != 0]

                if normal:
                    sentiments = np.multiply(
                        [float(i) for i in sentiments], ([0.2]*len(sentiments)))
                    sentiments = np.where(sentiments < -1, -1,
                                        np.where(sentiments > 1, 1, sentiments))

                if len(sentiments) > 0:
                    return sum(sentiments) / len(sentiments)
                else:
                    return 0
            return "An error occured here instead"
        return "An error occured"

def sentida_examples():
    SEN = Sentida()
    print("_____________________________")
    print("\nExample of usage:\nLad der bliver fred\nSentiment = ", SEN.sentida(
        "Lad der blive fred.", output="mean"), "\n_____________________________")
    # Example of usage: 2.0
    print("\nWith exclamation mark:\nLad der blive fred!\nSentiment = ", SEN.sentida(
        "Lad der blive fred!", output="mean"), "\n_____________________________")
    # With exclamation mark: 3.13713
    print("\nWith several exclamation mark:\nLad der blive fred!!!\nSentiment = ", SEN.sentida(
        "Lad der blive fred!!!", output="mean"), "\n_____________________________")
    # With several exclamation mark:  3.7896530399999997
    print("\nUppercase:\nlad der BLIVE FRED\nSentiment = ", SEN.sentida(
        "Lad der BLIVE FRED", output="mean"), "\n_____________________________")
    # Uppercase:  3.466
    print("\nNegative sentence:\nDet går dårligt\nSentiment = ", SEN.sentida(
        "Det går dårligt.", output="mean"), "\n_____________________________")
    # With exclamation mark:  -1.8333333333333335
    print("\nNegation in sentence:\nDet går ikke dårligt\nSentiment = ", SEN.sentida(
        "Det går ikke dårligt.", output="mean"), "\n_____________________________")
    # Negation in sentence:  1.8333333333333335
    print("\n'Men' ('but'):\nLad der blive fred, men det går dårligt\nSentiment = ", SEN.sentida(
        "Lad der blive fred, men det går dårligt.", output="mean"), "\n_____________________________")
    # 'Men' ('but'):  -1.5
    print("\nNon-normalized:\nLad der blive fred\nSentiment = ", SEN.sentida(
        "Lad der blive fred.", output="mean", normal=False), "\n_____________________________")
    # Normalized:  0.4
    print("\nMultiple sentences mean:\nLad der bliver fred. Det går dårligt!\nSentiments =", SEN.sentida(
        "Lad der bliver fred. Det går dårligt!", "by_sentence_mean"), "\n_____________________________")
    print("\nMultiple sentences total:\nLad der bliver fred. Det går dårligt!\nSentiments =", SEN.sentida(
        "Lad der bliver fred. Det går dårligt!", "by_sentence_total"), "\n_____________________________")

if __name__ == "__main__":
    Sentida()
