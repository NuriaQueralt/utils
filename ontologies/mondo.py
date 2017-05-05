'''
Created on Sep 30, 2016

@author: Nuria Queralt Rosinach
@version: 1.0
@note: Library for Mondo ontology
@license: CC0
'''

import sys, re

def owl_parser(mondo_owl):
    '''
    Owl parser for Mondo
    :return:
    '''

    # Input
    with open(mondo_owl, 'r') as mondo_f:
        mondo_d = mondo_f.read()
    mondo_f.close()

    # Variable
    doid2orpha_dct = {}

    # RE patterns
    doid_pattern = re.compile(r' <owl:Class rdf:about="http://purl.obolibrary.org/obo/DOID_(.+)">')
    orpha_pattern = re.compile(r'<owl:equivalentClass rdf:resource="http://www.orpha.net/ORDO/Orphanet_(.+)"/>')

    # Algorithm
    # Classes in chunks
    mondo_terms = mondo_d.strip().split('</rdf:RDF>')[0].split('// Classes')[1].split('<!-- ')[1:]

    # Parse chunks and extract mappings
    i=1
    l=0
    for term in mondo_terms:
        # DOID class
        if i:
            print("START\n{}\nEND\n".format(term))
            i = 0
        doid_match = doid_pattern.search(term)
        if not doid_match:
            continue
        doid_code = 'DOID:' + doid_match.group(1)
        #print("{}".format(doid_code))
        # Orphanet equivalent classes (mappings)
        orpha_matches = orpha_pattern.finditer(term)
        if not orpha_matches:
            continue
        orpha_l = []
        for orpha_match in orpha_matches:
            orpha_code = 'Orphanet:' + orpha_match.group(1)
            #print("{}\t{}".format(doid_code,orpha_code))
            orpha_l.append(orpha_code)
        doid2orpha_dct[doid_code] = orpha_l
        if len(orpha_l) > l:
            l = len(orpha_l)
    #print('{}'.format(len(doid2orpha_dct)))
    return doid2orpha_dct


if __name__ == '__main__':

    try:
        ## Save disease and drug list in tab file
        # input
        mondo_f = "/home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/mondo.owl"

        # parse owl file
        owl_parser(mondo_f)


    except OSError:
        print("Some problem occurred....T_T")
        sys.exit()