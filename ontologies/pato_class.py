'''
Created on Sep 30, 2019

@name: pato_class.py
@description: Module for the PATO ontology
@author: Nuria Queralt Rosinach
@version: 1.0
@date: 30-09-2019
@license: CC0
'''

import re, sys

class term(object):
    '''
    Classes in the ontology
    '''


    def __init__(self, pato_owl):
        '''
        Constructor
        '''

        self.metadata = []
        #self.doid2orpha = {}
        self.opposites = {}

        # Input
        with open(pato_owl, 'r', encoding='latin1') as pato_f:
            pato_d = pato_f.read()
        pato_f.close()

        # RE patterns
        iri_pattern = re.compile(r'<owl:Class rdf:about="(.+)"(.*)>')
        label_pattern = re.compile(r'<rdfs:label(.+)>(.+)</rdfs:label>')
        exact_synonym_pattern = re.compile(r'<oboInOwl:hasExactSynonym(.+)>(.+)</oboInOwl:hasExactSynonym>')
        definition_pattern = re.compile(r'<obo:IAO_0000115(.+)>(.+)</obo:IAO_0000115>')
        #doid_pattern = re.compile(r' <owl:Class rdf:about="http://purl.obolibrary.org/obo/DOID_(.+)">')
        #orpha_pattern = re.compile(r'<owl:equivalentClass rdf:resource="http://www.orpha.net/ORDO/Orphanet_(.+)"/>')
        id_pattern = re.compile(r'<owl:Class rdf:about="http://purl.obolibrary.org/obo/(.+)">')
        opposite_pattern = re.compile(r'<obo:RO_0002604 rdf:resource="http://purl.obolibrary.org/obo/(.+)"/>')

        # Algorithm
        # Classes in chunks
        pato_terms = pato_d.strip().split('</rdf:RDF>')[0].split('// Classes')[1].split('<!-- ')[1:]

        # Get term metadata
        # Parse chunks and extract mappings, term info
        for term in pato_terms:
            concept = {}

            # get term id, iri
            iri_match = iri_pattern.search(term)
            try:
                iri = iri_match.group(1)
            except AttributeError:
                #print('term that is not a class: ',term)
                continue

            id = iri.rsplit('/', 1)[1].replace('_', ':')

            # get term info: label, synonyms, definition
            label_match = label_pattern.search(term)
            if not label_match:
                label = 'NA'
            else:
                label = label_match.group(2)
            synonym_matches = exact_synonym_pattern.finditer(term)
            synonyms_l = []
            for synonym_match in synonym_matches:
                synonym = synonym_match.group(2)
                synonyms_l.append(synonym)
            synonyms = "|".join(synonyms_l)
            if not synonyms:
                synonyms = 'NA'
            definition_match = definition_pattern.search(term)
            if not definition_match:
                definition = 'NA'
            else:
                definition = definition_match.group(2)

            # build the concept dictionary
            concept['id'] = id
            concept['iri'] = iri
            concept['label'] = label
            concept['synonyms'] = synonyms
            concept['definition'] = definition

            # append the concept to the list of terms
            self.metadata.append(concept)


        # # Get do2orpha mappings
        # # Parse chunks and extract mappings, term info
        # for term in pato_terms:
        #     # DOID class
        #     doid_match = doid_pattern.search(term)
        #     if not doid_match:
        #         continue
        #     doid_code = 'DOID:' + doid_match.group(1)
        #
        #     # Orphanet equivalent classes (mappings)
        #     orpha_matches = orpha_pattern.finditer(term)
        #     if not orpha_matches:
        #         continue
        #     orpha_l = []
        #     for orpha_match in orpha_matches:
        #         orpha_code = 'Orphanet:' + orpha_match.group(1)
        #         orpha_l.append(orpha_code)
        #     self.doid2orpha[doid_code] = set(orpha_l)

        # Get opposite pato classes
        # Parse chunks and extract 'is_opposite_of' relations
        c = 0
        for term in pato_terms:
            # PATO class
            pato_subject_match = id_pattern.search(term)
            pato_object_match = opposite_pattern.search(term)
            if not pato_subject_match:
                print('not subject matched!')
                continue
            subject = pato_subject_match.group(1).replace('_', ':')

            if not pato_object_match:
                #print('not opposite trait for {}'.format(pato_subject_match.group(1)))
                continue
            object = pato_object_match.group(1).replace('_', ':')

            # # check that there are no classes with more than open opposites: CHECKED, there are not
            # opp_matches = opposite_pattern.finditer(term)
            # if not opp_matches:
            #     continue
            # opp_l = []
            # for opp in opp_matches:
            #     opp_l.append(opp.group(1))
            # if len(opp_l) > 1:
            #     print('{} {}'.format(subject,opp_l))
            # else:
            #     print('{}\t{}'.format(subject, object))

            self.opposites[subject] = object
            #print('{}\t{}'.format(subject, object))


    def get_metadata_per_id(self, id):
        '''
        This function returns all the metadata for term queried: id, iri, label, synonyms, definition.
        :param id: str, ID of the term, e.g. DOID:4
        :return: dict, one dictionary with the metadata
        '''

        if '_' in id:
            id = id.replace('_',':')

        concept = 0
        for term in self.metadata:
            if term['id'] == id:
                concept = term
        if concept:
            return concept
        else:
            return print('Please enter a correct ID format, e.g. PATO:0000299. Use ":" of namespace separator. Thanks!')

    def get_specific_metadata_per_id(self, id, metadata='iri'):
        '''
        This Function returns the specific requested metadata for term queried.
        :param id: str, ID of the term, e.g. DOID:4
        :param metadata: str, 'iri', 'label', 'synonyms', or 'definition'
        :return: str
        '''

        term = self.get_metadata_per_id(id)
        return term[metadata]

    def print_metadata(self,outfile):
        '''
        This function extracts basic term metadata information for all terms in the ontology to be used in graph
        representation applications such as neo4j or Knowledge.Bio.
        Particularly, returns the id, :LABEL, label, synonyms, and definition
        :return: output file called 'pato_concepts.tsv' with all the metadata for all terms
        '''

        # Output
        out_f = open('{}'.format(outfile),'w')
        out_f.write('id:ID,:LABEL,preflabel,synonyms:IGNORE,definition\n')
        out_f.write('owl#Thing,PATOCLASS,"Thing","NA","Root class."\n')

        # Algorithm
        # Parse chunks and extract mappings, term info
        for term in self.metadata:
            # get term id, iri, label, synonyms, definition metadata
            id = term.get('id')
            iri = term.get('iri')
            label = term.get('label')
            synonyms = term.get('synonyms')
            definition = term.get('definition')

            # write term metadata down
            out_f.write('{},PATOCLASS,"{}","{}","{}"\n'.format(id, label, synonyms, definition))

        out_f.close()

        return print('Term metadata file generated at "{}"'.format(outfile))

    # def get_orphanet_mappings_per_doid(self, doid):
    #     '''
    #     This function return the orphanet mappings for the DO term queried.
    #     :param doid: DOID
    #     :return: orphanet mappings
    #     '''
    #     return self.doid2orpha.get(doid, ['NA'])

    def print_opposites(self,outfile):
        '''
        This function extracts opposite traits for all classes in the ontology to be used in TILDE.
        Particularly, returns 'is opposite of (RO:0002604)' relations in prolog format
        :return: output file called  by the user, sth like 'pato_opposite_classes.bg'
        '''

        # Output
        out_f = open('{}'.format(outfile),'w')

        # Algorithm
        # Parse chunks and extract mappings, term info
        for quality, opposite in self.opposites.items():
            # get opposites
            # (hasQuality(x,y),Q(y) :- P(x))
            out_f.write('hasOppositeQuality({},{}), Q({}) :- Q({}).\n'.format(quality,opposite,opposite,quality))

        out_f.close()

        return print('Class opposites file generated at "{}"'.format(outfile))


class hierarchy(object):
    '''
    Inferred ontology - extraction of the hierarchy
    '''

    def __init__(self, pato_owl):
        '''
        Constructor
        :param pato_owl:
        '''

        self.totalNumberOfTerms = 0
        self.namespaces = {}
        self.predicates = {}

        # Input
        with open(pato_owl, 'r') as pato_f:
            pato_d = pato_f.read()

        # Output
        out_f = open('/home/nuria/soft/neo4j-community-3.0.3/import/mondo/mondo_statements.tsv', 'w')
        out_f.write(':START_ID,:TYPE,association_type,pid,:END_ID,reference_uri,reference_supporting_text,reference_date\n')

        # RE patterns
        subjectIri_pattern = re.compile(r'<owl:Class rdf:about="(.+)">')
        propertyObjectIris_pattern = re.compile(r'<(.+) rdf:resource="(.+)"/>')

        # Algorithm
        # Classes in chunks
        pato_terms = pato_d.strip().split('</rdf:RDF>')[0].split('// Classes')[1].split('<!-- ')[1:]
        self.totalNumberOfTerms = len(pato_terms)

        # Parse chunks and extract relationships
        pid = 'P279'
        reference_uri = "http://purl.obolibrary.org/obo/upheno/pato.owl"
        reference_text = "No sentence because edge extracted from the PATO ontology"
        reference_date = "2017-05-02"
        for term in pato_terms:
            # extract relationships in each class disclosure
            subjectIri_match = subjectIri_pattern.search(term)
            subjectIri = subjectIri_match.group(1)
            subjectId = subjectIri.rsplit('/',1)[1].replace('_',':')
            objectPropertyIris_matches = propertyObjectIris_pattern.finditer(term)
            for objectPropertyIris_match in objectPropertyIris_matches:
                propertyIri = objectPropertyIris_match.group(1)
                objectIri = objectPropertyIris_match.group(2)
                propertyId = propertyIri.split(':')[1]
                objectId = objectIri.rsplit('/',1)[1].replace('_', ':')
                out_f.write('{},{},{},{},{},{},"{}",{}\n'.format(subjectId,propertyId,propertyId,pid,objectId,reference_uri,reference_text,reference_date))

                # get information: distinct property and namespace types
                self.predicates[propertyIri] = 1
                ns = objectIri.rsplit('/',1)[1].split('_')[0]
                self.namespaces[ns] = 1
        out_f.close()

    def get_total_number_of_terms(self):
        return print('Total number of terms: {}'.format(self.totalNumberOfTerms))

    def get_predicates(self):
        return print('Distinct predicates: {}'.format(self.predicates.keys()))

    def get_object_namespaces(self):
        return print('Distinct objects namespaces: {}'.format(self.namespaces.keys()))



if __name__ == '__main__':

    try:
        # input
        #pato_f = "/home/nuria/soft/neo4j-community-3.0.3/import/mondo/mondo.owl"
        pato_f = "/home/rosinanq/workspace/droppheno/ontologies/pato.owl"
        #pato_inferred_f = "/home/nuria/soft/neo4j-community-3.0.3/import/mondo/mondo-inferred.owl"

        # output
        #concepts_f = '/home/nuria/soft/neo4j-community-3.0.3/import/mondo/mondo_concepts.tsv'

        # parse owl file
        tm = term(pato_f)
        #print(tm.doid2orpha)
        #print(tm.metadata)
        #tm.print_metadata(concepts_f)
        #print(tm.get_metadata_per_id(id='DOID_0001816'))
        #print(tm.get_specific_metadata_per_id(id='DOID_0001816', metadata='iri'))
        #print(tm.get_specific_metadata_per_id(id='DOID:0001816', metadata='label'))
        #print(tm.get_specific_metadata_per_id(id='DOID_0001816', metadata='definition'))
        #cl = hierarchy(pato_inferred_f)
        #cl.get_total_number_of_terms(), cl.get_predicates(), cl.get_object_namespaces()

        # pato
        #print(tm.get_metadata_per_id(id='PATO:0000299'))
        opposites_file = "/home/rosinanq/workspace/droppheno/ontologies/pato_opposites.bg"
        tm.print_opposites(opposites_file)
        # check opposites by writing down the labels
        opposites_file = "/home/rosinanq/workspace/droppheno/ontologies/pato_opposites_label.bg"
        out_f = open('{}'.format(opposites_file), 'w')
        for qa, qb in tm.opposites.items():
            a = tm.get_specific_metadata_per_id(id=qa, metadata='label')
            b = tm.get_specific_metadata_per_id(id=qb, metadata='label')
            print('{} {}'.format(a,b))
            out_f.write('hasOppositeQuality({},{}), Q({}) :- Q({}).\n'.format(a, b, b, a))

    except OSError:
        print("Some problem occurred....T_T")
        sys.exit()