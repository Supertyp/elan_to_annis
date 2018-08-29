# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 10:26:49 2018
elan_to_annis.py

@author: Wolfgang Barth
wolfgang.barth@anu.edu.au

transform a bunch of .eaf files into ANNIS file format for import.
uses config_file which is created with elan_annis_config_maker.py

"""

import ast
import glob
import os
import ntpath

# input and output
config_file = 'C:/Path/to/config/file/config_file.conf'
path = 'C:/path/to/all/the/elan/files'
out_path = 'C:/path/to/output/folder/'


def read_config_file(config_file):
    """ read config file into a dictinary
    """
    s = open(config_file, 'r').read()
    configDict = ast.literal_eval(s)
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
    
    write_to_file(node_annotationAnnisOut,
                  nodeCount,
                  'default_ns',
                  'word',
                  token)                        
    
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
        if x.isalpha() or x.isspace() or x.isdigit(): # or x in "!?:;.,'":
            text_list.append(x.lower())

    text = ''.join(text_list)
    text.replace('  ' , ' ')
    return text


def time_line_maker():
    
    """ make a time line for the ELAN file
        return corpus_dict including the timeline and all annotationIDs 
            
            {filename: 
                {time_line: [a1, a2, a3],
                 annotationID: 
                     {key: value,
                      key: value,},},}
    """
    
    # config file created with elan_annis_config_maker
    config = read_config_file(config_file) 
    
    corpus_dict = {} # the main dict to store all data
    
    file_index = -1 # so the first file starts with 0
    
    for file in glob.glob(os.path.join(path, '*.eaf')): # elan file format
        
        file_index += 1
        fileName = path_leaf(file)
        
        with open(file, encoding="utf8") as f:
            
            file_dict = {} # one dict holding all information of a file
            time_dict = {} # one per file used to establish timeline
            time_line = [] 
            
            for line in f:
                if line.startswith('        <TIME_SLOT'):
                    line_split = line.split('="')
                    time_slot_ID = line_split[1].split('"')[0]
                    time_value = line_split[2].split('"')[0]
                    time_dict[time_slot_ID] = time_value
                
                elif line.startswith('    <TIER'):
                    line_split = line.split('="')
                    tier_ID= line_split[-1].split('"')[0] #.replace(' ', '_')
                    tier_ID = config[fileName][tier_ID]
                    
                elif line.startswith('            <ALIGNABLE_ANNOTATION'):
                    line_split = line.split('="')
                    annotation_ID = line_split[1].split('"')[0]
                    time_slot_ref1 = line_split[-2].split('"')[0]
                    time_slot_ref2 = line_split[-1].split('"')[0]
                    annotation_ref = '-'
                    anno_type = 'align_anno'
                
                elif line.startswith('            <REF_ANNOTATION'):
                    line_split = line.split('="')
                    annotation_ID = line_split[1].split('"')[0]
                    annotation_ref = line_split[2].split('"')[0]
                    time_slot_ref1 = file_dict[annotation_ref]['time_slot_ref1']
                    time_slot_ref2 = file_dict[annotation_ref]['time_slot_ref2']
                    anno_type = 'ref_anno'
                    
                elif line.startswith('                <ANNOTATION_VALUE>'):
                    line_split = line.split('>')
                    annotation_value = line_split[1].split('<')[0]
                    annotation_value = clean_string(annotation_value)
                    if len(annotation_value) == 0:
                        annotation_value = '...' # if value is empty there is a error on import
                    token_list = annotation_value.split()
                        
                    time_line.append(annotation_ID)
                    
                    file_dict[annotation_ID] = {'annotation_value': annotation_value,
                                                'time_slot_ref1': time_slot_ref1,
                                                'time_slot_ref2': time_slot_ref2,
                                                'tier_ID' : tier_ID,
                                                'time_value1' : time_dict[time_slot_ref1],
                                                'time_value2' : time_dict[time_slot_ref2],
                                                'anno_type': anno_type,
                                                'letter_count': len(annotation_value),
                                                'annotation_ID': annotation_ID,
                                                'token_list': token_list,
                                                'annotation_ref': annotation_ref,
                                                'file_name': fileName}
   
            file_dict['time_line'] = time_line
            
        corpus_dict[fileName] = file_dict 
        
    return corpus_dict


def sort_time_line(corpus_dict, corpus_name):

    """ order the dialog relevant tiers into a chronological line up
        returns two lists:
            1. aligned list of relevant dialog tiers
            2. other tiers
    """
    
    doc_count = 1
    doc_ID = 0
    token_ID = -1
    node_index = 0
    
    print (str(doc_count) + ' - ' +  str(doc_ID)) 
    
    config = read_config_file(config_file)
   
    for document in corpus_dict:

        print ('document: ' + document)
        
        dialog = config[document]['mainText']
        print (dialog)
        delete_list = config[document]['delete']

        # to turn into single string per file
        fullTextList = []
        print (str(doc_count) + ' - ' +  str(doc_ID))
        # counting the previous and following file ids
        pre_doc = str(doc_count)
        doc_count += 1
        post_doc = str(doc_count)
        
        dialog_list = []
        dialog_order = {}
        aligned_dicts = []
        other_tiers = []
        
        letter_index = 0
     
        # write one line per file in the folder pre & post increment by one
        write_to_file(corpusAnnisOut,
                      str(doc_ID), 
                      document, 
                      'DOCUMENT', 
                      'NULL', 
                      pre_doc, 
                      post_doc, 
                      'FALSE')
        
        doc_count += 1
        
        for annotation_ID in corpus_dict[document]['time_line']:
            corpus_dict[document][annotation_ID]['file_index'] = doc_ID
            
            if corpus_dict[document][annotation_ID]['tier_ID'] in dialog:
                
                dialog_order[corpus_dict[document][annotation_ID]['time_value1']] = annotation_ID
                
                dialog_list.append(int(corpus_dict[document][annotation_ID]['time_value1']))
            
            else:
                if corpus_dict[document][annotation_ID]['tier_ID'] not in delete_list:
                    
                    other_tiers.append(corpus_dict[document][annotation_ID])
            
        dialog_list.sort()
        
        #align all dicts chronologically
        for x in dialog_list:
            chrono_id = dialog_order[str(x)]
            aligned_dicts.append(corpus_dict[document][chrono_id])
        
        for each in aligned_dicts:
            each['span_first_letter'] = str(letter_index)
            span_length = len(each['annotation_value'])
            letter_index += span_length
            each['span_last_letter'] = str(letter_index)
            letter_index += 1

        for each in aligned_dicts:
            token_list = each['annotation_value'].split()
            token_ID_list = []
            token_letter_list = []
            first_letter = int(each['span_first_letter'])
            for toks in token_list:
                token_ID += 1
                token_ID_list.append(token_ID)
                token_letter_list.append([first_letter, int(first_letter) + len(toks)])
                first_letter += len(toks) + 1
            
            each['token_letter_list'] = token_letter_list
            each['token_ID_list'] = token_ID_list
  
            fullTextList.append(each['annotation_value'])
            
        fullText = " ".join(fullTextList)
            
        write_to_file(textAnnisOut,
                      str(doc_ID), 
                      '0', 
                      document, 
                      fullText)

        """ make all file entries for the aligned tiers and then for the other_tiers
        which always refer to the aligned tiers
        all tiers which don'r refer to a aligned tier are dropped.
        """
    
        referee_dict = {}
           
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
            
            referee_dict[each['annotation_ID']] = each
        
        """
        for each in aligned_dicts:
            print (' ')
            for k, v in each.items():
                print (str(k) + ': ' + str(v))
        
        
        for each in other_tiers:
            print (' ')
            for k, v in each.items():
                print (str(k) + ': ' + str(v)) 
        """
        
        for each in other_tiers:
            
            if each['annotation_ref'] in referee_dict:
                
                spanName = 'sref' + str(referee_dict[each['annotation_ref']]['token_ID_list'][0])
             
                # write to file for each text
                write_text(str(node_index),
                           each['file_index'],
                           spanName,
                           str(each['tier_ID']),
                           str(referee_dict[each['annotation_ref']]['span_first_letter']),
                           str(referee_dict[each['annotation_ref']]['span_last_letter']),
                           str(referee_dict[each['annotation_ref']]['token_ID_list'][0]),
                           str(referee_dict[each['annotation_ref']]['token_ID_list'][-1]),
                           str(each['annotation_value']))
                
                node_index += 1
        
        doc_ID += 1

    # write one line for the top_level corpus 
    write_to_file(corpusAnnisOut,
                  str(doc_ID), 
                  corpus_name, # this needs to be variable
                  'CORPUS', 
                  'NULL', 
                  '0', 
                  str(doc_count), 
                  'TRUE')


def make_all_files(node_index, aligned_dicts, other_tiers):
    
    """ make all file entries for the aligned tiers and then for the other_tiers
        which always refer to the aligned tiers
        all tiers which don'r refer to a aligned tier are dropped.
    """
    
    referee_dict = {}
       
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
        
        referee_dict[each['annotation_ID']] = each
        
    
    for each in other_tiers:
        
        if each['annotation_ref'] in referee_dict :
            
            spanName = 'sref' + str(referee_dict[each['annotation_ref']]['token_ID_list'][0])
         
            # write to file for each text
            write_text(str(node_index),
                       each['file_index'],
                       spanName,
                       str(each['tier_ID']),
                       str(referee_dict[each['annotation_ref']]['span_first_letter']),
                       str(referee_dict[each['annotation_ref']]['span_last_letter']),
                       str(referee_dict[each['annotation_ref']]['token_ID_list'][0]),
                       str(referee_dict[each['annotation_ref']]['token_ID_list'][-1]),
                       str(each['annotation_value']))
            
            node_index += 1
        
    return node_index
               
if __name__== "__main__": 
    
    config = read_config_file(config_file)
    
    corpus_name = config['corpus_name'] # the folder name will be the corpus name
    
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
      
    corpus_dict  = time_line_maker()
    sort_time_line(corpus_dict, corpus_name)
    
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