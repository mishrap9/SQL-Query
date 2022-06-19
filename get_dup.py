field_match = {'AGENT_NAME': {"'aakash'", "'rahul kumar'"}, 'Employee_Name': {"'rahul'", "'rahul kumar'", "'aakash'"}, 'Branch_Category': {"'a'"}}


def get_dups(field_match):
    dup_field = {}
    for field, values in field_match.items():
        values = list(values)
        for value in values:
            count = 0
            match = value
            values_matched = []
            for match_field, match_values in field_match.items():
                match_values = list(match_values)
                if value in match_values and field != match_field:
                    values_matched.append(match_field)
                    values_matched.append(field)
                    count += 1
            if count >0:
                dup_field[match.strip("'")] = list(set(values_matched))
    return dup_field
print (get_dups(field_match))
