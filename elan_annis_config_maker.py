# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 13:22:26 2018
ELAN ANNIS CONFIG MAKER
elan_annis_config_maker.py

@author: Wolfgang Barth
wolfgang.barth@anu.edu.au

create a config file with a dictionary that includes all tier-names 
the value can be changed to what you want it to be in ANNIS

customize:

    path: set path to folder of files
    
"""
import glob
import os
import ntpath
from bs4 import BeautifulSoup
import datetime


def make_out_file():
    """ create current time stamp and config file name
    """
    now = datetime.datetime.now()
    date_time = now.strftime("%Y%m%d_%H%M")
    print ('\n config_file: config_' + date_time + '.conf')
    return ('config_' + date_time + '.conf')

outfile = make_out_file()

# path to folder full of ELAN (.eaf) files
path = 'C:/Path/to/folder/full/of/files'

# location where config file will be written
configOut = open('C:/Location/of/config/file/' + outfile, 'w')


folder_name = path.split('/')[-1]
def clean_string(text_raw):
    
    """ takes a string and delets all non ABC 123 characters
    """
    text_list = []
    text_raw.replace('\t', '')
    
    # mostly standard stuff allowed at the moment
    for x in text_raw:
        if x.isalpha() or x.isspace() or x.isdigit() or " " or x in "!?:;.,'":
            text_list.append(x.lower())

    text = ''.join(text_list)
    text.replace('  ' , ' ')
    return text

configOut.write('# CONFIG FILE: ' + outfile + '\n')
welcomeText = (
"""
# customize the dictionary values to change tier names
# the mainText value has to match the final value of the
# main tier, so if you change the tier name, you also have
# to change the mainText accordingly\n\n
# if there is a dialog in the ELAN file, list both tiers in the mainText list\n
"""
)
configOut.write(welcomeText)

configOut.write("{\n'corpus_name': '" + folder_name + "',\n")
configOut.write("'replace_with_space': '§$%&',\n")
configOut.write("'replace_with_underscore': '*+',\n")

def path_leaf(path):
    """ cut the file name out of the path
    """
    head, tail = ntpath.split(path)
    filename = tail.split(".")[0] # remove the extension of the file
    return filename

def config_maker():
      
    for file in glob.glob(os.path.join(path, '*.eaf')):
        fileName = path_leaf(file)
        
        # output
        print ('\nfile: ' + fileName + ' ---------' )
        
        configOut.write("\n'" + str(fileName) + "': {")

       
        with open(file, encoding="utf8") as f:
            tier_list = []
            for line in f:
                
                # find all tiers in XML(.eaf) file
                if line.startswith('    <TIER'):
                    
                    soup = BeautifulSoup(line, 'html5lib')
                    tierLine = soup.find('tier')
                    tierID = tierLine['tier_id']
                    
                     
                    tier_list.append(tierID)
                    
                    print ('----- ' + tierID + ' --> ' + clean_string(tierID).replace(' ', '_'))
                  
        configOut.write("\n        'mainText': ['" + clean_string(tier_list[0].replace(' ', '_')) + "'],")
        configOut.write("\n        'delete': [],\n")
        for tier in tier_list:
            configOut.write("        '" + tier + "': '" + clean_string(tier).replace(' ', '_') + "',\n")
        configOut.write('        },')
    configOut.write('\n}')
    configOut.close()

config_maker()