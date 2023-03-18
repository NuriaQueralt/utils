//-----------------------------------------------------------
// Sarah M. Algamdi
//-----------------------------------------------------------
// This changes the IRI of all classes in the ontology
// to run:
// groovy change_entity_iri.groovy ontology_path new_IRI new_ontology_path
//----------------------------------------------------------- 


@Grapes([
 @Grab(group='org.slf4j', module='slf4j-simple', version='1.6.1'),
 @Grab(group = 'org.semanticweb.elk', module = 'elk-owlapi', version = '0.4.2'),
 @Grab(group = 'net.sourceforge.owlapi', module = 'owlapi-api', version = '4.2.5'),
 @Grab(group = 'net.sourceforge.owlapi', module = 'owlapi-apibinding', version = '4.2.5'),
 @Grab(group = 'net.sourceforge.owlapi', module = 'owlapi-impl', version = '4.2.5'),
 @Grab(group = 'net.sourceforge.owlapi', module = 'owlapi-parsers', version = '4.2.5'),
 @GrabConfig(systemClassLoader = true)
])


import org.semanticweb.owlapi.model.parameters.*
import org.semanticweb.elk.owlapi.ElkReasonerFactory;
import org.semanticweb.elk.owlapi.ElkReasonerConfiguration
import org.semanticweb.elk.reasoner.config.*
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.reasoner.*
import org.semanticweb.owlapi.reasoner.structural.StructuralReasoner
import org.semanticweb.owlapi.vocab.OWLRDFVocabulary;
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.io.*;
import org.semanticweb.owlapi.owllink.*;
import org.semanticweb.owlapi.util.*;
import org.semanticweb.owlapi.search.*;
import org.semanticweb.owlapi.manchestersyntax.renderer.*;
import org.semanticweb.owlapi.reasoner.structural.*
import groovy.json.JsonOutput
import java.io.File 


OWLOntologyManager manager = OWLManager.createOWLOntologyManager()
OWLDataFactory fac = manager.getOWLDataFactory()
StructuralReasonerFactory f1 = new StructuralReasonerFactory()



ont =manager.loadOntologyFromOntologyDocument(new File(args[0]))


ConsoleProgressMonitor progressMonitor = new ConsoleProgressMonitor()
OWLReasonerConfiguration config = new SimpleConfiguration(progressMonitor)
ElkReasonerFactory f = new ElkReasonerFactory()
OWLReasoner reasoner = f.createReasoner(ont,config)



final OWLEntityRenamer renamer = new OWLEntityRenamer(manager, Collections.singleton(ont));
final Map<OWLEntity, IRI> entity2IRIMap = new HashMap<>();


ont.getClassesInSignature(true).each {cl ->


	final IRI iri = cl.getIRI();
	class_iri = iri.toString().substring(0,iri.toString().lastIndexOf("/"))
	class_id  = iri.toString().substring(iri.toString().lastIndexOf("/")+1,iri.length()-1)
	newIRI = iri.toString().replace(class_iri,args[1])
    entity2IRIMap.put(cl, IRI.create(newIRI));


}

    ont.applyChanges(renamer.changeIRI(entity2IRIMap));


// save ontology
manager.saveOntology(ont, IRI.create((new File(args[2]).toURI())))