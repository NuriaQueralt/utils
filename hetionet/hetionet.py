'''
Created on Aug 16, 2016

@author: Nuria Queralt Rosinach
@version: 1.0
@note: Module for hetionet
@license: CC0
'''

import json, sys, re
from pprint import pprint
from scipy.weave.ast_tools import name_pattern

def json2tab(nodeType):
    '''
    Parsing json files for compound and disease data characterization extracted from hetionet v2.0
    '''
    if (nodeType == 'Disease'):
        # input
        with open('/home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/Characterization-Disease-Drug-Scope-of-hetio/in/diseases.json') as diseases_file:
            diseases_json = json.load(diseases_file)
        diseases_file.close()
        
            
        # output
        doid_outfile = open('/home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/Characterization-Disease-Drug-Scope-of-hetio/out/hetionet-doids-list.tab', 'w')
        disease_outfile = open('/home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/Characterization-Disease-Drug-Scope-of-hetio/out/hetionet-diseases-list.tab', 'w')
        
        # algorithm
        for obj_list in diseases_json['data']:
            for row_list in obj_list['row']:
                disease_outfile.write('{}\t{}\n'.format(row_list['identifier'],row_list['name']))
                doid_outfile.write('{}\n'.format(row_list['identifier']))
                
        # close files
        disease_outfile.close()
        doid_outfile.close()
    elif (nodeType == 'Compound'):
        # input
        with open('/home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/Characterization-Disease-Drug-Scope-of-hetio/in/drugs.json') as drugs_file:
            drugs_json = json.load(drugs_file)
        drugs_file.close()
        
            
        # output
        drugbankid_outfile = open('/home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/Characterization-Disease-Drug-Scope-of-hetio/out/hetionet-drugbankids-list.tab', 'w')
        drug_outfile = open('/home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/Characterization-Disease-Drug-Scope-of-hetio/out/hetionet-drugs-list.tab', 'w')
        
        # algorithm
        for obj_list in drugs_json['data']:
            for row_list in obj_list['row']:
                drug_outfile.write('{}\t{}\n'.format(row_list['identifier'],row_list['name']))
                drugbankid_outfile.write('{}\n'.format(row_list['identifier']))
                
        # close files
        drugbankid_outfile.close()
        drug_outfile.close()
    else:
         print('This node type is still not parseable by the API.')   
        
    return None

def get_do_ontologyOBOChildParent(in_path,out_path,in_file):
    '''Script to extract Child-is_a-Parent relations for iGraph.
    Input: in_path (path to input), out_path (path to output), in_file (DO obo ontology file)
    Output: 'do_ontologyChildParent.tab' (file for R)'''
    
    # IN
    with open('{}{}'.format(in_path,in_file), 'r') as obo_file:
        obo_data = obo_file.read()
    obo_file.close() 
    
    # OUT
    out_name = "do_ontologyChildParent.tab"
    out_file = open("{}{}".format(out_path,out_name),'w')
    
    # VARIABLES
    rel_dict = {} # key => [id, alt_id], value => [id, alt_id list]
    parent2name_dict = {} # k => doid, v => name
    
    # RE PATTERNS
    id_pattern = re.compile(r'id: (DOID:\d+)\n')
    is_a_pattern = re.compile(r'is_a: (DOID:\d+) ! (.+)\n')
    
    # ALGORITHM
    term_list = obo_data.strip('\n').split('ontology: doid')[1].split('[Typedef]')[0].split('[Term]')[1:] # [0] is a \n line
    for term in term_list:
        child_match = id_pattern.search(term)
        if child_match:
            child_id = child_match.group(1)
            match = re.search('is_obsolete:', term)
            if match:
                continue    
            parent_matches = is_a_pattern.finditer(term)
            if parent_matches:
                parents_list = []
                for parent in parent_matches:
                    parent_id = parent.group(1)
                    parent_name = parent.group(2)
                    # Write ontology is-a relations
                    out_file.write("{}\t{}\n".format(child_id,parent_id))
                    parents_list.append(parent_id)
                    parent2name_dict[parent_id] = parent_name   
                rel_dict[child_id] = parents_list
                             
            
    # CLOSE   
    out_file.close()
    
    return None

def get_do_ontologyOBOBranch(in_path,out_path,in_file):
    '''Script to extract branches of the DO ontology.
    Input: in_path (path to input), out_path (path to output), in_file (DO obo ontology file)
    Output: 'do_ontology1rstBranchParents.tab' (file for R)'''
    
    # IN
    with open('{}{}'.format(in_path,in_file), 'r') as obo_file:
        obo_data = obo_file.read()
    obo_file.close() 
    
    # OUT
#    out_name = "do_ontology1rstBranchParents.tab"
    out_name = "do_ontology1rstBranchParents.tab"
    out_file = open("{}{}".format(out_path,out_name),'w')
    
    # VARIABLES
    rel_dict = {} # key => [id, alt_id], value => [id, alt_id list]
    branch2name_dict = {} # k => doid, v => name
    
    # RE PATTERNS
    id_pattern = re.compile(r'id: (DOID:\d+)\n')
    name_pattern = re.compile(r'name: (.+)\n')
    is_a_pattern = re.compile(r'is_a: DOID:4 ! (.+)\n')
    
    # ALGORITHM
    term_list = obo_data.strip('\n').split('ontology: doid')[1].split('[Typedef]')[0].split('[Term]')[1:] # [0] is a \n line
    
    for term in term_list:
        child_match = id_pattern.search(term)
        if child_match:
            child_id = child_match.group(1)
            child_match = name_pattern.search(term)
            if not child_match:
                child_name = 'NA'
            else:
                child_name = child_match.group(1)
            parent_match = is_a_pattern.search(term)
            if parent_match:
                parent_name = parent_match.group(1)
                # Write ontology is-a relations
                out_file.write("{}\t{}\n".format(child_id,child_name))                
                branch2name_dict[child_id] = child_name
    rel_dict['DOID:4'] = parent_name                            
            
    # CLOSE   
    out_file.close()
    
    return None

def get_activeDO(in_path,out_path,in_file, obsolete_continue = True):
    '''Script to get all active classes in the DO ontology.
    Input: in_path, out_path (path to input and output, respectively), in_file (DO obo file)
    Output: ''allActIdDOOntology.tab' (list of DOID (ppal id) in DO obo file).'''
    
    # IN
    with open('%s%s'%(in_path,in_file), 'r') as obo_file:
        obo_data = obo_file.read()
    obo_file.close() 
    
    # OUT
#    out_name = "allMergedDiseases2ICD.tab"
#    out_file = open("%s%s"%(out_path,out_name),'w')
    
    # VARIABLES
    alt_id_dict = {}
    xref_dict = {}
    do_alldoid_dict = {} # all doid to name, where all doid = active + obsolete + alt terms
    do_name_dict = {} # all doid to name, where all doid = active + obsolete terms
    do_alt_id_dict = {} # only alt_id from all, active and obsolete
    do_obsolete_dict = {} # only obsolete
    do_xref_dict = {} # active terms to xref
    do_xref_tag_dict = {} # all unique vocabularies that DO mapped  
    
    # RE PATTERNS
    id_pattern = re.compile(r'id: (DOID:\d+)\n')
    name_pattern = re.compile(r'name: (.+)\n')
    alt_id_pattern = re.compile(r'alt_id: (DOID:\d+)\n')
    xref_pattern = re.compile(r'xref: (.+)\n')
    
    # ALGORITHM                       
    # Save DO terms from the ontology
    term_list = obo_data.strip('\n').split('ontology: doid')[1].split('[Typedef]')[0].split('[Term]')[1:]
    for term in term_list:
        doid_match = id_pattern.search(term)
        if doid_match:  
            doid = doid_match.group(1)
            do_alldoid_dict[doid] = 1
            xref_list = []
            xref_dict[doid] = xref_list      
            name_match = name_pattern.search(term)
            if not name_match:
                name = 'NA'
            else:
                name = name_match.group(1)
            do_name_dict[doid] = name
            alt_id_matches = alt_id_pattern.finditer(term)
            alt_id_list = []
            for alt_id_match in alt_id_matches:
                alt_id = alt_id_match.group(1)
                do_alt_id_dict[alt_id] = 1
                do_alldoid_dict[alt_id] = 1
                xref_dict[alt_id] = xref_list
                alt_id_list.append(alt_id)
            alt_id_dict[doid] = alt_id_list        
            obsolete_match = re.search('is_obsolete:',term)
            if obsolete_match:
                do_obsolete_dict[doid] = 1
                if obsolete_continue:
                    continue
            xref_matches = xref_pattern.finditer(term)
            xref_list = []
            for xref_match in xref_matches:
                xref_id = xref_match.group(1)
                do_xref_tag = xref_id.split(":")[0]
                do_xref_tag_dict[do_xref_tag] = 1
                xref_list.append(xref_id)
            xref_dict[doid] = xref_list
            do_xref_dict[doid] = xref_list
            if alt_id_dict[doid]:
                for alt_id in alt_id_dict[doid]:
                    xref_dict[alt_id] = xref_list  
                    
    with open('%sallActIdDOOntology.tab' % out_path, 'w') as doontology_file:
        for disease in do_xref_dict:
            doontology_file.write("%s\n" % (disease))
    doontology_file.close()                                       
            
    # CLOSE   
#    out_file.close()
    
    return None

def get_chebi_ontologyOBOChildParent(in_path,out_path,in_file):
    '''Script to extract Child-is_a-Parent relations for iGraph.
    Input: in_path (path to input), out_path (path to output), in_file (ChEBI obo ontology file)
    Output: 'chebi_ontologyChildParent.tab' (file for R)'''
    
    # IN
    with open('{}{}'.format(in_path,in_file), 'r') as obo_file:
        obo_data = obo_file.read()
    obo_file.close() 
    
    # OUT
    out_name = "chebi_ontologyChildParent.tab"
    out_file = open("{}{}".format(out_path,out_name),'w')
    
    # VARIABLES
    rel_dict = {} # key => [id, alt_id], value => [id, alt_id list]
    parent2name_dict = {} # k => chebi, v => name
    
    # RE PATTERNS
    id_pattern = re.compile(r'id: (CHEBI:\d+)\n')
    is_a_pattern = re.compile(r'is_a: (CHEBI:\d+) ! (.+)\n')
    
    # ALGORITHM
    term_list = obo_data.strip('\n').split('ontology: chebi')[1].split('[Typedef]')[0].split('[Term]')[1:] # [0] is a \n line
    for term in term_list:
        child_match = id_pattern.search(term)
        if child_match:
            child_id = child_match.group(1)
            match = re.search('is_obsolete:', term)
            if match:
                continue    
            parent_matches = is_a_pattern.finditer(term)
            if parent_matches:
                parents_list = []
                for parent in parent_matches:
                    parent_id = parent.group(1)
                    parent_name = parent.group(2)
                    # Write ontology is-a relations
                    out_file.write("{}\t{}\n".format(child_id,parent_id))
                    parents_list.append(parent_id)
                    parent2name_dict[parent_id] = parent_name   
                rel_dict[child_id] = parents_list
                             
            
    # CLOSE   
    out_file.close()
    
    return None

def get_chebi_ontologyOBOBranch(in_path,out_path,in_file):
    '''Script to extract branches of the ChEBI ontology.
    Input: in_path (path to input), out_path (path to output), in_file (ChEBI obo ontology file)
    Output: 'chebi_ontology1rstBranchParents.tab' (file for R)'''
    
    # IN
    with open('{}{}'.format(in_path,in_file), 'r') as obo_file:
        obo_data = obo_file.read()
    obo_file.close() 
    
    # OUT
#    out_name = "do_ontology1rstBranchParents.tab"
    out_name = "chebi_ontology1rstBranchParents.tab"
    out_file = open("{}{}".format(out_path,out_name),'w')
    
    # VARIABLES
    rel_dict = {} # key => [id, alt_id], value => [id, alt_id list]
    branch2name_dict = {} # k => doid, v => name
    
    # RE PATTERNS
    id_pattern = re.compile(r'id: (CHEBI:\d+)\n')
    name_pattern = re.compile(r'name: (.+)\n')
    is_a_pattern = re.compile(r'is_a: CHEBI:36342 ! (.+)\n')
    
    # ALGORITHM
    term_list = obo_data.strip('\n').split('ontology: chebi')[1].split('[Typedef]')[0].split('[Term]')[1:] # [0] is a \n line
    
    for term in term_list:
        child_match = id_pattern.search(term)
        if child_match:
            child_id = child_match.group(1)
            child_match = name_pattern.search(term)
            if not child_match:
                child_name = 'NA'
            else:
                child_name = child_match.group(1)
            parent_match = is_a_pattern.search(term)
            if parent_match:
                parent_name = parent_match.group(1)
                # Write ontology is-a relations
                out_file.write("{}\t{}\n".format(child_id,child_name))                
                branch2name_dict[child_id] = child_name
    rel_dict['CHEBI:36342'] = parent_name                            
            
    # CLOSE   
    out_file.close()
    
    return None

def get_activeChEBI(in_path,out_path,in_file, obsolete_continue = True):
    '''Script to get all active classes in the ChEBI ontology.
    Input: in_path, out_path (path to input and output, respectively), in_file (ChEBI obo file)
    Output: ''allActIdCHEBIOntology.tab' (list of CHEBI (ppal id) in CHEBI obo file).'''
    
    # IN
    with open('%s%s'%(in_path,in_file), 'r') as obo_file:
        obo_data = obo_file.read()
    obo_file.close() 
    
    # OUT
#    out_name = "allMergedDiseases2ICD.tab"
#    out_file = open("%s%s"%(out_path,out_name),'w')
    
    # VARIABLES
    alt_id_dict = {}
    xref_dict = {}
    do_alldoid_dict = {} # all doid to name, where all doid = active + obsolete + alt terms
    do_name_dict = {} # all doid to name, where all doid = active + obsolete terms
    do_alt_id_dict = {} # only alt_id from all, active and obsolete
    do_obsolete_dict = {} # only obsolete
    do_xref_dict = {} # active terms to xref
    do_xref_tag_dict = {} # all unique vocabularies that DO mapped  
    
    # RE PATTERNS
    id_pattern = re.compile(r'id: (CHEBI:\d+)\n')
    name_pattern = re.compile(r'name: (.+)\n')
    alt_id_pattern = re.compile(r'alt_id: (CHEBI:\d+)\n')
    xref_pattern = re.compile(r'xref: (.+)\n')
    
    # ALGORITHM                       
    # Save DO terms from the ontology
    term_list = obo_data.strip('\n').split('ontology: chebi')[1].split('[Typedef]')[0].split('[Term]')[1:]
    for term in term_list:
        doid_match = id_pattern.search(term)
        if doid_match:  
            doid = doid_match.group(1)
            do_alldoid_dict[doid] = 1
            xref_list = []
            xref_dict[doid] = xref_list      
            name_match = name_pattern.search(term)
            if not name_match:
                name = 'NA'
            else:
                name = name_match.group(1)
            do_name_dict[doid] = name
            alt_id_matches = alt_id_pattern.finditer(term)
            alt_id_list = []
            for alt_id_match in alt_id_matches:
                alt_id = alt_id_match.group(1)
                do_alt_id_dict[alt_id] = 1
                do_alldoid_dict[alt_id] = 1
                xref_dict[alt_id] = xref_list
                alt_id_list.append(alt_id)
            alt_id_dict[doid] = alt_id_list        
            obsolete_match = re.search('is_obsolete:',term)
            if obsolete_match:
                do_obsolete_dict[doid] = 1
                if obsolete_continue:
                    continue
            xref_matches = xref_pattern.finditer(term)
            xref_list = []
            for xref_match in xref_matches:
                xref_id = xref_match.group(1)
                do_xref_tag = xref_id.split(":")[0]
                do_xref_tag_dict[do_xref_tag] = 1
                xref_list.append(xref_id)
            xref_dict[doid] = xref_list
            do_xref_dict[doid] = xref_list
            if alt_id_dict[doid]:
                for alt_id in alt_id_dict[doid]:
                    xref_dict[alt_id] = xref_list  
                    
    with open('%sallActIdCHEBIOntology.tab' % out_path, 'w') as doontology_file:
        for disease in do_xref_dict:
            doontology_file.write("%s\n" % (disease))
    doontology_file.close()                                       
            
    # CLOSE   
#    out_file.close()
    
    return None

def parser(parse_file, out_path, database = "drugbank", ext = "xml"):
    """
    General parser distributor.
    """
    
    # VARIABLES
    database_parsers_dict = {}
    
    
    # PARSERS
    database_parsers_dict['drugbank'] = ['xml']
    
    
    # ALGORITHM
    database = database.lower()
    ext = ext.lower()
    if database == "drugbank":
        parsers_list = database_parsers_dict[database]
        if ext == "xml":
            db2chebi_dict, db2atc_parents_dict = drugbank_xml_parser(parse_file, out_path, database, ext)
        else:
            print("The entered '{}' database does not have a parser yet for the entered '{}' format.".format(database, ext))
            print("The parsers for {} are for {} formats. Sorry for the inconveniences.".format(database, parsers_list))
    else:
        print("The entered '{}' database is not in the parsers' library. Try it again.".format(database, ext))
        
    return db2chebi_dict, db2atc_parents_dict    
    
def drugbank_xml_parser(parse_file, out_path, database, ext):
    """
    drugbank xml parser.
    """    
    
    # IN 
    with open('{}'.format(parse_file), 'r') as drugbank_infile:
        drugbank_data = drugbank_infile.read()
    drugbank_infile.close()
    
    # OUT
    out_file = open("{}/parsed-{}-{}.tab".format(out_path,database,ext), 'w')
    out_db2chebi_file = open("{}/parsed-{}-{}-db2chebi.tab".format(out_path,database,ext), 'w')
    out_db2atc_file = open("{}/parsed-{}-{}-db2atc.tab".format(out_path,database,ext), 'w')
    out_atc1stBranch_file = open("{}/atc_ontology1rstBranchParents.tab".format(out_path), 'w')
    
    # RE PATTERNS
    id_pattern = re.compile(r'<drugbank-id primary=\"true\">(DB\d+)</drugbank-id>')
    name_pattern = re.compile(r'<name>(.+)</name>')
    chebi_pattern = re.compile(r'<resource>ChEBI</resource>\n      <identifier>(\d+)</identifier>')
    atc_pattern = re.compile(r'<atc-code code="(.+)">')
    atc_parents_pattern = re.compile(r'<level code="(.+)">(.+)</level>\n    </atc-code>')
    
    # VARIABLES
    db2chebi_dict = {} 
    db2atc_dict = {}
    db2atc_parents_dict = {}
    atc_parents2name_dict = {}
    
    # ALGORITHM
    print("You entered '{}' database and '{}' format.".format(database, ext))
    print("You entered the following file to parse: {}.\nThe parser is starting...".format(parse_file))
    print("The output files will be at: {}".format(out_path))
    # PARSE DRUGBANK DATABASE XML FILE
    drug_list = drugbank_data.strip('\n').split('exported-on="2016-07-01">')[1].split('</drugbank>')[0].split('</drug>\n<drug type=')
    i = 0
    for drug in drug_list:
        out_file.write('STAAAAAAAAAAAAAAART {}:{}FIIIIIIIIIIIN\n\n\n\n'.format(i,drug))
        i += 1
        # MATCH ID
        id_match = id_pattern.search(drug)
        if id_match:
            db_id = id_match.group(1)
        name_match = name_pattern.search(drug)
        if name_match:
            db_name = name_match.group(1)
        # CHEBI ID
        chebi_matches = chebi_pattern.finditer(drug)
        chebi_list = []
        for chebi_match in chebi_matches:   
            chebi_id = 'CHEBI:' + chebi_match.group(1)
            #print('{}'.format(chebi_id))
            chebi_list.append(chebi_id)
        db2chebi_dict[db_id] = chebi_list  
        out_db2chebi_file.write('{}\t{}\t{}\n'.format(db_id, db_name, chebi_list))
        # ATC CODE
        atc_matches = atc_pattern.finditer(drug)
        atc_list = []
        for atc_match in atc_matches:
            atc_id = 'ATC:' + atc_match.group(1)
            #print('{}'.format(atc_id))
            atc_list.append(atc_id)
        db2atc_dict[db_id] = atc_list
        # ATC FIRST BRANCH SUPPER CLASS
        atc_parents_matches = atc_parents_pattern.finditer(drug)
        atc_parents_list = []
        atc_parents_name_list = []
        for atc_parents_match in atc_parents_matches:
            atc_parent_id = 'ATC:' + atc_parents_match.group(1)
            atc_parent_name = atc_parents_match.group(2)
            #print('{}'.format(atc_parent_name))
            atc_parents2name_dict[atc_parent_id] = atc_parent_name
            atc_parents_list.append(atc_parent_id)
            atc_parents_name_list.append(atc_parent_name)         
        db2atc_parents_dict[db_id] = atc_parents_name_list 
        out_db2atc_file.write('{}\t{}\t{}\t{}\t{}\n'.format(db_id, db_name, atc_list, atc_parents_list, atc_parents_name_list))
    
    for parent_id in atc_parents2name_dict:
        parent_name = atc_parents2name_dict[parent_id]
        #print('{}'.format(parent_name))
        out_atc1stBranch_file.write('{}\n'.format(parent_name))
        
    print('Number of fragments: {}'.format(i))
    print("Parsing finished. See you next time!") 
    
    # OUT CLOSE
    out_file.close()
    out_db2chebi_file.close()
    out_db2atc_file.close()
    
    return db2chebi_dict , db2atc_parents_dict

def get_mapping_drugbank2chebi(in_file, out_file, db2chebi_dict):
    """
    Get drugbank to chebi mappings.
    Input: Drugbank ID list (tab)
    Output: ChEBI ID list (tab)
    """
    
    # OUT
    out_f = open('{}'.format(out_file), 'w')
    
    # ALGORITHM
    i=0; j=0 
    for line in open('{}'.format(in_file), 'r').readlines():
        hetnet_db_id = line.strip('\n')
        j += 1  
        if hetnet_db_id in db2chebi_dict and len(db2chebi_dict[hetnet_db_id]) != 0:
            i += 1     
            #print('mapped in the dictionary: {}{}'.format(hetnet_db_id, db2chebi_dict[hetnet_db_id]))   
            for chebi_id in db2chebi_dict[hetnet_db_id]: 
                #print('chebi mapped: {}\n'.format(chebi_id))
                out_f.write('{}\n'.format(chebi_id))
    print('chebi input:  {}, mapped in the dictionary: {}'.format(j, i))
    
    # OUT CLOSE
    out_f.close()
    
    return None

def get_mapping_drugbank2atc(in_file, out_file, db2atc_dict):
    """
    Get drugbank to chebi mappings.
    Input: Drugbank ID list (tab)
    Output: ATC parent list (tab)
    """
    
    # OUT
    out_f = open('{}'.format(out_file), 'w')
    
    # ALGORITHM
    i=0; j=0 
    for line in open('{}'.format(in_file), 'r').readlines():
        hetnet_db_id = line.strip('\n')
        j += 1  
        if hetnet_db_id in db2atc_dict and len(db2atc_dict[hetnet_db_id]) != 0:
            i += 1     
            #print('mapped in the dictionary: {}{}'.format(hetnet_db_id, db2chebi_dict[hetnet_db_id]))   
            for atc_id in db2atc_dict[hetnet_db_id]: 
                #print('atc mapped: {}\n'.format(atc_id))
                out_f.write('{}\n'.format(atc_id))
    print('atc input:  {}, mapped in the dictionary: {}'.format(j, i))
    
    # OUT CLOSE
    out_f.close()
    
    
    return None
  

if __name__ == '__main__':
    
    try:   
        ## Save disease and drug list in tab file
        #node = 'Compound'
        #json2tab(node)
        ## Parse DO and CHEBI obo ontologies
        in_path = '/home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/Characterization-Disease-Drug-Scope-of-hetio/in/'
        out_path = '/home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/Characterization-Disease-Drug-Scope-of-hetio/out/'
        do_file = 'doid.obo'
        chebi_file = 'chebi.obo' 
        # DO parsing
        #get_do_ontologyOBOChildParent(in_path,out_path,do_file)
        #get_do_ontologyOBOBranch(in_path,out_path,do_file)
        #get_activeDO(in_path,out_path,do_file, obsolete_continue = True)
        
        # ChEBI parsing
        #get_chebi_ontologyOBOChildParent(in_path,out_path,chebi_file) 
        #get_chebi_ontologyOBOBranch(in_path,out_path,chebi_file)
        #get_activeChEBI(in_path,out_path,chebi_file, obsolete_continue = True)
        
        # Drugbank parsing mappings from the database xml downloaded file: drugbank2chebi and drugbank2atc
        database = "drugbank"
        format = "xml"
        drugbank_file = "/home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/Characterization-Disease-Drug-Scope-of-hetio/in/drugbank-full-database.xml"
        #db2chebi_dict = parser(drugbank_file, out_path, database, format)
        db2chebi_dict, db2atc_parents_dict = parser(drugbank_file, out_path, database, format)
        # Mapping input to ChEBI
        in_file = out_path + 'hetionet-drugbankids-list.tab'
        out_file = out_path + 'hetionet-chebids-list.tab'
        #get_mapping_drugbank2chebi(in_file, out_file, db2chebi_dict)
        out_file = out_path + 'hetionet-atcids-list.tab'
        get_mapping_drugbank2atc(in_file, out_file, db2atc_parents_dict)
    
        
    except OSError:
        print("Some problem occurred....T_T")
        sys.exit() 