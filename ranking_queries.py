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
def get_n (text):
    list_of_words = ['top', 'bottom', 'highest', 'lowest', 'best', 'worst']
    for i in range(0, len(list_of_words)):
        if list_of_words[i] in text:
            expression = text.split(list_of_words[i])
            my_string = expression[1].strip()
            number = ''
            for i in my_string:
                if i.isdigit():
                    if i !=' ':
                        number = number + i
                    else:
                        break
                else:
                    break
            return number


field_mapping = {'AGENT_NAME': ['agent', 'agent name', 'name of agent', 'field agent'], 'Employee_Name': ['employee'], 'SUM_INSURED': ['sum insured', 'value insured', 'insured value', 'insured val'], 'Zone': ['region'], 'Channel': ['channel'], 'PREMIUM': ['premium', 'pre tax premium', 'premium before tax', 'sales', 'sale'], 'Product': ['product name', 'policy name', 'product', 'pdt'], 'BRANCH_CODE': ['branch code', 'office code', 'branch id'], 'ENTRY_DATE': ['entry date', 'issuance date', 'date of issue'], 'POLICY_NUMBER': ['policy number', 'policy #', '#', 'policies'], 'NOP': ['number of policies', 'policies', 'no. of policies', '# policies', 'nop', 'nop', 'no of policies'], 'START_DATE': ['start date', 'starting from'], 'Business': ['business type', 'business category', 'business'], 'TOTAL_PREMIUM': ['total premium', 'post tax premium', 'premium after tax', 'premium with tax'], 'EXPIRY_DATE': ['expiry date', 'exipiring on'], 'ADM ID': ['adm number', 'adm code', 'e code', 'employee id'], 'BRANCH': ['branch', 'office location', 'bo'], 'AGENT_CODE': ['agent code', 'code of agent'], 'SERVICE_TAX': ['service tax']}

# qry = "all agents to Aditya Birla Insurance Brokers Ltd"
# grams_qry = pluralize_singularize(qry)
# print (grams_qry)

field_groups = {}
def get_fields_to_group (text):
    grams_qry = pluralize_singularize(text)
    for gram_cnt in range(grams_len-1, 0, -1):
        grams = grams_qry[gram_cnt]
        for gram in grams:
            for key in field_mapping.keys():
                if gram in field_mapping[key]:
                    field_groups[key] = key
                    break

    number = get_n(text)
    if number == '':
        limit = 1
    else:
        limit = number
    order = 'DESC'
    descending_words = ['top', 'best', 'highest', 'maximum']
    ascending_words = ['bottom', 'worst', 'lowest', 'minimum']
    for i in range(len(ascending_words)):
        if ascending_words[i] in text:
            order = 'ASC'
            break
        elif descending_words[i] in text:
            order = 'DESC'
            break
    return field_groups, limit, order

text = "best performing agents for <Optima Restore> in March"
print(get_fields_to_group(text))
