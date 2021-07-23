import nltk
import csv
import re
import os
from nltk.corpus import stopwords
from nltk.tag.stanford import StanfordPOSTagger
from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic
import sys
from itertools import islice

import gensim
import gensim.models.keyedvectors as word2vec

path_to_model = "../Python/FE_SAFE.py/stanford-postagger-2016-10-31/models/english-bidirectional-distsim.tagger"
path_to_jar = "../Lab/Python/FE_SAFE.py/stanford-postagger-2016-10-31/stanford-postagger.jar"

st_tagger = StanfordPOSTagger(path_to_model, path_to_jar)

def penn_to_wn(tag):
    """ Convert between a Penn Treebank tag to a simplified Wordnet tag """
    if tag.startswith('N'):
        return 'n'
 
    if tag.startswith('V'):
        return 'v'
 
    if tag.startswith('J'):
        return 'a'
 
    if tag.startswith('R'):
        return 'r'
 
    return 'n'
 
def tagged_to_synset(word, tag):
    wn_tag = penn_to_wn(tag)
    if wn_tag is None:
        return None
    try:
        return wn.synsets(word, wn_tag)[0]
    except:
        return None
 
def sentence_similarity(sentence1, sentence2):
    """ compute the sentence similarity using Wordnet """
    # Tokenize and tag
    
    # sentence1 = pos_tag(word_tokenize(sentence1))
    sentence1=st_tagger.tag(word_tokenize(sentence1))
    
    # sentence2 = pos_tag(word_tokenize(sentence2))
    sentence2=st_tagger.tag(word_tokenize(sentence2))

    
    # Get the synsets for the tagged words
    #################################################

    # synsets1=[]
    # synsets2=[]
    # for tagged_word in sentence1:
    #     print(tagged_word)
    #     tagged_word = list(tagged_word)
    #     synsets1.append(tagged_to_synset(tagged_word[0],tagged_word[1]))
    # for tagged_word in sentence2:
    #     print(tagged_word)
    #     tagged_word = list(tagged_word)
    #     print(tagged_word)
    #     synsets2.append(tagged_to_synset(tagged_word[0],tagged_word[1]))

    # The code above is the elaboration of code below
    synsets1 = [tagged_to_synset(*tagged_word) for tagged_word in sentence1]
    synsets2 = [tagged_to_synset(*tagged_word) for tagged_word in sentence2]
 
    # Filter out the Nones in the synonym set
    synsets1 = [ss for ss in synsets1 if ss]
    synsets2 = [ss for ss in synsets2 if ss]
 
    score, count = 0.0, 0
 
###########################################################################
    # for syn1 in synsets1:
    #     arr_simi_score = []
    #     print('=========================================')
    #     print(syn1)
    #     print('----------------')
    # for syn2 in synsets2:
    #     print(syn2)
    #     simi_score = syn1.path_similarity(syn2)
    #     print(simi_score)
    #     if simi_score is not None:
    #         arr_simi_score.append(simi_score)
    #         print('----------------')
    #         print(arr_simi_score)
    #     if(len(arr_simi_score) > 0):
    #         best = max(arr_simi_score)
    #         print(best)
    #         score += best
    #         count += 1
    #         # Average the values
    #         print('score: ', score)
    #         print('count: ', count)
    #         score /= count

###########################################################################

    for syn1 in synsets1:
        arr_simi_score = []
        # print('=========================================')
        print("Each word from Synonym se1",syn1)
        # print('----------------')
        for syn2 in synsets2:
            print("Each word from Synonym se2",syn2)
            # simi_score = syn1.path_similarity(syn2)
            simi_score = syn1.wup_similarity(syn2)
            print("word to word path_similarity score",simi_score)
            if simi_score is not None:
                arr_simi_score.append(simi_score)
                print('----------------')
                print(arr_simi_score)
        if(len(arr_simi_score) > 0):
            best = max(arr_simi_score)
            print("best score so far", best)
            score += best
            count += 1
    # Average the values
    print('score: ', score)
    print('count: ', count)
    if count!=0:
        score /= count
    else:
        score=0.0
    return score



def text_cleaning(app_desc):
    app_desc = str(app_desc)
    app_desc=app_desc.replace('\\n','')  # Cool Cleaning stuff use of '\\'
    app_desc=re.sub(r'([--:\w?@%&+~#=]*\.[a-z]{2,4}\/{0,2})((?:[?&](?:\w+)=(?:\w+))+|[--:\w?@%&+~#=]+)?', '', app_desc, flags=re.MULTILINE)
    app_desc = re.sub(r'<.*?>', ' ', app_desc)
    app_desc=re.sub(r'[^[a-zA-z ]+]*', ' ',app_desc)
    app_desc=re.sub(r'[^\w]', ' ',app_desc)
    app_desc = re.sub(r'\s+', ' ', app_desc).strip()
    return app_desc


 
"""STOP WORD removal"""
def stop_word_removal(text):
    stop_words = set(stopwords.words('english')) 
    # word_tokens = word_tokenize(text) 
    text = [w for w in text if not w in stop_words] 
    # text=str(text)
    print(text)
    return text 




""" Writing a file by using writer object"""
def fileopener(filename_):

    csvfile=open(filename_,'a',newline='')
    fieldnames = ['WN_Feature_No','WN_Feature','Rev_Feature','Rev_Sentiment', 'Similarity_Score']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    return writer   

if __name__ == '__main__':
    
##############FACEBOOK Target App Semantic Grouping ##########################################

    file_name='..\\Research\\Experiments\\RQ2\\facebook\\feature_grouping\\feature_groups.csv'
    csv_writer=fileopener(file_name)
    count=0
    f_desc= open('..\\Research\\Experiments\\RQ2\\facebook\\facebook_func_features.txt', encoding="utf-8", errors="ignore")
    
    similarity_threshold =0.6
    

    des_text = f_desc.readlines()
    for _feature in desc_text:
        count=count+1
        func_feature=text_cleaning(_feature)
        print(count,": func_feature")
        with open('..\\Research\\Experiments\\RQ2\\facebook\\feature_classification\\popular_features.csv', encoding="utf-8", errors="ignore") as file:
            f_cd_feature_file=csv.DictReader(file)
            for line in f_cd_feature:
                feature_set = line["Features"].split(",")
                for feature in feature_set:
                    cd_feature=text_cleaning(feature)
                    print(cd_feature)
                    simi_score=sentence_similarity(func_feature,cd_feature)
                    if simi_score>=similarity_threshold:
                        csv_writer.writerow({'fn_feature_No':count,'fn_feature':func_feature,'cd_Feature':cd_feature,'Similarity_Score':simi_score})
            
                    
    #                 highest_score=app_simi_score
    #                 print("Score/feature: ",highest_score)

    #         # print("sim(description_1,description_2) = ", app_simi_score,"/1.")
    #         print("+++Highest Score/review: ",highest_score)
    #         