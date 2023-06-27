# Description: extract, tokenize, stem, remove stop words and clusterize 
#              text previously detected in uploaded images.

# Include required libraries
from configurator import *
from filelock import FileLock
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
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import sys

stemmer = PorterStemmer()
stop_words = stopwords.words('english')
vectorizer = TfidfVectorizer(stop_words = stop_words)
K = 1 # Number of clusters (more than 1 is currently not supported)

# Return lowercased and stemmed tokens of a given document
def prepare_tokens(document):
    tokens = word_tokenize(document.lower()) # Tokens of lowercased document
    tokens = [stemmer.stem(t) for t in tokens] # Porter stemmed tokens
    return tokens

english_corpus_tokens = prepare_tokens(' '.join(words.words()))

# Extract tokens from given ocr detection file
def extract_ocr_tokens(ocr_file_path):
    ocr_file = open(ocr_file_path, 'r')
    ocr_json = json.loads(ocr_file.read())
    ocr_file.close()
    ocr_tokens = []
    for ocr_content in ocr_json['texts']:
        ocr_tokens += prepare_tokens(ocr_content['content'])
    ocr_tokens = [t for t in ocr_tokens if t in english_corpus_tokens]
    
    return ocr_tokens

# Clusterize tokens of given ocr detection file and save result into given cluster file
def clusterize_ocr(ocr_file_path, cluster_file_path):
    ocr_tokens = extract_ocr_tokens(ocr_file_path)
    # Set k-means initial cluster
    km_init = 'k-means++' # Default init parameter for KMeans
    if os.path.exists(cluster_file_path):
        # A cluster already exists so we init KMeans with its centroid
        cluster_file = open(cluster_file_path, 'r')
        cluster_vectors = cluster_file.read().splitlines()
        cluster_file.close()
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

# Save progress of clustering given recording's frames
def save_progress(recording_id):
    # Increment number of processed frames for cluster
    cluster_frames_processed = 1
    cluster_tmp_file_path = clusters_folder + recording_id + '.tmp'
    if os.path.isfile(cluster_tmp_file_path):
        cluster_tmp_file = open(cluster_tmp_file_path, 'r+')
        cluster_frames_processed = int(cluster_tmp_file.read()) + 1
        cluster_tmp_file.seek(0)
    else:
        cluster_tmp_file = open(cluster_tmp_file_path, 'w')
        
    cluster_tmp_file.write(str(cluster_frames_processed))
    cluster_tmp_file.close()
    # Replace .tmp file by .final file to inform worker that cluster is completed
    rec_infos_file_name = recording_id + '_' + recording_infos_file
    rec_infos_file_path = recordings_folder + recording_id + '/' + rec_infos_file_name
    rec_infos_file = open(rec_infos_file_path, 'r')
    rec_infos_file_lines = rec_infos_file.read().splitlines()
    rec_infos_file.close()
    for line in rec_infos_file_lines:
        line_infos = line.split('|')
        if line_infos[0] == 'relevant_frames_count' and \
           int(line_infos[1]) == cluster_frames_processed:
            os.remove(cluster_tmp_file_path)
            open(clusters_folder + recording_id + '.final', 'x').close()
            break

# Program main function
def clusterize():
    clusterizer_worker_folder = detections_folder + 'worker' + clusterizer_worker_id + '/'
    if not os.path.exists(clusterizer_worker_folder):
        return

    ips_folder = clusterizer_worker_folder + 'ip/'
    ocrs_folder = clusterizer_worker_folder + 'ocr/'
    for ocr_file_name in os.listdir(ocrs_folder):
        ocr_file_name_parts = os.path.splitext(ocr_file_name)
        if not os.path.isfile(clusterizer_worker_folder + ocr_file_name_parts[0] + '.final') or \
           ocr_file_name_parts[-1] != '.json':
            continue

        recording_id = ocr_file_name_parts[0].split('_')[0]
        ocr_file_path = ocrs_folder + ocr_file_name
        cluster_file_path = clusters_folder + recording_id + '.txt'

        # Lock cluster files to avoid conflict with other worker
        cluster_lock_file_path = clusters_folder + recording_id + '.lock'
        with FileLock(cluster_lock_file_path):
            clusterize_ocr(ocr_file_path, cluster_file_path) # K-means clustering
            save_progress(recording_id) # Save processed recording's frames
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