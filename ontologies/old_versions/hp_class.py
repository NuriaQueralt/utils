'''
Created on Oct 31, 2016

@author: Nuria Queralt Rosinach
@version: 1.0
@note: Module for the HPO ontology
@license: CC0
'''

import sys, re

class term(object):
    '''
    terms in the ontology as classes
    '''

    def __init__(self, hp_owl):
        '''
        Constructor
        '''
        
        # VARIABLES
        self.id = ''
        self.term = ''
        self.hp2term = {}
        self.hp2mesh = {}
        
        # Ontology file
        with open(hp_owl, 'r') as hp_f:
            hp_data = hp_f.read()
        hp_f.close()
        
        # RE PATTERNS
        hpid_pattern = re.compile(r'<owl:Class rdf:about="http://purl.obolibrary.org/obo/HP_(.+)">') 
        hpTerm_pattern = re.compile(r'<rdfs:label rdf:datatype="http://www.w3.org/2001/XMLSchema#string">(.+)</rdfs:label>')
        hpTerm_pattern2 = re.compile(r'<rdfs:label>(.+)</rdfs:label>')
        hpTerm_pattern3 = re.compile(r'<rdfs:label xml:lang="en">(.+)</rdfs:label>')
        hpDeprecated_pattern = re.compile(r'<owl:deprecated rdf:datatype="http://www.w3.org/2001/XMLSchema#boolean">true</owl:deprecated>')
        meshXref_pattern = re.compile(r'<oboInOwl:hasDbXref rdf:datatype="http://www.w3.org/2001/XMLSchema#string">MSH:(.+)</oboInOwl:hasDbXref>')
        
        # ALGORITHM
        # classes in chunks
        hp_terms = hp_data.strip().split('</rdf:RDF>')[0].split('// Classes')[1].split('<!-- ')[1:]

        # Parse chunks and extract mappings
        for term in hp_terms:
            # HPID class
            hpid_match = hpid_pattern.search(term)
            if not hpid_match:
                continue
            self.id = 'HP:' + hpid_match.group(1)
            
            hpDeprecated_match = hpDeprecated_pattern.search(term)
            if hpDeprecated_match:
                #print('deprecated: {}'.format(self.id))
                continue
            #print('{}'.format(self.id))
            hpTerm_match = hpTerm_pattern.search(term)
            try:
                self.term = hpTerm_match.group(1)
            except AttributeError:
                #print('{}'.format(self.id))
                hpTerm_match = hpTerm_pattern2.search(term)
                try:
                    self.term = hpTerm_match.group(1)
                    #print('{}'.format(self.term))    
                except AttributeError:
                    #print('{}'.format(self.id))
                    hpTerm_match = hpTerm_pattern3.search(term)
                    self.term = hpTerm_match.group(1)
                    #print('{}'.format(self.term))  
            self.hp2term[self.id] = self.term

            # Orphanet equivalent classes (mappings)
            mesh_matches = meshXref_pattern.finditer(term)
            if not mesh_matches:
                continue
            mesh_l = []
            for mesh_match in mesh_matches:
                mesh_code = 'MESH:' + mesh_match.group(1)
                mesh_l.append(mesh_code)
            self.hp2mesh[self.id] = set(mesh_l)
        
    
    def get_hp_term(self,hpid):
        return self.hp2term.get(hpid, 'NA')
    def get_mesh_mappings_per_hp(self,hpid):
        return self.hp2mesh.get(hpid, ['NA'])
    def print_hp2mesh_mappings(self,path):
        '''Function to print hp to mesh mappings from the hp ontology
           param path: /home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/
           return file: /home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/hp-hp2mesh-mappings.tsv
        '''
        
        # out
        mappings_f = open('{}hp-hp2mesh-mappings.tsv'.format(path), 'w') 
        mappings_f.write('hp_code\thp_term\tmesh_code\n'.format())
        
        for hp in self.hp2mesh:
            for mesh in self.hp2mesh[hp]:
                term = self.hp2term[hp]
                mappings_f.write('{}\t{}\t{}\n'.format(hp,term,mesh))
        mappings_f.close()
        print('The hp2mesh mappings output file is at: {}hp-hp2mesh-mappings.tsv. See you next time!.\n'.format(path))    
        
if __name__ == '__main__':

    try:
        ## Parse hp ontology (owl)
        # Path to in and out files
        owl_f = '/home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/hp.owl'
        path = '/home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/'

        ## Print mappings file
        #hp = term(owl_f)
        #hp.print_hp2mesh_mappings(path)

    except OSError:
        print("Some problem occurred....T_T")
        sys.exit()        