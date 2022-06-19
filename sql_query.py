def construct_qry(table_name, field_equals, fields, field_aggregations, field_groups):
    sql_qry = "SELECT * FROM " + table_name
    i = 0
    for field_group in field_groups.keys():
        if i == 0:
            sql_qry = sql_qry + ' GROUP BY ' + field_groups[field_group]
        else:
            sql_qry = sql_qry + ' , ' + field_groups[field_group]
        i += 1
    i = 0
    for field_equal in field_equals.keys():
        if 'date' in field_equal.lower():
            if i == 0:
                sql_qry = sql_qry + ' WHERE ' + field_equals[field_equal]
            else:
                sql_qry = sql_qry + ' AND ' + field_equals[field_equal]
            i += 1
        else:
            if i == 0:
                sql_qry = sql_qry + ' WHERE ' + field_equal + " = " + field_equals[field_equal]
            else:
                sql_qry = sql_qry + ' OR ' + field_equal + " = " + field_equals[field_equal]
            i += 1
    i = 0
    query_field = ''
    for field_aggregation in field_aggregations.keys():
        if i > 0:
            query_field = query_field + ', '
        query_field = query_field + field_aggregation + '(' + field_aggregations[field_aggregation] + ')'
        i += 1
    sql_qry = sql_qry.replace ('*', query_field )
    return sql_qry


field_equals = {'Employee_Name': "'abhishek gupta'", 'AGENT_NAME': "'abhishek gupta'"}
fields = {'PREMIUM': 'premium'}
field_aggregations = {'AVG': 'PREMIUM', 'SUM': 'PREMIUM', 'FIELD3': 'PREMIUM', 'FIELD4' : 'PREMIUM'}
field_groups = {}
print (construct_qry("AppoloTable", field_equals, fields, field_aggregations, field_groups))