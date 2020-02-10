#!/usr/bin/env python

import re
import sys
import subprocess

pattern = re.compile(r'(?<=tag=)([^;]*)')
genetypepattern = re.compile(r'(?<=gene_type=)([^;]*)')
transcriptidpattern = re.compile(r'(?<=transcript_id=)([^;]*)')
genenamepattern = re.compile(r'(?<=gene_name=)([^;]*)')

transcripts = {}

lines = []
infh = open("gencode.v19.annotation.gff3", "r")
for line in infh:
    if line[0] == "#":
        lines.append(line)
        
    #elif line.split("\t")[1] == "HAVANA":
    #    pass
        
    else:
        try:
            m = genetypepattern.search(line)
            #print m
            #print m.group(0).strip()
            #print m.group(0).strip()
            if m.group(0).strip() not in ["protein_coding", "IG_C_gene", "IG_V_gene", "IG_D_gene", "IG_J_gene"]:
                #print m.group(0).strip()
                continue
        except AttributeError as e:
            print line
    
        try:
            m = pattern.search(line)
            
            tags = m.group(1).strip().split(",")
            #print tags
            if any(x in ["PAR", "cds_start_NF", "cds_end_NF", "mRNA_start_NF", "mRNA_end_NF", "not_organism_supported",  "pseudo_consens", "non_canonical_U12", "alternative_5_UTR", "alternative_3_UTR"] for x in tags):
            #if any(x in ["PAR",  "pseudo_consens", "non_canonical_U12", "alternative_5_UTR", "alternative_3_UTR"] for x in tags):
                #print tags
                continue
            else:
                if "appris_principal" in tags or "appris_candidate_longest" in tags: #Used when running with gencode V19
                #if "appris_principal_1" in tags or "appris_principal_2" in tags or "appris_principal_3" in tags or "appris_principal_4" in tags or "appris_principal_5" in tags: #Used for newer gencode
                    #print tags
                    tid = transcriptidpattern.search(line).group(1).strip()
                    gn = genenamepattern.search(line).group(1).strip()
                    transcripts[tid] = gn
                    lines.append(line)
            
                '''tid = transcriptidpattern.search(line).group(1).strip()
                gn = genenamepattern.search(line).group(1).strip()
                transcripts[tid] = gn'''
            
            #print line
        except AttributeError as e:
            #print line
            pass
infh.close()
            

bads = []
            
gene_names = set(transcripts.values())
'''for name in gene_names:
    if transcripts.values().count(name) != 1:
        bads.append(name)
    #print name, ":", transcripts.values().count(name)
    
    
    
for name in bads:
    print name, ":", transcripts.values().count(name)


    
print len(gene_names)'''
#print transcripts
#print "YES?"
transcript_lengths = {}
for tid in transcripts.keys():
    transcript_lengths[tid] = 0
    
for line in lines:
    if line[0] == "#":
        continue
    s = line.split("\t")
    tid = transcriptidpattern.search(line).group(1).strip()

    if s[2] == "CDS":
        transcript_lengths[tid] += (int(s[4]) - int(s[3]) +1)
    
    
    
outfh = open("transcripts_with_lengths.tsv", "w")
for tid in transcripts.keys():
    outfh.write("\t".join([tid, transcripts[tid], str(transcript_lengths[tid])]) + "\n")
outfh.close()
    


genes = {}
for name in gene_names:
    genes[name] = {"tid": "NA", "length": 0}
    
infh = open("transcripts_with_lengths.tsv", "r")
for line in infh:
    s = line.strip().split("\t")
    if int(s[2]) > genes[s[1]]["length"]:
        genes[s[1]]["tid"] = s[0]
        genes[s[1]]["length"] = s[2]
        
    elif int(s[2]) == genes[s[1]]["length"]:
        if "ENSTR" in s[0] or "ENSG" in s[0]:
            continue
        if genes[s[1]]["tid"] > s[1]:  # is existing one later alphabetically, then replace
            genes[s[1]]["tid"] = s[0]
            genes[s[1]]["length"] = s[2]
infh.close()            
            
            
outfh = open("filtered_gencode.v19.annotation.gff3", "w")
for line in lines:
    if line[0] == "#":
        outfh.write(line)
            
for gene in genes.keys():
    tid = genes[gene]["tid"]
    bash_cmd = "grep \"transcript_id=%s;\" gencode.v19.annotation.gff3" % tid
    process1 = subprocess.Popen(bash_cmd, shell = True, stdout = subprocess.PIPE)
    annotations = process1.communicate()[0].rstrip().split("\n")
    for a in annotations:
        outfh.write(a + "\n")
        
outfh.close()
    













