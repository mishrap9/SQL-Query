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

field_mappings = get_field_mappings('mappings.txt')
print (field_mappings)