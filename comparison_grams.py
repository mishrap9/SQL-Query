from nltk import ngrams
import os
import json
import inflect
import re


grams_len = 6

def get_ngrams(text_qry):
    grams_qry = {}
    for i in range(1, grams_len):
        grams = list(ngrams(text_qry.split(), i))
        grams_str = []
        for gram in grams:
            grams_str.append(' '.join(str(i) for i in gram))
        grams_qry[i] = grams_str
    return grams_qry

def pluralize_singularize(text_qry):
    qry = text_qry.lower().replace(',', ' ')
    tokens = qry.split()
    p = inflect.engine()
    plural_tokens = []
    singular_tokens = []

    for token in tokens:
        if (len(token) > len(p.plural(token))):
            plural_tokens.append(token)
        else:
            plural_tokens.append(p.plural(token))
        if p.singular_noun(token) == False:
            singular_tokens.append(token)
        else:
            singular_tokens.append(p.singular_noun(token))
    plural_text = ' '.join(plural_tokens)
    singular_text = ' '.join(singular_tokens)
    return get_ngrams(plural_text + ' ' + singular_text)

print (pluralize_singularize("show me premium for all employees with > 5 years of experience"))