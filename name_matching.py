all_names = {'Bryan' : 'Bryan H', 'Daniel' : 'Daniel T', 'Cyril' : 'Cyril M', 'Thomas' : 'Thomas F', 'Patrick' : 'Patrick Cerf',
             'Cerf' : 'Patrick Cerf', 'Jasmin' : 'Jasmin Begagic', 'Begagic' : 'Jasmin Begagic', 'Joeri' : 'Joeri Graf',
             'Graf' : 'Joeri Graf', 'Andrey' : 'Andrey kleymenov', 'Kleymenov' : 'Andrey kleymenov', 'Martin' : 'Martin N'}
found_names = []
def get_names (text):
    for name in all_names.keys():
        if name.lower() in text.lower():
            found_names.append (all_names[name])
    return set(found_names)


print (get_names("My client p. cerf, jasmin B, Bryan and Thomas F is from Los Angeles"))