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

field_mappings = get_value_mappings('valueMappings.csv')
print (field_mappings)