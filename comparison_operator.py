
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
        if i > 0:
            mappings_tokens = mapping.split('~')
            row_count = 0
            for mapping_token in mappings_tokens:
                mapping_str = mapping_token.replace('\n', '').strip().lower()
                if len(mapping_str) > 0:
                    field_mappings[index_mappings[row_count]].add(mapping_str)
                row_count += 1
        i += 1
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


def get_comparison_query (qry):
    time_words = ['month', 'months', 'year', 'years', 'week', 'weeks', 'jan', 'january', 'feb', 'february', 'mar', 'march', 'apr', 'april', 'may', 'jun', 'june', 'jul', 'july', 'aug', 'august', 'sep', 'sept', 'september', 'oct', 'october', 'nov', 'november', 'dec', 'december']
    comparison_operators = ['>', '<', '=']
    final_comparison_text = []
    field_mappings = get_field_mappings('mappings.txt')
    compared_text = ''
    for operator in comparison_operators:
        if operator in qry:
            expression = qry.split(operator)
            for i in range (len(expression)):
                for char in expression[i].strip().split():
                    if char != ' ' and char.isdigit():
                        matched_operator = operator
                        compared_text = expression[i].strip()
                        break
                    else:
                        break

    if compared_text != '':
        compared_text = compared_text.split()
        matched_index = len(compared_text)
        for i in range (0, len(compared_text)):
            for fields in field_mappings.keys():
                if compared_text[i].lower() in field_mappings[fields]:
                    if i < matched_index:
                        matched_index = i
        for i in range (0, matched_index+1):
            final_comparison_text.append(compared_text[i])

    return " ".join(final_comparison_text)

print (get_comparison_query("which agents had > 5 garbage branch from 12 march to 25 march"))
print (get_comparison_query("how many branches have < 2000000 renewal premium fro 5 march to 15 march"))

