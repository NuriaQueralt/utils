'''
Created on Jan 24, 2017

@author: Núria Queralt Rosinach
@version: 2.0
@note: Module for the DO ontology
@license: CC0
'''

import re, sys

class term(object):
    '''
    Classes in the ontology
    '''


    def __init__(self, do_owl):
        '''
        Constructor
        '''

        # VARIABLES
        self.id = ''
        self.term = ''
        self.do2term = {}
        self.do2orpha = {}
        self.do2mesh = {}
        
        # Input
        with open(do_owl, 'r') as do_f:
            do_d = do_f.read()
        do_f.close()

        # RE patterns
        doid_pattern = re.compile(r' <owl:Class rdf:about="http://purl.obolibrary.org/obo/DOID_(.+)">')
        term_pattern = re.compile(r'<rdfs:label rdf:datatype="http://www.w3.org/2001/XMLSchema#string">(.+)</rdfs:label>')
        term_pattern2 = re.compile(r'<rdfs:label>(.+)</rdfs:label>')
        term_pattern3 = re.compile(r'<rdfs:label xml:lang="en">(.+)</rdfs:label>')
        orpha_pattern = re.compile(r'<oboInOwl:hasDbXref rdf:datatype="http://www.w3.org/2001/XMLSchema#string">ORDO:(.+)</oboInOwl:hasDbXref>')
        mesh_pattern = re.compile(r'<oboInOwl:hasDbXref rdf:datatype="http://www.w3.org/2001/XMLSchema#string">MSH:(.+)</oboInOwl:hasDbXref>')
        deprecated_pattern = re.compile(r'<owl:deprecated rdf:datatype="http://www.w3.org/2001/XMLSchema#boolean">true</owl:deprecated>')

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
            self.id = 'DOID:' + doid_match.group(1)
            
            # Obsolete terms control
            deprecated_match = deprecated_pattern.search(term)
            if deprecated_match:
                #print('deprecated: {}'.format(self.id))
                continue
            
            # term
            term_match = term_pattern.search(term)
            try:
                self.term = term_match.group(1)
            except AttributeError:
                #print('{}'.format(self.id))
                term_match = term_pattern2.search(term)
                try:
                    self.term = term_match.group(1)
                    #print('{}'.format(self.term))    
                except AttributeError:
                    #print('{}'.format(self.id))
                    term_match = term_pattern3.search(term)
                    self.term = term_match.group(1)
                    #print('{}'.format(self.term))  
            self.do2term[self.id] = self.term
 
            # Orphanet xref (mappings)
            orpha_matches = orpha_pattern.finditer(term)
            if not orpha_matches:
                continue
            orpha_l = []
            for orpha_match in orpha_matches:
                orpha_code = 'Orphanet:' + orpha_match.group(1)
                orpha_l.append(orpha_code)
                #print('{}\t{}'.format(self.id,orpha_code))
            self.do2orpha[self.id] = set(orpha_l)
    
            # MESH xref (mappings)
            mesh_matches = mesh_pattern.finditer(term)
            if not mesh_matches:
                continue
            mesh_l = []
            for mesh_match in mesh_matches:
                mesh_code = 'MESH:' + mesh_match.group(1)
                mesh_l.append(mesh_code)
                #print('{}\t{}'.format(self.id,mesh_code))
            self.do2mesh[self.id] = set(mesh_l)
            
    def get_do_term(self,doid):
        return self.do2term.get(doid, 'NA')
    def get_orphanet_mappings_per_doid(self, doid):
        return self.do2orpha.get(doid, ['NA'])
    def get_mesh_mappings_per_doid(self, doid):
        return self.do2mesh.get(doid, ['NA'])
    def print_do2mesh_mappings(self,path):
        '''Function to print doid to mesh mappings from the do ontology
           param path: /home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/
           return file: /home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/do-do2mesh-mappings.tsv
        '''
        
        # out
        mappings_f = open('{}do-do2mesh-mappings.tsv'.format(path), 'w') 
        mappings_f.write('do_code\tdo_term\tmesh_code\n'.format())
        
        for do in self.do2mesh:
            for mesh in self.do2mesh[do]:
                term = self.do2term[do]
                mappings_f.write('{}\t{}\t{}\n'.format(do,term,mesh))
        mappings_f.close()
        print('The do2mesh mappings output file is at: {}do-do2mesh-mappings.tsv. See you next time!.\n'.format(path))        
    
    
if __name__ == '__main__':

    try:
        ## Parse hp ontology (owl)
        # Path to in and out files
        owl_f = '/home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/doid.owl'
        path = '/home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/'

        ## Print mappings file
        do = term(owl_f)
        do.print_do2mesh_mappings(path)
        
    except OSError:
        print("Some problem occurred....T_T")
        sys.exit()
    
    
