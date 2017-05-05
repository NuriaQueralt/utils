'''
Created on Nov 23, 2016

@author: Nuria Queralt Rosinach
@version: 1.0
@note: Module for the DO ontology
@license: CC0
'''

import re

class term(object):
    '''
    Classes in the ontology
    '''


    def __init__(self, do_owl):
        '''
        Constructor
        '''

        self.doid2orpha = {}
        # Input
        with open(do_owl, 'r') as do_f:
            do_d = do_f.read()
        do_f.close()

        # RE patterns
        doid_pattern = re.compile(r' <owl:Class rdf:about="http://purl.obolibrary.org/obo/DOID_(.+)">')
        orpha_pattern = re.compile(r'<oboInOwl:hasDbXref rdf:datatype="http://www.w3.org/2001/XMLSchema#string">ORDO:(.+)</oboInOwl:hasDbXref>')

        # Algorithm
        # Classes in chunks
        do_terms = do_d.strip().split('</rdf:RDF>')[0].split('// Classes')[1].split('<!-- ')[1:]

        # Parse chunks and extract mappings
        for term in do_terms:
            #print('{}'.format(term))
            # DOID class
            doid_match = doid_pattern.search(term)
            if not doid_match:
                continue
            doid_code = 'DOID:' + doid_match.group(1)
 
            # Orphanet xref (mappings)
            orpha_matches = orpha_pattern.finditer(term)
            if not orpha_matches:
                continue
            orpha_l = []
            for orpha_match in orpha_matches:
                orpha_code = 'Orphanet:' + orpha_match.group(1)
                orpha_l.append(orpha_code)
                #print('{}\t{}'.format(doid_code,orpha_code))
            self.doid2orpha[doid_code] = set(orpha_l)
 
    def get_orphanet_mappings_per_doid(self, doid):
        return self.doid2orpha.get(doid, ['NA'])
    
