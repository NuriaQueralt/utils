#!/usr/bin/env python
# -*- coding: utf-8 -*-

##    Description    Tool for generating a SDFile from diverse sources
##                   
##    Authors:       Inés Martínez (mmartinez4@imim.es)
##                   Manuel Pastor (manuel.pastor@upf.edu)
##
##    Copyright 2015 Manuel Pastor
##
##    This file is part of PhiTools
##
##    PhiTools is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation version 3.
##
##    PhiTools is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with PhiTools.  If not, see <http://www.gnu.org/licenses/>

import urllib
import os
import sys
import getopt
from rdkit import Chem
from rdkit.Chem import AllChem

def getSDF(out,data,iformat,idname,header):

    vals = []
    noms = []    
    f = open (data)
    counter=0
    for line in f:
        if counter==0 :
            if header :
                counter+=1
                continue
            
        line=line.rstrip()
        line=line.split('\t')

        vals.append(line[0])  # the mol must be in the first place
        if len(line)>1:
            noms.append(line[1])
        else:
            noms.append('mol%0.8d'%counter)
        counter+=1
    f.close()

    # for inchis use SDWriter
    if iformat == 'inchis':
        writer = Chem.rdmolfiles.SDWriter(out)
        for v,n in zip(vals,noms):
            print v[:20]
            try:
                mol = Chem.inchi.MolFromInchi (v)
                AllChem.Compute2DCoords(mol)
                mol.SetProp(idname,n)
                writer.write(mol)
            except:
                print 'error processing ', v
                pass
        writer.close()

        return

    # for names convert to SMILES, in either case use MolFromSmiles
    fo = open (out,'w+')     
    for v,n in zip(vals,noms):
        
        if iformat == 'names':
            print v,'\t', 
            smi = urllib.urlopen('http://cactus.nci.nih.gov/chemical/structure/'+v+'/smiles')
            smi1 = smi.readline().rstrip()
        else:
            smi1 = v  

        if smi1 and not ('Page not found' in smi1):
            print smi1
        else:
            print 'error processing ', v
            continue
        
        try:
            m = Chem.MolFromSmiles(smi1)
            Chem.AllChem.Compute2DCoords(m)
            m.SetProp(idname,n)
        except:
            print 'error processing', v
            continue
            
        mb = Chem.MolToMolBlock(m)        

        fo.write(mb)
        
        if iformat=='names':
            fo.write('>  <name>\n'+v+'\n\n')

        fo.write('>  <'+idname+'>\n'+n+'\n\n')
        
        fo.write('>  <smiles>\n'+smi1+'\n\n')

        fo.write('$$$$\n')        
    fo.close()

def usage ():
    """Prints in the screen the command syntax and argument"""
    print 'getSDF -f|s|i input.csv [--id=molecule_id] [-o output.sdf]'
    print '\n\t -f input.csv (molecules as names)'
    print '\t -s input.csv (molecules as SMILES)'
    print '\t -i input.csv (molecules as InChI)'
    print '\t --id=molecule_id field where the unique id will be added)'
    print '\t -o output.sdf (output SDFile)'

    sys.exit(1)

def main ():
    out= 'output.sdf'
    data = None
    iformat = None
    idname = 'name'
    header = False
    
    try:
       opts, args = getopt.getopt(sys.argv[1:],'f:s:i:o:', ['header','id='])
    except getopt.GetoptError:
        print "Arguments not recognized"
        usage()
    
    if not len(opts):
        print "Arguments not recognized"
        usage()

    if len(opts)>0:
        for opt, arg in opts:
            if opt in '-o':
                out = arg
            elif opt in '-f':
                data = arg
                iformat = 'names'
            elif opt in '-s':
                data = arg
                iformat = 'smiles'
            elif opt in '-i':
                data = arg
                iformat = 'inchis'
            elif opt in '--id':
                idname = arg
            elif opt in '--header':
                header = True

    if not data: usage()
    
    getSDF(out,data,iformat,idname,header)    

if __name__ == '__main__':    
    main()
