'''
Created on May 02, 2017

@author: Núria Queralt Rosinach
@version: 2.0
@note: Module for hetionet
@license: CC0
'''

import sys, re
#from ontologies import mondo as mondo
from ontologies import mondo_class as mondo
from ontologies import do_class as do
from ontologies import umls_class as umls
from ontologies import hp_class as hp
from lib import abravo_lib as util

def orphadata_xml_parser(parse_f,path):

    '''
    Orphanet xml disease-HPO annotation file parser
    :param parse_file: /home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/en_product4_HPO.xml
    :return associations_file: /home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/orphanet-disease-symptom.tsv
    :return diseases_file: /home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/orphanet-diseases.tsv
    :return symptoms_file: /home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/orphanet-symptoms.tsv
    '''

    # IN
    with open('{}'.format(parse_f), 'r', encoding="ISO-8859-1") as orphadata_f:
        orphadata_d = orphadata_f.read()
    orphadata_f.close()

    # OUT
    rd_sym_f = open("{}orphanet-disease-symptom.tsv".format(path), 'w')
    sym_f = open("{}orphanet-symptoms.tsv".format(path), 'w')
    rd_f = open("{}orphanet-diseases.tsv".format(path), 'w')

    # RE PATTERNS
    rd_orphaNum_pattern = re.compile(r'<OrphaNumber>(.+)</OrphaNumber>\n')
    rd_name_pattern = re.compile(r'<Name lang="en">(.+)</Name>')
    sym_id_pattern = re.compile(r'<HPOId>HP:(\d+)</HPOId>\n')
    sym_term_pattern = re.compile(r'<HPOTerm>(.+)</HPOTerm>\n')

    # VARIABLES
    rd2name_dct = {}
    rd2symId_dct = {}
    rd2symTerm_dct = {}
    sym_dct = {}

    # ALGORITHM
    association_l = orphadata_d.split('</Disorder>')
    for rd in association_l:
        rd_match = rd_orphaNum_pattern.search(rd)
        if not rd_match:
            continue
        rd_orphaNum = rd_match.group(1)
        rd_name_match = rd_name_pattern.search(rd)
        rd_name = rd_name_match.group(1)
        rd2name_dct[rd_orphaNum] = rd_name
        sym_id_matches = sym_id_pattern.finditer(rd)
        sym_id_l = []
        for sym_id_match in sym_id_matches:
            sym_id = 'HP:' + sym_id_match.group(1)
            sym_id_l.append(sym_id)
        sym_term_matches = sym_term_pattern.finditer(rd)
        sym_term_l = []
        for sym_term_match in sym_term_matches:
            sym_term = sym_term_match.group(1)
            sym_term_l.append(sym_term)
        rd2symId_dct[rd_orphaNum] = sym_id_l
        rd2symTerm_dct[rd_orphaNum] = sym_term_l

    # Write association file
    rd_sym_f.write('orphanet_code\torphanet_term\thp_code\thp_term\n')
    for rd in rd2name_dct:
        for idx in range(len((rd2symId_dct[rd]))):
            if len(rd2symId_dct[rd]) == 0:
                rd2symId_dct[rd][idx] = None
                rd2symTerm_dct[rd][idx] = None
            rd_sym_f.write('Orphanet:{}\t{}\t{}\t{}\n'.format(rd,rd2name_dct[rd],rd2symId_dct[rd][idx],rd2symTerm_dct[rd][idx]))
            sym_dct[rd2symId_dct[rd][idx]] = rd2symTerm_dct[rd][idx]

    # Write symptoms file
    sym_f.write('hp_code\thp_term\n')
    for sym in sym_dct:
        sym_f.write('{}\t{}\n'.format(sym,sym_dct[sym]))

    # Write diseases file
    rd_f.write('orphanet_code\torphanet_term\n')
    for rd in rd2name_dct:
        rd_f.write('Orphanet:{}\t{}\n'.format(rd,rd2name_dct[rd]))

    # CLOSE
    rd_sym_f.close()
    sym_f.close()
    rd_f.close()

def map_mondo_orpha2do(path):
    '''
        Function to map disease identifiers from Orphanumber to DOID using MONDO extracted mappings
        :param file: /home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/orphanet-disease-symptom.tsv
        :return file: /home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/mondo-orpha2do-mappings.tsv
        :return file: /home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/orphanet-mondo-doid_orphanum-hp.tsv
        :return file: /home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/orphanet-diseases-mondo-orpha2do.tsv
    '''
    
    # IN
    orphaDisPhe_p = '/home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/orphanet-disease-symptom.tsv'
    with open('{}'.format(orphaDisPhe_p), 'r') as orphaDisPhe_f:
        orphaDisPhe_l = orphaDisPhe_f.readlines()
    orphaDisPhe_f.close()
    
    # OUT
    rd_sym_f = open("{}orphanet-mondo-doid_orphanum-hp.tsv".format(path), 'w')
    rd_sym_f.write('orphanet_code\tmondo_do:orphanet_cardinality\tmondo_do_mapping\torphanet_term\thp_code\thp_term\n')
    rd_mappings_f = open("{}mondo-orpha2do-mappings.tsv".format(path,), 'w')
    rd_mappings_f.write("orphanet\tdo\n")
    orpha_mappings_f = open("{}orphanet-diseases-mondo-orpha2do.tsv".format(path,), 'w')
    orpha_mappings_f.write('orphanumber\tdoid\n')
    
    # VARIABLES
    orpha2do_dct = {}
    mondo_orpha_dct = {}
    orpha_orpha_dct = {}
    
    # ALGORITHM
    # import mondo doid2orpha mappings dictionary
    mondo_owl = "/home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/mondo.owl"
    #mondo_dct = mondo.owl_parser(mondo_owl)
    mondo_term = mondo.term(mondo_owl)
    mondo_do2orpha_dct = mondo_term.doid2orpha
    #mondo_do2orpha_dct = mondo_term.get_orphanet_mappings_per_doid(doid)
    
    # define reverse mappings, orpha to do
    for doid,orphanumber_l in mondo_do2orpha_dct.items():
        for orpha in orphanumber_l:
            util.add_elem_with_dictionary(orpha2do_dct, orpha, doid)
            mondo_orpha_dct[orpha] = 1

    # write down the mondo mappings orpha2do
    for orpha in orpha2do_dct:
        for key in orpha2do_dct[orpha].keys():
            rd_mappings_f.write("{}\t{}\n".format(orpha, key))
    
    # map orphanet rare diseases from orphanumber to doid
    for line in orphaDisPhe_l:
        if line.startswith('orphanet_code'):
            continue
        line_l = line.strip('\n').split('\t')
        orpha_id = line_l[0]
        #------------------------------------------------ orpha_name = line_l[1]
        #----------------------------------------------------- hp_id = line_l[2]
        #--------------------------------------------------- hp_name = line_l[3]
        orpha_orpha_dct[orpha_id] = 1
        if not orpha_id in orpha2do_dct:
            mapping_cardinality = 0
            disease_id = orpha_id
            rd_sym_f.write('{}\t1:{}\t{}\t{}\t{}\t{}\n'.format(line_l[0],mapping_cardinality,disease_id,line_l[1],line_l[2],line_l[3]))
        else:
            doid_l = list(orpha2do_dct[orpha_id].keys())
            mapping_cardinality = len(doid_l)
            if len(doid_l) > 1:
                print('orpha_id: {} has more than one doid'.format(orpha_id))
            for disease_id in doid_l:
                rd_sym_f.write('{}\t1:{}\t{}\t{}\t{}\t{}\n'.format(line_l[0],mapping_cardinality,disease_id,line_l[1],line_l[2],line_l[3]))
                
    for orpha in orpha_orpha_dct: 
        if orpha in orpha2do_dct:           
            for doid in orpha2do_dct[orpha].keys():
                orpha_mappings_f.write('{}\t{}\n'.format(orpha, doid))
        
    # close files
    rd_sym_f.close()
    rd_mappings_f.close()
    orpha_mappings_f.close()
    
    mondo_orpha_set = set(mondo_orpha_dct.keys())
    orpha_orpha_set = set(orpha_orpha_dct.keys())
    print('From mondo, "equivalentClass" mappings DO to Orphanet:')
    print('orphanet_orpha: {}; mondo_orpha: {} OrphaNumbers'.format(len(orpha_orpha_set),len(mondo_orpha_set)))
    commons = list(mondo_orpha_set & orpha_orpha_set)
    differs = list(orpha_orpha_set - mondo_orpha_set)
    print('mapped: {}'.format(len(commons)))
    commons_h = commons[0:4]
    print('mapped: {}'.format(commons_h))
    print('not mapped: {}'.format(len(differs)))
    differs_h = differs[0:4]
    print('not mapped: {}'.format(differs_h))
    
def map_do_orpha2do(path):
    '''
        Function to map disease identifiers from Orphanumber to DOID using DO extracted mappings
        :param file: /home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/orphanet-disease-symptom.tsv
        :return file: /home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/do-orpha2do-mappings.tsv
        :return file: /home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/orphanet-do-doid_orphanum-hp.tsv
        :return file: /home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/orphanet-diseases-do-orpha2do.tsv
    '''
    
    # IN
    orphaDisPhe_p = '/home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/orphanet-disease-symptom.tsv'
    with open('{}'.format(orphaDisPhe_p), 'r') as orphaDisPhe_f:
        orphaDisPhe_l = orphaDisPhe_f.readlines()
    orphaDisPhe_f.close()
    
    # OUT
    rd_sym_f = open("{}orphanet-do-doid_orphanum-hp.tsv".format(path), 'w')
    rd_sym_f.write('orphanet_code\tdo_do:orphanet_cardinality\tdo_do_mapping\torphanet_term\thp_code\thp_term\n')
    rd_mappings_f = open("{}do-orpha2do-mappings.tsv".format(path,), 'w')
    rd_mappings_f.write("orphanet\tdo\n")
    orpha_mappings_f = open("{}orphanet-diseases-do-orpha2do.tsv".format(path,), 'w')
    orpha_mappings_f.write('orphanumber\tdoid\n')
    
    # VARIABLES
    orpha2do_dct = {}
    do_orpha_dct = {}
    orpha_orpha_dct = {}
    
    # ALGORITHM
    # import do doid2orpha mappings dictionary
    do_owl = "/home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/doid.owl"
    do_term = do.term(do_owl)
    do_do2orpha_dct = do_term.do2orpha
    
    # define reverse mappings, orpha to do
    for doid,orphanumber_l in do_do2orpha_dct.items():
        for orpha in orphanumber_l:
            util.add_elem_with_dictionary(orpha2do_dct, orpha, doid)
            do_orpha_dct[orpha] = 1

    # write down the do mappings orpha2do
    for orpha in orpha2do_dct:
        for key in orpha2do_dct[orpha].keys():
            rd_mappings_f.write("{}\t{}\n".format(orpha, key))
    
    # map orphanet rare diseases from orphanumber to doid
    for line in orphaDisPhe_l:
        if line.startswith('orphanet_code'):
            continue
        line_l = line.strip('\n').split('\t')
        orpha_id = line_l[0]
        #------------------------------------------------ orpha_name = line_l[1]
        #----------------------------------------------------- hp_id = line_l[2]
        #--------------------------------------------------- hp_name = line_l[3]
        orpha_orpha_dct[orpha_id] = 1
        if not orpha_id in orpha2do_dct:
            mapping_cardinality = 0
            disease_id = orpha_id
            rd_sym_f.write('{}\t1:{}\t{}\t{}\t{}\t{}\n'.format(line_l[0],mapping_cardinality,disease_id,line_l[1],line_l[2],line_l[3]))
        else:
            doid_l = list(orpha2do_dct[orpha_id].keys())
            mapping_cardinality = len(doid_l)
            if len(doid_l) > 1:
                print('orpha_id: {} has more than one doid'.format(orpha_id))
            for disease_id in doid_l:
                rd_sym_f.write('{}\t1:{}\t{}\t{}\t{}\t{}\n'.format(line_l[0],mapping_cardinality,disease_id,line_l[1],line_l[2],line_l[3]))
                
    for orpha in orpha_orpha_dct: 
        if orpha in orpha2do_dct:           
            for doid in orpha2do_dct[orpha].keys():
                orpha_mappings_f.write('{}\t{}\n'.format(orpha, doid))
        
    # close files
    rd_sym_f.close()
    rd_mappings_f.close()
    orpha_mappings_f.close()
    
    do_orpha_set = set(do_orpha_dct.keys())
    orpha_orpha_set = set(orpha_orpha_dct.keys())
    print("")
    print('From do, "xref" mappings DO to Orphanet:')
    print('orphanet_orpha: {}; do_orpha: {} OrphaNumbers'.format(len(orpha_orpha_set),len(do_orpha_set)))
    commons = list(do_orpha_set & orpha_orpha_set)
    differs = list(orpha_orpha_set - do_orpha_set)
    print('mapped: {}'.format(len(commons)))
    commons_h = commons[0:4]
    print('mapped: {}'.format(commons_h))
    print('not mapped: {}'.format(len(differs)))
    differs_h = differs[0:4]
    print('not mapped: {}'.format(differs_h))

def map_umls_hpo2mesh(path):
    '''
    Function to map symptom identifiers from HPO to MESH using the inferred mappings from the UMLS
    :param file: /home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/orphanet-symptoms.tsv
    :return: file: /home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/orphanet-symptoms-umls2016aa-hp_mesh.tsv
    '''

    # IN
    orphaPhe_p = '/home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/orphanet-symptoms.tsv'
    with open('{}'.format(orphaPhe_p), 'r') as orphaPhe_f:
        orphaPhe_l = orphaPhe_f.readlines()
    orphaPhe_f.close()

    # OUT
    mappings_f = open("{}umls2016aa-hp2mesh-mappings.tsv".format(path), "w")
    mappings_f.write('hp_code\thp_term\tmesh_code\tmesh_term\n')
    sym_f = open("{}orphanet-symptoms-umls2016aa-hp_mesh.tsv".format(path), 'w')
    sym_f.write('hp_code\thp_term\tmesh_code\tmesh_term\n')

    # VARIABLES
    sym_hpTotal_dct = {}
    sym_hpMapped_dct = {}
    sym_mshMapped_dct = {}
    
    # ALGORITHM
    # mappings from the umls (inferred)   
    umls_mappings = umls.hpo_mesh()
    for hp in umls_mappings.inferred_hpo2mesh_d:
        hp_name = umls_mappings.get_hp_term(hp)
        for mesh in umls_mappings.get_mesh_mappings_per_hp(hp):
            mesh_name = umls_mappings.get_mesh_term(mesh)
            mappings_f.write('{}\t{}\t{}\t{}\n'.format(hp,hp_name,mesh,mesh_name))
          
    # write output file
    for line in orphaPhe_l:
        if line.startswith('hp_code'):
            continue
        line_l = line.strip('\n').split('\t')
        hp_code = line_l[0]
        hp_term = line_l[1]
        sym_hpTotal_dct[hp_code] = 1
        mesh_code_l = umls_mappings.get_mesh_mappings_per_hp(hp_code)
        for mesh_code in mesh_code_l:
            mesh_term = umls_mappings.get_mesh_term(mesh_code)
            #print('{}\t{}\t{}\t{}'.format(hp_code, hp_term, mesh_code, mesh_term))
            sym_f.write('{}\t{}\t{}\t{}\n'.format(hp_code, hp_term, mesh_code, mesh_term))
            if mesh_code != 'NA':
                sym_hpMapped_dct[hp_code] = 1
                sym_mshMapped_dct[mesh_code] = 1
                #print('{}\t{}'.format(hp_code, mesh_code))
    
    # close files    
    mappings_f.close()
    sym_f.close()
    
    # prints
    print('### Results UMLS mappings:')
    print('The total number of symptoms in orphanet (hp): {}'.format(len(sym_hpTotal_dct)))
    print('The total number of symptoms mapped (hp): {}'.format(len(sym_hpMapped_dct)))
    print('The total number of symptoms in orphanet (msh): {}'.format(len(sym_mshMapped_dct)))
    
def map_hpo_hpo2mesh(path):
    '''
    Function to map symptom identifiers from HPO to MESH using the inferred mappings from the HPO
    :param file: /home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/orphanet-symptoms.tsv
    :return: file: /home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/orphanet-symptoms-hpo-hp_mesh.tsv
    '''

    # IN
    orphaPhe_p = '/home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/orphanet-symptoms.tsv'
    with open('{}'.format(orphaPhe_p), 'r') as orphaPhe_f:
        orphaPhe_l = orphaPhe_f.readlines()
    orphaPhe_f.close()

    # OUT
    sym_f = open("{}orphanet-symptoms-hpo-hp_mesh.tsv".format(path), 'w')
    sym_f.write('hp_code\thp_term\tmesh_code\n')

    # VARIABLES
    sym_hpTotal_dct = {}
    sym_hpMapped_dct = {}
    sym_mshMapped_dct = {}
    
    # ALGORITHM
    # mappings from the hpo (defined classes)   
    owl_f = '/home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/hp.owl'
    hpo_term = hp.term(owl_f)
    hpo_term.print_hp2mesh_mappings(path)
          
    # write output file
    for line in orphaPhe_l:
        if line.startswith('hp_code'):
            continue
        line_l = line.strip('\n').split('\t')
        hp_code = line_l[0]
        hp_term = line_l[1]
        sym_hpTotal_dct[hp_code] = 1
        mesh_code_l = hpo_term.get_mesh_mappings_per_hp(hp_code)
        for mesh_code in mesh_code_l:
            sym_f.write('{}\t{}\t{}\n'.format(hp_code, hp_term, mesh_code))
            if mesh_code != 'NA':
                sym_hpMapped_dct[hp_code] = 1
                sym_mshMapped_dct[mesh_code] = 1
                #print('{}\t{}'.format(hp_code, mesh_code))
    
    # close files    
    sym_f.close()
    
    # prints
    print('### Results HPO mappings:')
    print('The total number of symptoms in orphanet (hp): {}'.format(len(sym_hpTotal_dct)))
    print('The total number of symptoms mapped (hp): {}'.format(len(sym_hpMapped_dct)))
    print('The total number of symptoms in orphanet (msh): {}'.format(len(sym_mshMapped_dct)))
    

if __name__ == '__main__':

    try:
        ## Parse rare disease - HPO annotation file (xml)
        # Path to in and out files
        orphadata_f = '/home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/en_product4_HPO.xml'
        path = '/home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/'

        ## Parse Orphadata XML rd-hpo annotation file
        #orphadata_xml_parser(orphadata_f,path)

        ## Map orphanet diseases to DO (MONDO mappings)
        #map_mondo_orpha2do(path)
        
        ## Map orphanet diseases to DO (DO)
        #map_do_orpha2do(path)

        ## Map orphanet symptoms from HPO to MESH (UMLS)
        #map_umls_hpo2mesh(path)

        ## Map orphanet symptoms from HPO to MESH (HPO)
        #map_hpo_hpo2mesh(path)

    except OSError:
        print("Some problem occurred....T_T")
        sys.exit()
