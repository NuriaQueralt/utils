'''
Created on Apr 21, 2017

@author: Núria Queralt Rosinach
@version: 1.0
@note: Module for hetionet
@license: CC0
'''

import sys, re
#from lib import abravo_lib as util

def disease_gene_xml_parser(parse_f,path):

    '''
    Orphanet xml disease-HPO annotation file parser
    :param parse_file: /home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/en_product6.xml
    :return associations_file: /home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/orphanet-disease-gene.tsv
    :return diseases_file: /home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/orphanet-diseases.tsv
    :return symptoms_file: /home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/orphanet-symptoms.tsv
    '''

    # IN
    with open('{}'.format(parse_f), 'r', encoding="ISO-8859-1") as orphadata_f:
        orphadata_d = orphadata_f.read()
    orphadata_f.close()

    # OUT
    rd_gene_f = open("{}orphanet-disease-gene.tsv".format(path), 'w')
    rd_gene_f.write(
        'orphanet_code\torphanet_term\torphanet_gene_id\tgene_orphanumber\tgene_name\tgene_type\tgene_symbol\tdga_type\tdga_status\n')
    # sym_f = open("{}orphanet-genes.tsv".format(path), 'w')
    # rd_f = open("{}orphanet-diseases.tsv".format(path), 'w')

    # RE PATTERNS
    orphaNum_pattern = re.compile(r'<OrphaNumber>(.+)</OrphaNumber>\n')
    name_pattern = re.compile(r'<Name lang="en">(.+)</Name>')
    gene_id_pattern = re.compile(r'<Gene id="(\d+)">')
    symbol_pattern = re.compile(r'<Symbol>(.+)</Symbol>')

    # VARIABLES
    rd2name_dct = {}
    gene2type_dct = {}

    # ALGORITHM
    association_l = orphadata_d.split('</Disorder>')
    for rd in association_l:
         rd_match = orphaNum_pattern.search(rd)
         if not rd_match:
             continue
         rd_orphaNum = rd_match.group(1)
         rd_name_match = name_pattern.search(rd)
         rd_name = rd_name_match.group(1)
         rd2name_dct[rd_orphaNum] = rd_name
         print('rd_orpha: {}\trd_name: {}'.format(rd_orphaNum,rd_name))
         # GeneList fragment
         geneList_l = rd.split('<GeneList count=')[1].split('<DisorderGeneAssociationList count=')
         gene_id_matches = gene_id_pattern.finditer(geneList_l[0])
         gene_id_l = []
         for gene_id_match in gene_id_matches:
             gene_id = gene_id_match.group(1)
             gene_id_l.append(gene_id)
         gene_type_matches = name_pattern.finditer(geneList_l[0])
         gene_type_l = []
         for gene_type_match in gene_type_matches:
             gene_type = gene_type_match.group(1)
             gene_type_l.append(gene_type)
         for i in range(len(gene_id_l)):
             gene2type_dct[gene_id_l[i]] = gene_type_l[i]
         #print('gene_id: {}\tgene_type: {}'.format(gene_id, gene_type))
         # DisorderGeneAssociationList fragment
         dgaList_l = geneList_l[1].split('</DisorderGeneAssociation>')
         dgaList_l.pop()
         for dga in dgaList_l:
              #print('fragment: {}'.format(dga))
              gene_id_match = gene_id_pattern.search(dga)
              gene_id = gene_id_match.group(1)
              gene_orphaNum_match = orphaNum_pattern.search(dga)
              gene_orphaNum = gene_orphaNum_match.group(1)
              gene_symbol_match = symbol_pattern.search(dga)
              gene_symbol = gene_symbol_match.group(1)
              names_matches = name_pattern.finditer(dga)
              names_l = []
              for names_match in names_matches:
                  name = names_match.group(1)
                  names_l.append(name)
              gene_name = names_l[0]
              dga_type = names_l[1]
              dga_status = names_l[2]
              print('gene_id: {}\tgene_orphanum: {}\tgene_name: {}\tgene_type:{}\tgene_symbol: {}\tdga_type: {}\tdga_status: {}'.format(gene_id,
                                                                                                                gene_orphaNum,
                                                                                                                 gene_name,
                                                                                                                gene2type_dct[gene_id],
                                                                                                                 gene_symbol,
                                                                                                                 dga_type,
                                                                                                                  dga_status))
              rd_gene_f.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(rd_orphaNum,rd_name,gene_id,gene_orphaNum,gene_name,gene2type_dct[gene_id],
                                                                                                                 gene_symbol,
                                                                                                                 dga_type,
                                                                                                                  dga_status))
    print('Total disorders: {}'.format(len(rd2name_dct)))
    # # Write association file
    # rd_gene_f.write('orphanet_code\torphanet_term\torphanet_gene_id\tgene_name\tgene_type\tgene_symbol\tdga_type\tdga_status\n')
    # for rd in rd2name_dct:
    #     for idx in range(len((rd2symId_dct[rd]))):
    #         if len(rd2symId_dct[rd]) == 0:
    #             rd2symId_dct[rd][idx] = None
    #             rd2symTerm_dct[rd][idx] = None
    #         rd_sym_f.write('Orphanet:{}\t{}\t{}\t{}\n'.format(rd,rd2name_dct[rd],rd2symId_dct[rd][idx],rd2symTerm_dct[rd][idx]))
    #         sym_dct[rd2symId_dct[rd][idx]] = rd2symTerm_dct[rd][idx]
    #
    # # Write symptoms file
    # sym_f.write('hp_code\thp_term\n')
    # for sym in sym_dct:
    #     sym_f.write('{}\t{}\n'.format(sym,sym_dct[sym]))
    #
    # # Write diseases file
    # rd_f.write('orphanet_code\torphanet_term\n')
    # for rd in rd2name_dct:
    #     rd_f.write('Orphanet:{}\t{}\n'.format(rd,rd2name_dct[rd]))
    #
    # CLOSE
    rd_gene_f.close()
    # sym_f.close()
    # rd_f.close()

def disease_phenotype_xml_parser(parse_f,path):

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



if __name__ == '__main__':

    try:
        ## Parse rare disease annotation file (xml)
        # Path to in and out files
        orphadata_f = '/home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/en_product6.xml'
        path = '/home/nuria/workspace/repurposing-hetio/rephetio-dhimmelstein/hetionet+hpo/data/'

        # Parse Orphadata XML rd-gene annotation file
        disease_gene_xml_parser(orphadata_f,path)

        ## Parse Orphadata XML rd-hpo annotation file
        # disease_phenotype_xml_parser(orphadata_f,path)


    except OSError:
        print("Some problem occurred....T_T")
        sys.exit()