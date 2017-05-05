'''
Created on Oct 28, 2016

@author: Nuria Queralt Rosinach
@version: 1.0
@note: Module for the UMLS metathesaurus
@license: CC0
'''

from lib import abravo_lib as util

def get_hpo_mesh_mappings():
    '''
    Function to infer hpo2mesh and mesh2hpo mappings from the UMLS metathesaurus
    :return: hpo2mesh_dict
    :return: mesh2hpo_dict
    :return: hp2name_dict
    :return: mesh2name_dict
    '''
    
    # VARIABLES
    umls_hpo2umls_d = {}
    umls_mesh2umls_d = {}
    inferred_hpo2mesh_d = {}
    inferred_mesh2hpo_d = {}
    hp2name_d = {}
    mesh2name_d = {}

    # ALGORITHM
    # Create hpo2umls dict from UMLS mappings
    for line in open('/home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/umls-hpo-2016aa.tsv','r').readlines():
        if line.startswith('CUI'):
            continue
        line_l = line.strip('\n').split('\t')
        cui = line_l[0]
        hp_code = line_l[2]
        hp_term = line_l[3]
        util.add_elem_with_dictionary(umls_hpo2umls_d, hp_code, cui)
        hp2name_d[hp_code] = hp_term
        
        #print('{}\t{}\t{}'.format(cui,hp_code,hp_term))

    # Create mesh2umls dict from UMLS mappings
    for line in open('/home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/umls-mesh-2016aa.tsv','r').readlines():
        if line.startswith('CUI'):
            continue
        line_l = line.strip('\n').split('\t')
        cui = line_l[0]
        mesh_code = line_l[2]
        mesh_term = line_l[3]
        util.add_elem_with_dictionary(umls_mesh2umls_d, mesh_code, cui)
        mesh2name_d[mesh_code] = mesh_term
        
        #print('{}\t{}\t{}'.format(cui,mesh_code,mesh_term))
        
    # Infer and create hpo2mesh dict
    for hp in umls_hpo2umls_d:
        hpCuis_s = set(umls_hpo2umls_d[hp])
        for mesh in umls_mesh2umls_d:
            meshCuis_s = set(umls_mesh2umls_d[mesh])
            if len(hpCuis_s) > len(meshCuis_s) or len(hpCuis_s) == len(meshCuis_s):
                resta = hpCuis_s - meshCuis_s
            else:
                resta = meshCuis_s - hpCuis_s
            if len(resta) == 0:
                util.add_elem_with_dictionary(inferred_hpo2mesh_d, hp, mesh)
                util.add_elem_with_dictionary(inferred_mesh2hpo_d, mesh, hp)
                print('{} {} {} {} {} {} {}'.format(resta, hp, hp2name_d[hp],hpCuis_s, mesh,mesh2name_d[mesh], meshCuis_s))  
                
    return inferred_hpo2mesh_d, inferred_mesh2hpo_d, hp2name_d, mesh2name_d