
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
    operator_count = 0
    field_mappings = get_field_mappings('mappings.txt')
    value_mappings = get_value_mappings('valueMappings.csv')
    compared_text = ''
    for operator in comparison_operators:
        if operator in qry:
            operator_count = 1
            expression = qry.split(operator)
            for i in range (len(expression)):
                for char in expression[i].strip().split():
                    if char != ' ' and char.isdigit():
                        matched_operator = operator
                        compared_text = expression[i].strip()
                        break
                    else:
                        break
    if not operator_count:
        split_qry = qry.split(' ')
        for i in range(0, len(split_qry)):
            if split_qry[i].isnumeric():
                compared_text = ' '.join(split_qry[i:len(split_qry)])
                matched_operator = '='
                break

    if compared_text != '':
        compared_text = compared_text.split()
        numeric_count = 0
        time_count = 0
        for j in range (0, len(compared_text)):
            matched_index = 0
            if compared_text[j].isnumeric():
                if not numeric_count:
                    numeric_count = 1
                    final_comparison_text.append(compared_text[j])
            elif compared_text[j].lower() in time_words:
                if not time_count:
                    time_count = 1
                    final_comparison_text.append(compared_text[i])
            else:
                for field in value_mappings.keys():
                    if compared_text[j].lower() in value_mappings[field]:
                        matched_index = 1
                        final_comparison_text.append(compared_text[j])
                        break
                if matched_index:
                    break
        for j in range(matched_index, len(compared_text)):
            matched_index = 0
            if compared_text[j].lower in time_words:
                final_comparison_text.append(compared_text[j])
            else:
                for field in field_mappings.keys():
                    if compared_text[j].lower() in field_mappings[field]:
                        final_comparison_text.append(compared_text[j])
                        matched_index = 1
                        break
                if matched_index:
                    break
        return matched_operator + ' ' + ' '.join(final_comparison_text)


print (get_comparison_query("list top 5 branches for renewals last month"))

