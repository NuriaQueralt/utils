'''
Created on Oct 28, 2016

@author: Nuria Queralt Rosinach
@version: 1.0
@note: Module for the UMLS metathesaurus
@license: CC0
'''

from lib import abravo_lib as util

class hpo_mesh(object):
    '''
    mappings as classes in UMLS
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
        # VARIABLES
        self.umls_hpo2umls_d = {}
        self.umls_mesh2umls_d = {}
        self.inferred_hpo2mesh_d = {}
        self.inferred_mesh2hpo_d = {}
        self.hp2name_d = {}
        self.mesh2name_d = {}
    
        # ALGORITHM
        # Create hpo2umls dict from UMLS mappings
        for line in open('/home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/umls-hpo-2016aa.tsv','r').readlines():
            if line.startswith('CUI'):
                continue
            line_l = line.strip('\n').split('\t')
            cui = line_l[0]
            hp_code = line_l[2]
            hp_term = line_l[3]
            util.add_elem_with_dictionary(self.umls_hpo2umls_d, hp_code, cui)
            self.hp2name_d[hp_code] = hp_term
            
            #print('{}\t{}\t{}'.format(cui,hp_code,hp_term))
    
        # Create mesh2umls dict from UMLS mappings
        for line in open('/home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/umls-mesh-2016aa.tsv','r').readlines():
            if line.startswith('CUI'):
                continue
            line_l = line.strip('\n').split('\t')
            cui = line_l[0]
            mesh_code = line_l[2]
            mesh_term = line_l[3]
            util.add_elem_with_dictionary(self.umls_mesh2umls_d, mesh_code, cui)
            self.mesh2name_d[mesh_code] = mesh_term
            
            #print('{}\t{}\t{}'.format(cui,mesh_code,mesh_term))
            
        # Infer and create hpo2mesh dict
        for hp in self.umls_hpo2umls_d:
            hpCuis_s = set(self.umls_hpo2umls_d[hp])
            for mesh in self.umls_mesh2umls_d:
                meshCuis_s = set(self.umls_mesh2umls_d[mesh])
                if len(hpCuis_s) > len(meshCuis_s) or len(hpCuis_s) == len(meshCuis_s):
                    resta = hpCuis_s - meshCuis_s
                else:
                    resta = meshCuis_s - hpCuis_s
                if len(resta) == 0:
                    util.add_elem_with_dictionary(self.inferred_hpo2mesh_d, hp, mesh)
                    util.add_elem_with_dictionary(self.inferred_mesh2hpo_d, mesh, hp) 
                    #print('{} {} {} {} {} {} {}'.format(resta, hp, self.hp2name_d[hp],hpCuis_s, mesh,self.mesh2name_d[mesh], meshCuis_s))
                    
    def get_hp_mappings_per_mesh(self, mesh):
        return self.inferred_mesh2hpo_d.get(mesh, ['NA'])
    def get_mesh_mappings_per_hp(self, hp):
        return self.inferred_hpo2mesh_d.get(hp, ['NA'])
    def get_hp_term(self,hp):
        return self.hp2name_d.get(hp, 'NA')
    def get_mesh_term(self,mesh):
        return self.mesh2name_d.get(mesh, 'NA')
            


        
        