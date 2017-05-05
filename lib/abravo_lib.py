def add_elem_dictionary2(dictionary, key, elem, repet = False):
    if key in dictionary:
        aux = dictionary.get(key)
        if repet:
            aux.append(elem)
            dictionary[key] = aux
        else:   
            if not elem in aux:
                aux.append(elem)
                dictionary[key] = aux
    else:
        dictionary[key] = [elem]
    return dictionary


def add_one_dictionary2(dictionary, key):
    if key in dictionary:
        aux = dictionary.get(key)
        dictionary[key] = aux + 1
    else:
        dictionary[key] = 1
    return dictionary
    
def add_elem_with_dictionary(dictionary, key, elem, repeat = False):
    if not repeat:
        aux = dictionary.get(key, {})
        aux[elem] = 1
        dictionary[key] = aux
        return dictionary
    aux = dictionary.get(key, [])
    aux.append(elem)
    dictionary[key] = aux
    return dictionary

def add_one_dictionary(dictionary, key):
    aux = dictionary.get(key, 0)
    dictionary[key] = aux + 1
    return dictionary
