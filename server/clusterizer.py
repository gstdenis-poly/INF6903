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
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize
import os
import shutil
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import sys

stemmer = PorterStemmer()
stop_words = stopwords.words('french') + stopwords.words('english')
vectorizer = TfidfVectorizer(stop_words = stop_words)
K = 1 # Number of clusters (more than 1 is currently not supported)

def has_alpha_num(string):
    for c in string:
        if c.isalnum():
            return True
    return False

# Program main function
def clusterize():
    clusterizer_worker_folder = detections_folder + 'worker' + clusterizer_worker_id + '/'
    if not os.path.exists(clusterizer_worker_folder):
        return

    ocrs_folder = clusterizer_worker_folder + 'ocr/'
    for ocr_file_name in os.listdir(ocrs_folder):
        ocr_file_name_parts = os.path.splitext(ocr_file_name)
        if not os.path.isfile(clusterizer_worker_folder + ocr_file_name_parts[0] + '.final') or \
           ocr_file_name_parts[-1] != '.json':
            continue

        ocr_file_path = ocrs_folder + ocr_file_name
        ocr_text = open(ocr_file_path, 'r').read()
        ocr_json = json.loads(ocr_text)

        ocr_tokens = []
        for ocr_content in ocr_json['texts']:
            content = ocr_content['content'].lower() # Lowercased content
            tokens = word_tokenize(content) # Tokens of lowercased content
            tokens = [stemmer.stem(t) for t in tokens] # Porter stemmed tokens
            # Tokens with at least one alphanumeric character
            tokens = [t for t in tokens if has_alpha_num(t)]

            ocr_tokens += tokens

        cluster_file_name = ocr_file_name_parts[0] + '.txt'
        cluster_file_path = clusters_folder + '/' + cluster_file_name

        km_init = 'k-means++' # Default init parameter for KMeans
        if os.path.exists(cluster_file_path):
            # A cluster already exists so we init KMeans with its centroid
            cluster_vectors = open(cluster_file_path, 'r').read().splitlines()
            km_init = np.array([[float(v.split(' | ')[-1]) for v in cluster_vectors]])

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
    
        # Save centroid into file (term:tf-idf pairs)
        output_file = open(cluster_file_path, 'w')
        for centroid in km.cluster_centers_:
            for term, vector in zip(terms, centroid):
                output_file.write(term + '|' + str(vector) + '\n')
            output_file.close()

        # Keep .json file but remove .png file
        shutil.move(ocr_file_path, clusters_folder + ocr_file_name)
        os.remove(ocrs_folder + ocr_file_name_parts[0] + '.png')

# Program's main
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Wrong arguments')
    else:
        clusterizer_worker_id = sys.argv[1]
        while True:
            clusterize()