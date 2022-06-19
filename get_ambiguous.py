from nltk import ngrams
import os
import json
from sutime import SUTime
import inflect
import re
import datetime
from nltk.stem import PorterStemmer
from nlputils import *

grams_len = 6
default_date_field = 'ENTRY_DATE'
default_year = '2018'
nlp_utils = NLPUtils()
# sql_utils = SQLUtils()
# db_utils = DBUtils()
field_syns, field_value_syns = nlp_utils.get_synonyms_mapping("resources/valueSynonyms.csv")
field_mappings = nlp_utils.get_field_mappings("resources/mappings.txt")
value_mappings = nlp_utils.get_value_mappings("resources/valueMappings.csv")
qry = "this is a query about rahul kumar"
grams_qry = nlp_utils.pluralize_singularize(qry)
field_value_matches, field_matches = get_ambiguous(grams_qry, grams_len)
print (field_matches)


def get_ambiguous(grams_qry, grams_len):
    field_value_matches = {}
    field_matches = {}
    for gram_cnt in range(grams_len-1, 0, -1):
        grams = grams_qry[gram_cnt]
        for gram in grams:
            gram_stem = nlp_utils.stem_string(gram)
            if gram_stem in stem_map.keys():
                value_mapped = stem_map[gram_stem]
                for value_mapping in value_mappings.keys():
                   if value_mapped in value_mappings[value_mapping]:
                       if not value_mapping in field_equals.keys():
                           not_in_value_field = True
                           for field_equal in field_equals.keys():
                               if "'" + stem_map[gram_stem] + "'" == field_equals[field_equal]:
                                   not_in_value_field = True
                           if not_in_value_field:
                               add_to_field_mappings(field_matches, value_mapping, "'" + stem_map[gram_stem] + "'")
                       else:
                           if value_mapping in field_equals.keys():
                               add_to_field_mappings(field_matches, value_mapping, "'" + stem_map[gram_stem] + "'")
            for field_mapping in field_mappings.keys():
               if gram in field_mappings[field_mapping]:
                   if not field_mapping in fields.keys():
                       not_in_field = True
                       for field in fields.keys():
                           if gram in fields[field]:
                               not_in_field = False
                       if not_in_field:
                           field_matches[field_mapping] = gram
    return field_value_matches, field_matches