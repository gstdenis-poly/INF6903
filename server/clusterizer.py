# Description: extract, tokenize, stem, remove stop words and tokens without 
#              at least one letter or one number and clusterize text previously 
#              detected in uploaded images.

# Include required libraries
from configurator import *
import json
import nltk
import numpy as np
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('words')
from nltk.corpus import stopwords, words
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize
import os
import shutil
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import sys

stemmer = PorterStemmer()
stop_words = stopwords.words('english')
vectorizer = TfidfVectorizer(stop_words = stop_words)
K = 1 # Number of clusters (more than 1 is currently not supported)

def has_alpha_num(string):
    for c in string:
        if c.isalnum():
            return True
    return False

# Prepare tokens for a given documents
def prepare_tokens(document):
    tokens = word_tokenize(document.lower()) # Tokens of lowercased document
    tokens = [stemmer.stem(t) for t in tokens] # Porter stemmed tokens
    # Tokens with at least one alphanumeric character
    tokens = [t for t in tokens if has_alpha_num(t)]

    return tokens

# Program main function
def clusterize():
    clusterizer_worker_folder = detections_folder + 'worker' + clusterizer_worker_id + '/'
    if not os.path.exists(clusterizer_worker_folder):
        return
    
    english_corpus_tokens = prepare_tokens(' '.join(words.words()))

    ips_folder = clusterizer_worker_folder + 'ip/'
    ocrs_folder = clusterizer_worker_folder + 'ocr/'
    for ocr_file_name in os.listdir(ocrs_folder):
        ocr_file_name_parts = os.path.splitext(ocr_file_name)
        if not os.path.isfile(clusterizer_worker_folder + ocr_file_name_parts[0] + '.final') or \
           ocr_file_name_parts[-1] != '.json':
            continue

        ocr_file_path = ocrs_folder + ocr_file_name
        ocr_file = open(ocr_file_path, 'r')
        ocr_json = json.loads(ocr_file.read())
        ocr_file.close()

        ocr_tokens = []
        for ocr_content in ocr_json['texts']:
            ocr_tokens += prepare_tokens(ocr_content['content'])
        ocr_tokens = [t for t in ocr_tokens if t in english_corpus_tokens]

        recording_id = ocr_file_name_parts[0].split('_')[0]
        cluster_file_name = recording_id + '.txt'
        cluster_file_path = clusters_folder + cluster_file_name

        km_init = 'k-means++' # Default init parameter for KMeans
        if os.path.exists(cluster_file_path):
            cluster_lock_file_path = clusters_folder + recording_id + '.lock'
            if os.path.isfile(cluster_lock_file_path):
                continue # Skip iteration if cluster file is locked by another worker
            else:
                open(cluster_lock_file_path, 'x').close() # Lock file

            # A cluster already exists so we init KMeans with its centroid
            cluster_file = open(cluster_file_path, 'r')
            cluster_vectors = cluster_file.read().splitlines()
            cluster_file.close()
            os.remove(cluster_lock_file_path) # Remove .lock file

            km_init = np.array([[float(v.split('|')[-1]) for v in cluster_vectors]])
            
        # tf-idf vectors with terms
        vectors = vectorizer.fit_transform([' '.join(ocr_tokens)])
        terms = vectorizer.get_feature_names_out()
        # Match shape of vectors and km_init if necessary
        if km_init != 'k-means++':
            padding = vectors.shape[1] - km_init.shape[1]
            if padding > 0:
                km_init = np.pad(km_init, ((0, 0), (0, padding)))
            elif padding < 0:
                vectors = np.pad(vectors.toarray(), ((0, 0), (0, abs(padding))))
        # Flat clustering using KMeans
        km = KMeans(n_clusters = K, init = km_init)
        km.fit(vectors)
    
        # Save centroid into file (term:tf-idf pairs) for next step of pipeline
        cluster_file = open(cluster_file_path, 'w')
        for centroid in km.cluster_centers_:
            for term, vector in zip(terms, centroid):
                cluster_file.write(term + '|' + str(vector) + '\n')
        cluster_file.close()

        # Remove detections files
        os.remove(ocr_file_path)
        os.remove(ocrs_folder + ocr_file_name_parts[0] + '.png')
        os.remove(ips_folder + ocr_file_name_parts[0] + '.json')
        os.remove(ips_folder + ocr_file_name_parts[0] + '.jpg')
        os.remove(clusterizer_worker_folder + ocr_file_name_parts[0] + '.final')

# Program's main
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Wrong arguments')
    else:
        clusterizer_worker_id = sys.argv[1]
        while True:
            clusterize()