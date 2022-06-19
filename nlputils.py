from nltk import ngrams
import os
import json
from sutime import SUTime
import inflect
import re
import datetime
from nltk.stem import PorterStemmer

re_compile = re.compile(r'^\'(.*)\'$')

class NLPUtils:
    def __init__(self):
        self.ps = PorterStemmer()
        self.grams_len = 6
        
    def stem_string(self, text_qry):
        text_tokens = text_qry.replace(', ', ' ').split()
        stem_tokens = []
        for text_token in text_tokens:
            stem_tokens.append(self.ps.stem(text_token))
        return ' '.join(stem_tokens)
    
    def get_stem_map(self, value_mappings):
        stem_map = {}
        for value_mapping in value_mappings.keys():
            for value_map in value_mappings[value_mapping]:
                stem_map[self.stem_string(value_map)] = value_map
        return stem_map
    
    def get_ngrams(self, text_qry):
        grams_qry = {}
        for i in range(1, self.grams_len):
            grams = list(ngrams(text_qry.split(), i))
            grams_str = []
            for gram in grams:
                grams_str.append(' '.join(str(i) for i in gram))
            grams_qry[i] = grams_str
        return grams_qry
    
    def pluralize_singularize(self, text_qry):
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
        sing_plu = self.get_ngrams(plural_text + ' ' + singular_text + ' ' + text_qry)
        return sing_plu

    def get_aggregations_mappings(self, filename):
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

    def get_field_mappings(self, filename):
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

    def get_date_fields(self, text_qry, date_type_fields, field_mappings):
        date_fields = []
        for date_field in date_type_fields:
            for field_mapping in field_mappings[date_field]:
                if field_mapping in text_qry:
                    date_fields.append(date_field)
        return date_fields

    def get_field_type(self, filename, field_type):
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

    def get_matches(self, qtr_str):
        pattern = r'(([\w]+)\s*[=(LIKE)]+\s*\'([<>,:;$&?@#%!=\^\[\]\(\)\|\+\-\*\.\-\w\s]+)\')'
        matches = re.findall(pattern, qtr_str)
        return matches

    def get_period(self, qry, field_equals, fields):
        field_frequency = {}
        periodicity = {}
        periodicity['daily'] = 'DAY'
        periodicity['weekly'] = 'WEEK'
        periodicity['monthly'] = 'MONTH'
        periodicity['yearly'] = 'YEAR'
        periodicity['annually'] = 'YEAR'
        periodicity['per anum'] = 'YEAR'
        periodicity['YTD'] = 'YTD'
        periodicity['year to date'] = 'YTD'
        periodicity['MTD'] = 'MTD'
        periodicity['month to date'] = 'MTD'
        period_str = ''
        for period in periodicity.keys():

            if period in qry:
                period_str = period
            
            if len(period_str)>0:
                for date_field in field_equals.keys():
                    if 'date' in date_field.lower():
                        if date_field in field_frequency.keys():
                            field_frequency[date_field].add(periodicity[period_str])
                        else:
                            field_frequency[date_field] = set()
                            field_frequency[date_field].add(periodicity[period_str])
            
                if len(field_frequency.keys())==0:
                    for date_field in fields.keys():
                        if 'date' in date_field.lower():
                            if date_field in field_frequency.keys():
                                field_frequency[date_field].add(periodicity[period_str])
                            else:
                                field_frequency[date_field] = set()
                                field_frequency[date_field].add(periodicity[period_str])
            
                if len(field_frequency.keys())==0:
                    field_frequency['ENTRY_DATE'] = set()
                    field_frequency['ENTRY_DATE'].add(periodicity[period_str])
        return field_frequency

    def exclude_field_equals(self, field_equals, fields):
        if 'AGENT_NAME' in  field_equals.keys() and 'Employee_Name' in field_equals.keys():
            if 'AGENT_NAME' in fields.keys() and 'Employee_Name' not in fields.keys():
                fields.pop('AGENT_NAME', 0)
                field_equals.pop('Employee_Name', 0)
            elif 'AGENT_NAME' not in fields.keys() and 'Employee_Name' in fields.keys():
                fields.pop('Employee_Name', 0)
                field_equals.pop('AGENT_NAME', 0)
        
        if 'AGENT_NAME' in  field_equals.keys() and 'Employee_Name' in field_equals.keys():
            for agent_name in field_equals['AGENT_NAME']:
                for emp_name in field_equals['Employee_Name']:
                    if len(agent_name.replace("'", '')) > len(emp_name.replace("'", '')):
                        if emp_name.replace("'", '') in agent_name.replace("'", ''):
                            field_equals.pop('Employee_Name', 0)
                    if agent_name.replace("'", '') in emp_name.replace("'", ''):
                        field_equals.pop('Employee_Name', 0)

    def clean_field_equals(self, field_equals):
        for field in field_equals.keys():
            if len(field_equals[field]) > 1:
                field_values = field_equals[field]
                filtered_values = field_values.copy()
                for field_value in field_values:
                    filtered_values = self.remove_from_field_equals(field_value, filtered_values)
                field_equals[field] = filtered_values
    
    def remove_from_field_equals(self, item, values):
        is_first_time = True
        filtered_values = set()
        for value in values:
            if len(re_compile.findall(value)) > 0:
                modified_value = re_compile.findall(value)[0]
            else:
                modified_value = value
            if item == value and is_first_time:
                is_first_time = False
                filtered_values.add(value)
            elif not ((item == value and not is_first_time) or modified_value.lower() in item.lower()) :
                filtered_values.add(value)
        return filtered_values

    def get_synonyms_mapping(self, filename):
        field_syns = {}
        field_value_syn = {}
        with open (filename, 'r') as file:
            for line in file:
                expressions = line.split('|')
                synonyms = expressions[2].split(';')
                for word in synonyms:
                    field_syns[word.strip().lower()] = expressions[1].strip()
                field_syns[expressions[1].strip().lower()] = expressions[1].strip()
                field_value_syn[expressions[1].strip()] = expressions[0].strip()
        return field_syns, field_value_syn

    def get_field_types(self, filename):
        with open(filename) as f:
            mappings = f.readlines()
        field_types = {}
        for mapping in mappings:
            field_types[mapping[0:mapping.index(' (')]] = mapping[mapping.index('(') + 1:mapping.index(')')]
        return field_types

    def get_value_mappings(self, filename):
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
        index_mappings[9] = 'TL_ID'
        index_mappings[10] = 'Branch_Category'
        index_mappings[11] = 'Category_Designation'

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

    def remove_fields(self, fields, field_equals, field_aggregations):
        fields_clean = fields    
        for field in field_equals.keys():
            if field in fields.keys():
                fields_clean.pop(field, None)
        
        if len(fields_clean.keys())==0 and len(field_aggregations.keys())==0:
            field_aggregations['SUM'] = 'PREMIUM'
        return fields_clean

    def tilldate(self, qry): 
        return qry.replace("till date","till "+datetime.datetime.now().strftime("%Y-%m-%d"))

    def query_type(self, text, field_aggregations, fields):
        if text.lower().startswith("number of") or text.lower().startswith("no of") or text.lower().startswith("how many"):
             field_aggregations["COUNT"] = "*"
             fields = {}
        if "details of" in text.lower():
             fields = {}
             field_aggregations = {}
        return field_aggregations, fields

    def group_text_fields(self, fields, field_groups, field_types, field_aggregations, limit_n):
        if limit_n==0:
            for field in fields.keys():
                if field not in field_groups.keys():
                    if field_types[field] == 'text':
                        field_groups[field] = field
            if 'PREMIUM' in fields.keys():
                if field not in field_aggregations.keys():
                    field_aggregations['SUM'] = 'PREMIUM'
                    fields.pop('PREMIUM', 0)  
        return field_groups, field_aggregations, fields
    
    def text_to_num(self,query):
        match = re.findall(r'[><=]\d', query)
        if len(match)>0:
            match[0] = match[0].replace('>', '> ').replace('<', '< ').replace('=', '= ')
            query = re.sub(r'[><=]\d', match[0], query)
        query = query.replace(" 0 ", " zero ")
        query = query.replace(" 1 ", " one ")
        query = query.replace(" 2 ", " two ")
        query = query.replace(" 3 ", " three ")
        query = query.replace(" 4 ", " four ")
        query = query.replace(" 5 ", " five ")
        query = query.replace(" 6 ", " six ")
        query = query.replace(" 7 ", " seven ")
        query = query.replace(" 8 ", " eight ")
        query = query.replace(" 9 ", " nine ")

        numbers_words = {}
        units = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen"]

        tens = ["","ten", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

        scales = ["hundred", "thousand", "lakh", "million", "crore"]

        query = re.sub(r'(crore|lakh|million|thousand|hundred)+\s+(and)+', r'\1', query)


        for index, word in enumerate(units):
            numbers_words[word] = (1, index)
        for index, word in enumerate(tens):
            numbers_words[word] = (1, index * 10)
        for index, word in enumerate(scales):
            if index < 2:
                numbers_words[word] = (10 ** (index + 2), 0)
            else:
                numbers_words[word] = (10 ** (index + 3), 0)

        current = 0
        result = 0
        converted_query = ''
        for word in query.split():
            if word.lower() not in numbers_words:
                if result + current >0:
                    converted_query = converted_query + " " + str(result + current) + " " + word
                    result= 0
                    current = 0
                else:
                    converted_query = converted_query + " " + word
                continue

            scale, increment = numbers_words[word]
            current = current * scale + increment
            if scale > 100:
                result += current
                current = 0
        if result + current > 0:
            converted_query = converted_query + " " + str(result + current)

        return converted_query.strip()
    