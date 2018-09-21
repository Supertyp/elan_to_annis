# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 12:25:33 2018

@author: Wolfgang
"""

import ast
import glob
import os
import ntpath
from bs4 import BeautifulSoup


# path to folder full of Flextext files
path = 'C:/Users/Path/to/folder'
out_path = 'C:/Users/Path/to/output/folder/'
config_file = 'C:/Users/Path/to/config_XXXXXXXX_XXXX.conf' 


def read_config_file(config_file):
    """ read config file into a dictinary
    """
    s = open(config_file, 'r').read()
    configDict = ast.literal_eval(s)
    print (str(configDict))
    return configDict


def close_all_files():
    """ all files have to be closed at the end
    """
    annisVersionOut.close()
    textAnnisOut.close()
    nodeAnnisOut.close()
    node_annotationAnnisOut.close()
    componentAnnisOut.close()
    rankAnnisOut.close()
    corpusAnnotationOut.close()
    edgeAnnotationOut.close()
    corpusAnnisOut.close()
    resolve_vis_mapAnnisOut.close()


def path_leaf(path):
    """ cut the file name out of the path
    """ 
    head, tail = ntpath.split(path)
    filename = tail.split(".")[0] # remove the extension of the file
    return filename


def write_to_file(file_name, *args):
    """ writes all given args to a file: file_name
    """
    file_name.write(str('\t'.join([str(arg) for arg in args]) + '\n'))


def write_span(nodeCount,
               file_index,
               spanName,
               first_letter_index,
               last_letter_index,
               firstTok,
               lastTok,
               token):
    
    """ for each span, a bunch of entries have to be made in a bunch of files 
    """
    
    write_to_file(nodeAnnisOut,
                  nodeCount,
                  '0',
                  file_index,
                  'default_ns',
                  spanName,
                  first_letter_index,
                  last_letter_index,
                  'NULL',
                  firstTok,
                  lastTok,
                  'NULL',
                  'NULL',
                  'NULL',
                  'TRUE')
    
    """
    write_to_file(node_annotationAnnisOut,
                  nodeCount,
                  'default_ns',
                  'word',
                  token)                        
    """
    
    write_to_file(componentAnnisOut,
                  nodeCount,
                  'c',
                  'default_ns',
                  'NULL')                        
    
    write_to_file(rankAnnisOut,
                  nodeCount,
                  '0',
                  nodeCount,
                  nodeCount,
                  nodeCount,
                  'NULL',
                  '0')


def write_text(nodeCount,
               file_index,
               spanName,
               name_of_tier,
               textFirstLetter,
               textLastLetter,
               textFirstToken,
               textLastToken,
               text):
    
    """ for each text entry a bunch of entries in a bunch of files
    """

    write_to_file(nodeAnnisOut,
                  nodeCount,
                  '0',
                  file_index,
                  'default_ns',
                  spanName,
                  textFirstLetter,
                  textLastLetter,
                  'NULL',
                  textFirstToken,
                  textLastToken,
                  'NULL',
                  'NULL',
                  'NULL',
                  'TRUE')
  
    write_to_file(node_annotationAnnisOut,
                  nodeCount,
                  'default_ns',
                  name_of_tier,
                  text)
 
    write_to_file(componentAnnisOut,
                  nodeCount,
                  'c',
                  'default_ns',
                  'NULL')
    
    write_to_file(rankAnnisOut,
                  nodeCount,
                  '0',
                  nodeCount,
                  nodeCount,
                  nodeCount,
                  'NULL',
                  '0')


def clean_string(text_raw):
    """ takes a string and delets all non ABC 123 characters
    """
    
    text_list = []
    text_raw.replace('\t', '')
    
    # only letters and space allowed at the moment
    for x in text_raw:
        if x.isalpha():
            text_list.append(x.lower())
        elif x.isspace() :
            text_list.append(x.lower())
        elif x.isdigit():
            text_list.append(x.lower())
        elif x in "!?:;.,'":
            text_list.append(x)    
        elif x == '@':
            text_list.append('_')            

    text = ''.join(text_list)
    text.replace('  ' , ' ')
    return text


def format_maker():
    
    doc_count = 1
    node_index = 0
    file_index = 0 
    
    config = read_config_file(config_file)
    
    for file in glob.glob(os.path.join(path, '*.flextext')):
        
        aligned_dicts = []
        phrase_list = []
        letter_index = 0
        token_index = 0
        tier_list = []
        
        
        pre_doc = str(doc_count)
        doc_count += 1
        post_doc = str(doc_count)
        
        document = path_leaf(file)
        main_text = config[document]['mainText']
        
        f = open(file)
        print ('\nfile: ' + document + ' ---------'+ str(file_index))
        print (main_text)
        
        soup = BeautifulSoup(f, 'html5lib')
        phrase_list = soup.findAll('phrase')
        for phrase in phrase_list[:]:
            phrase_dict = {'file_index': file_index,
                           'token_letter_list': [],
                           'file_name': document,
                           'span_last_letter': 0,
                           'span_first_letter': 0,
                           'token_ID_list': [],
                           }
            token_list = []
            title_list = phrase.findAll("word")
            
            for x in title_list:
                item_list = (x.findAll('item'))
                main_item_list = x.findAll('item', {'type' : [main_text,'punct']})
                #print (str(main_item_list))
                #main_token = str(item_list[0].contents[0])
                main_token = str(main_item_list[0].contents[0])
                                 
                
                token_list.append(main_token)
                letter_index_end = letter_index + len(main_token) - 1
                token_index += 1
                secondary_tiers = []
                
                for each in item_list:
                    
                    name_of_tier = str(each['type'])
                    name_of_tier = config[document][name_of_tier]
                    
                    if name_of_tier not in tier_list:
                        tier_list.append(str(name_of_tier))
                    
                    # add all additonal tiers
                    
                    # in case of empty strings
                    if len(each.contents) > 0:
                        token = each.contents[0]
                    else:
                        token = ' '
                        
                    secondary_tiers.append([token, name_of_tier, token_index, letter_index, letter_index_end])

                for tier in secondary_tiers:
                    if tier[1] != main_text:
                        spanName = str(token_index) + 'addTexT'
                        
                        write_text(node_index,
                                   file_index,
                                   spanName,
                                   tier[1],
                                   tier[3],
                                   tier[4],
                                   tier[2],
                                   tier[2],
                                   tier[0])
                        
                        node_index += 1
                        # ---------------------------------------------
                    else:
                        print ('YES')
                    
                    
                phrase_dict['token_letter_list'].append([letter_index, letter_index_end])
                phrase_dict['token_ID_list'].append(token_index)
                letter_index = letter_index_end + 1

            phrase_dict['span_first_letter'] = phrase_dict['token_letter_list'][0][0]     
            phrase_dict['span_last_letter'] = phrase_dict['token_letter_list'][-1][-1] 
            phrase_dict['token_list'] = token_list
            phrase_dict['anno_type'] = 'align_anno'
            phrase_dict['annotation_value'] = ' '.join(token_list)
            #phrase_dict['tier_ID'] = str(tier_list[0])
            phrase_dict['tier_ID'] = 'phrase'
            aligned_dicts.append(phrase_dict)
            phrase_list.append(' '.join(token_list))
          
        for each in aligned_dicts:
   
            call_index = 0
            for token in each['token_list']:
                
                spanName = 'sSpan' + str(each['token_ID_list'][call_index])
                
                write_span(node_index,
                           each['file_index'],
                           spanName,
                           str(each['token_letter_list'][call_index][0]),
                           str(each['token_letter_list'][call_index][1]),
                           each['token_ID_list'][call_index],
                           each['token_ID_list'][call_index],
                           each['token_list'][call_index])
                
                node_index += 1
                
                # write to file for each token
                write_to_file(nodeAnnisOut,
                              str(node_index),
                              '0',
                              each['file_index'],
                              'default_ns',
                              'sTok' + str(each['token_ID_list'][call_index] + 1),
                              str(each['token_letter_list'][call_index][0]),
                              str(each['token_letter_list'][call_index][1]),
                              str(each['token_ID_list'][call_index]),
                              str(each['token_ID_list'][call_index]),
                              str(each['token_ID_list'][call_index]),
                              'NULL',
                              'NULL',
                              each['token_list'][call_index],
                              'FALSE')
 
                call_index += 1
                node_index += 1

            spanName = 'sText' + str(each['token_ID_list'][0])
   
            # write to file for each text
            write_text(str(node_index),
                      each['file_index'],
                      spanName,
                      str(each['tier_ID']),
                      str(each['span_first_letter']),
                      str(each['span_last_letter']),
                      str(each['token_ID_list'][0]),
                      str(each['token_ID_list'][-1]),
                      str(each['annotation_value']))
            
            node_index += 1    
      
            
        fullText = " ".join(phrase_list)
            
        write_to_file(textAnnisOut,
                      str(file_index), 
                      '0', 
                      document, 
                      fullText)
             
    
        # write one line per file to corpus.annis
        write_to_file(corpusAnnisOut,
                  str(file_index), 
                  document, 
                  'DOCUMENT', 
                  'NULL', 
                  pre_doc, 
                  post_doc, 
                  'FALSE')
        
        doc_count += 1
        file_index += 1
        #print (str(tier_list))
        
    # write final line to corpus.annis                 
    write_to_file(corpusAnnisOut,
                  str(file_index), 
                  corpus_name, # this needs to be variable
                  'CORPUS', 
                  'NULL', 
                  '0', 
                  str(doc_count), 
                  'TRUE')
        
if __name__== "__main__":
    
    corpus_name = 'Super_corpus' # will be the corpus name in ANNIS
    
    # open all output files
    corpusAnnisOut = open(out_path + 'corpus.annis', 'w', encoding='utf-8')
    textAnnisOut = open(out_path + 'text.annis', 'w', encoding='utf-8')
    nodeAnnisOut = open(out_path + 'node.annis', 'w', encoding='utf-8')
    node_annotationAnnisOut = open(out_path + 'node_annotation.annis', 'w', encoding='utf-8')
    componentAnnisOut = open(out_path + 'component.annis', 'w', encoding='utf-8')
    rankAnnisOut = open(out_path + 'rank.annis', 'w', encoding='utf-8')
    resolve_vis_mapAnnisOut = open(out_path + 'resolver_vis_map.annis', 'w', encoding='utf-8')
    annisVersionOut = open(out_path + 'annis.version', 'w', encoding='utf-8')
    corpusAnnotationOut = open(out_path + 'corpus_annotation.annis', 'w', encoding='utf-8')
    edgeAnnotationOut = open(out_path + 'edge_annotation.annis', 'w', encoding='utf-8')
      
    format_maker()
    
    # create resolve_visual_map file
    write_to_file(resolve_vis_mapAnnisOut,
              corpus_name + 
              '\tNULL' +
              '\tdefault_ns' +
              '\tnode' +
              '\tgrid' + 
              '\tgrid (default_ns)' +
              '\thidden' + 
              '\t1' + 
              '\tNULL')
    
    # create annis.version file
    annisVersionOut.write('3.3')
    
    close_all_files()  
    
    print ('++ DONE! ++')    