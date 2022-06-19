default_aggregation_mappings = {'Business': ['SUM']}
field_aggregations = {}
field_groups = {}
field_equals = {'Business': {"'renewal'"}, 'Branch': {"'rajkot'", "'surat'"}}
fields = {'BRANCH': 'branch'}
def group_comparison_qry(qry, field_equals):
    comparison_words = ['compare', 'vs', 'versus']
    comparison_query = False
    for word in comparison_words:
        if word in qry:
            comparison_query = True
    for key in field_equals.keys():
        if len(field_equals[key]) >1 and comparison_query == True:
            field_groups[key] = key
    for key in fields.keys():
        if key not in field_aggregations.keys():
            if key in default_aggregation_mappings.keys():
                if key in field_equals.keys() and len(field_equals[key]) == 1:
                        field_aggregations[default_aggregation_mappings[key][0]] = key
    return field_groups, field_aggregations

print(group_comparison_qry("show March premiums of north zone vs south zone", field_equals))
