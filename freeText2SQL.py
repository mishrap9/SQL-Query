from nltk import ngrams
import os
import json
from sutime import SUTime
import inflect
import re

re_compile = re.compile(r'^\'(.*)\'$')


grams_len = 6
default_date_field = 'ENTRY_DATE'
default_year = '2018'

def get_phrases_from_text(seed, text, threshold):
    phrases_text = []
    phrases = []
    for i in reversed(range(2,6)):
        phrases += list(ngrams(text.split(), i))
    for phrase in phrases:
        phrase = " ".join(phrase)
        if s_utils.get_similarity(seed, phrase) > threshold:
            phrases_text.append(phrase)
    return phrases_text

def get_aggregations_mappings(filename):
    with open(filename) as f:
        mappings = f.readlines()
    field_mappings = {}
    for mapping in mappings:
        mapping_tokens = mapping.split(':')
        mapping_synonyms = mapping_tokens[1].split(',')
        mapping_synonyms_clean = []
        for mapping_synonym in mapping_synonyms:
            mapping_synonyms_clean.append(mapping_synonym.replace('\n', '').strip())
        field_mappings[mapping_tokens[0].strip()] = mapping_synonyms_clean
    return field_mappings

def get_field_type(filename, field_type):
    with open(filename) as f:
        mappings = f.readlines()
    
    field_mappings = []
    for mapping in mappings:
        mapping_tokens = mapping.split(':')
        mapping_synonyms = mapping_tokens[1].split(',')
        mapping_synonyms_clean = []
        for mapping_synonym in mapping_synonyms:
            mapping_synonyms_clean.append(mapping_synonym.replace('\n', '').strip().lower())
        if field_type in mapping_tokens[0]:
            field_mappings.append(mapping_tokens[0][0:str(mapping_tokens[0]).index(' (')])
    return field_mappings

def get_field_mappings(filename):
    with open(filename) as f:
        mappings = f.readlines()
    
    field_mappings = {}
    for mapping in mappings:
        mapping_tokens = mapping.split(':')
        mapping_synonyms = mapping_tokens[1].split(',')
        mapping_synonyms_clean = []
        for mapping_synonym in mapping_synonyms:
            mapping_synonyms_clean.append(mapping_synonym.replace('\n', '').strip().lower())
        field_mappings[mapping_tokens[0][0:str(mapping_tokens[0]).index(' (')]] = mapping_synonyms_clean
    return field_mappings

def get_value_mappings(filename):
    with open(filename) as f:
        mappings = f.readlines()
    
    field_mappings = {}
    i = 0
    index_mappings = {}
    index_mappings[0] = 'Branch'
    index_mappings[1] = 'POLICY_NUMBER'
    index_mappings[2] = 'Product'
    index_mappings[3] = 'Zone'
    index_mappings[4] = 'Branch'
    index_mappings[5] = 'Status'
    index_mappings[6] = 'AGENT_NAME'
    index_mappings[7] = 'Employee_Name'
    index_mappings[8] = 'Business'
    
    for index_mapping in index_mappings:
        field_mappings[index_mappings[index_mapping]] = set()
    
    for mapping in mappings:
        if i>0:
            mappings_tokens = mapping.split('~')
            row_count = 0
            for mapping_token in mappings_tokens:
                mapping_str = mapping_token.replace('\n', '').strip().lower()
                if len(mapping_str)>0:
                    field_mappings[index_mappings[row_count]].add(mapping_str)
                row_count+=1
        i+=1
    return field_mappings

def get_ngrams(text_qry):
    grams_qry = {}
    for i in range(1, grams_len):
        grams = list(ngrams(text_qry.split(), i))
        grams_str = []
        for gram in grams:
            grams_str.append(' '.join(str(i) for i in gram))
        grams_qry[i] = grams_str
    return grams_qry

def get_date_fields(text_qry, date_type_fields, field_mappings):
    date_fields = []
    for date_field in date_type_fields:
        for field_mapping in field_mappings[date_field]:
            if field_mapping in text_qry:
                date_fields.append(date_field)
    return date_fields

def is_plural(gram, values):
    p = inflect.engine()
    for value in values:
        if gram == p.plural(value):
            return value
    return ''

def pluralize_singularize(text_qry):
    qry = text_qry.lower().replace(',', ' ')
    tokens = qry.split()
    p = inflect.engine()
    plural_tokens = []
    singular_tokens = []
    
    for token in tokens:
        if(len(token)>len(p.plural(token))):
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

def is_ranking_qry(text_grams):
    ranking_terms = ['top', 'bottom', 'highest', 'lowest', 'best', 'worst']
    for ranking_term in ranking_terms:
        if ranking_term in text_grams:
            return True
    return False

def get_n (text):
    list_of_words = ['top', 'bottom', 'highest', 'lowest', 'best', 'worst']
    for i in range(0, len(list_of_words)):
        if list_of_words[i] in text:
            expression = text.split(list_of_words[i])
            trim_str = expression[1].strip()
            number = ''
            for i in trim_str:
                if i.isdigit():
                    if i !=' ':
                        number = number + i
                    else:
                        break
                else:
                    break
            return number

def stem_string(ps, text_qry):
    text_tokens = text_qry.replace(', ', ' ').split()
    stem_tokens = []
    for text_token in text_tokens:
        stem_tokens.append(ps.stem(text_token))
    return ' '.join(stem_tokens)

def get_stem_map(ps, value_mappings):
    stem_map = {}
    for value_mapping in value_mappings.keys():
        for value_map in value_mappings[value_mapping]:
            stem_map[stem_string(ps, value_map)] = value_map
    return stem_map

field_mappings = get_field_mappings("resources/mappings.txt")
value_mappings = get_value_mappings("resources/valueMappings.csv")
aggregation_mappings = get_aggregations_mappings("resources/aggregations.txt")
timecomp_mappings = get_aggregations_mappings("resources/timeComparison.json")
date_type_fields = get_field_type("resources/mappings.txt", 'date')
sutime = SUTime(jars='python-sutime/jars/', mark_time_ranges=True)

qry = "which branches are linked to Aditya Birla Insurance Brokers Ltd"
grams_qry = pluralize_singularize(qry)

stem_map = get_stem_map(ps, value_mappings)

is_ranking_qry(qry)

field_equals = {}
fields = {}
field_aggregations = {}
field_groups = {}
limit = ''
order = 'DESC'
for gram_cnt in range(grams_len-1, 0, -1):
    grams = grams_qry[gram_cnt]
    for gram in grams:
        gram_stem = stem_string(ps, gram)
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
                           field_equals[value_mapping] = "'" + stem_map[gram_stem] + "'"
        for field_mapping in field_mappings.keys():
           if gram in field_mappings[field_mapping]:
               if not field_mapping in fields.keys():
                   not_in_field = True
                   for field in fields.keys():
                       if gram in fields[field]:
                           not_in_field = False
                   if not_in_field:
                       fields[field_mapping] = gram

for field in fields.keys():
    for aggregation in aggregation_mappings.keys():
        for aggregation_str in aggregation_mappings[aggregation]:
            if (aggregation_str + ' ' + fields[field] in qry) or (aggregation_str + ' of ' + fields[field] in qry)  or (aggregation_str + ' value of ' + fields[field] in qry) or (aggregation_str + ' number of ' + fields[field] in qry):
                 field_aggregations[aggregation] = field
    if 'per ' + fields[field] in qry or fields[field] + ' wise' in qry:
        field_groups[field] = field

time_expressions = sutime.parse(qry)
time_expressions_text = ''
time_begin = ''
time_end = ''
time_value = ''
no_date_field = True
if(len(time_expressions)>0):
    for date_field in date_type_fields:
        if date_field.lower() not in qry:
            for date_field_mapped in field_mappings[date_field]:
                if date_field_mapped in qry:
                    no_date_field = False
                    break
        else:
            no_date_field = False
            break
    time_expressions_text = time_expressions[0]['text']
    if 'from' in time_expressions_text and 'to ' in time_expressions_text:
        time_begin = time_expressions[0]['value']['begin']
        time_end = time_expressions[0]['value']['end']
        if 'XXXX' in time_begin:
            time_begin = time_begin.replace('XXXX', default_year)
        if 'XXXX' in time_end:
            time_end = time_end.replace('XXXX', default_year)
    else:
        time_value = time_expressions[0]['value']
        time_value = time_value.replace('XXXX', default_year)

if no_date_field:
    if len(time_begin)>0 and len(time_end)>0:
        field_equals[default_date_field] = default_date_field + " >= '" + time_begin + "' AND " + default_date_field + " <= '" + time_end + "'"
    elif len(time_expressions_text)>0 and len(time_value)>0:
        for timecomp_mapping in timecomp_mappings.keys():
            for time_comparison in timecomp_mappings[timecomp_mapping]:
                if (time_comparison + ' ' +  time_expressions_text) in qry:
                    field_equals[default_date_field] = timecomp_mapping + " '" + time_value + "'"
                    break
        if default_date_field not in field_equals.keys():
                field_equals[default_date_field] = '== ' + time_value
else:
    date_fields = get_date_fields(qry, date_type_fields, field_mappings)
    if len(date_fields)==1:
        for timecomp_mapping in timecomp_mappings.keys():
            for time_comparison in timecomp_mappings[timecomp_mapping]:
                if (time_comparison + ' ' +  time_expressions_text) in qry:
                    field_equals[date_fields[0]] = timecomp_mapping + " '" + time_value + "'"
        if date_fields[0] not in field_equals.keys():
            field_equals[date_fields[0]] = '== ' + time_value


def construct_qry(table_name, field_equals, fields, field_aggregations, field_groups):
    sql_qry = "SELECT * FROM " + table_name
    i=0    
    for field_group in field_groups.keys():
        if i==0:
            sql_qry = sql_qry + ' GROUP BY ' + field_groups[field_group]
        else:
            sql_qry = sql_qry + ' , ' + field_groups[field_group]
        i+=1
    i=0    
    for field_equal in field_equals.keys():
        if 'date' in field_equal.lower():
            if i==0:
                sql_qry = sql_qry + ' WHERE ' + field_equals[field_equal]
            else:
                sql_qry = sql_qry + ' AND ' + field_equals[field_equal]
            i+=1
        else:
            if i==0:
                sql_qry = sql_qry + ' WHERE ' + field_equal + " = " + field_equals[field_equal]
            else:
                sql_qry = sql_qry + ' OR ' + field_equal + " = " + field_equals[field_equal]
            i+=1
            
    i = 0
    query_field = ''
    if len(field_aggregations.keys())>0:
        for field_aggregation in field_aggregations.keys():
            if i > 0:
                query_field = query_field + ', '
            query_field = query_field + field_aggregation + '(' + field_aggregations[field_aggregation] + ')'
            i += 1
        if len(query_field)>0:
            sql_qry = sql_qry.replace ('*', query_field )
    elif len(fields.keys())>0:
        for field in fields.keys():
            if i > 0:
                query_field = query_field + ', '
            query_field = query_field + field
            i += 1
        if len(query_field)>0:
            sql_qry = sql_qry.replace ('*', query_field )
    return sql_qry
    
construct_qry("AppoloTable", field_equals, fields, field_aggregations, field_groups)