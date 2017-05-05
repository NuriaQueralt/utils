'''
Created on Sep 30, 2016

@author: Nuria Queralt Rosinach
@version: 1.0
@note: Module for the Mondo ontology
@license: CC0
'''

import re

class term(object):
    '''
    Classes in the ontology
    '''


    def __init__(self, mondo_owl):
        '''
        Constructor
        '''

        self.doid2orpha = {}
        # Input
        with open(mondo_owl, 'r') as mondo_f:
            mondo_d = mondo_f.read()
        mondo_f.close()

        # RE patterns
        doid_pattern = re.compile(r' <owl:Class rdf:about="http://purl.obolibrary.org/obo/DOID_(.+)">')
        orpha_pattern = re.compile(r'<owl:equivalentClass rdf:resource="http://www.orpha.net/ORDO/Orphanet_(.+)"/>')

        # Algorithm
        # Classes in chunks
        mondo_terms = mondo_d.strip().split('</rdf:RDF>')[0].split('// Classes')[1].split('<!-- ')[1:]

        # Parse chunks and extract mappings
        for term in mondo_terms:
            # DOID class
            doid_match = doid_pattern.search(term)
            if not doid_match:
                continue
            doid_code = 'DOID:' + doid_match.group(1)

            # Orphanet equivalent classes (mappings)
            orpha_matches = orpha_pattern.finditer(term)
            if not orpha_matches:
                continue
            orpha_l = []
            for orpha_match in orpha_matches:
                orpha_code = 'Orphanet:' + orpha_match.group(1)
                orpha_l.append(orpha_code)
            self.doid2orpha[doid_code] = set(orpha_l)

    def get_orphanet_mappings_per_doid(self, doid):
        return self.doid2orpha.get(doid, ['NA'])


