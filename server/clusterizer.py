# Description: extract, tokenize, stem, remove stop words and clusterize 
#              text previously detected in uploaded images.

# Include required libraries
from collections import Counter
from configurator import *
from filelock import FileLock
import json
import nltk
import numpy as np
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize
import os
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

stemmer = PorterStemmer()
stop_words = stopwords.words('french') + stopwords.words('english')
vectorizer = TfidfVectorizer(stop_words = stop_words)
K = 1 # Number of clusters (more than 1 is currently not supported)

def is_alphabetical(string):
    for c in string:
        if not c.isalpha():
            return False
    return True

# Return account type of given account name
def get_account_type(acc_name):
    acc_type = None
    acc_file_path = accounts_folder + acc_name + '.txt'
    acc_file = open(acc_file_path, 'r')
    acc_file_lines = acc_file.read().splitlines()
    acc_file.close()

    for line in acc_file_lines:
        line_infos = line.split('|')
        if line_infos[0] == 'acc_type':
            acc_type = line_infos[1]
            break

    return acc_type

# Update terms in corpus document of given recording id with given words.
def update_corpus(recording_id, words):
    terms = set(words)
    
    rec_document_file_path = corpus_folder + recording_id + '.txt'
    if os.path.isfile(rec_document_file_path):
        rec_document_file = open(rec_document_file_path, 'r')
        rec_document_words = rec_document_file.read().split('|')
        rec_document_file.close() 

        terms = terms.union(set(rec_document_words))

    rec_document_file = open(rec_document_file_path, 'w')
    rec_document_file.write('|'.join(terms))
    rec_document_file.close()

# Get full corpus in database and keep only the terms that are unique
# among different recordings of the same account.
def get_corpus():
    accounts_terms_counter = {}
    for document_name in os.listdir(corpus_folder):
        account = document_name.split('-')[0]
        if account not in accounts_terms_counter:
            accounts_terms_counter[account] = Counter()

        document_file = open(corpus_folder + document_name, 'r')
        document_terms = document_file.read().split('|')
        document_file.close()

        accounts_terms_counter[account] += Counter(document_terms)

    corpus = []
    for account in accounts_terms_counter:
        for term in accounts_terms_counter[account]:
            if accounts_terms_counter[account][term] == 1:
                corpus += [term]

    return corpus

# Return lowercased and stemmed tokens for given words, non alphanumeric
# are excluded.
def prepare_tokens(words):
    tokens = [w for w in words if is_alphabetical(w)] # Tokens of alphabetical words only
    tokens = [t.lower() for t in tokens] # Tokens of lowercased words
    tokens = [stemmer.stem(t) for t in tokens] # Porter stemmed tokens
    return tokens

# Extract tokens from given ocr detection file. If the account related to the
# given recording id is of type 'provider', its corpus is updated. A token must
# exists in database corpus to be returned.
def extract_ocr_tokens(recording_id, ocr_file_path):
    ocr_file = open(ocr_file_path, 'r')
    ocr_json = json.loads(ocr_file.read())
    ocr_file.close()

    ocr_words = []
    for ocr_content in ocr_json['texts']:
        ocr_words += word_tokenize(ocr_content['content'])

    account = recording_id.split('-')[0]
    if get_account_type(account) == 'provider':
        update_corpus(recording_id, ocr_words)
    
    ocr_tokens = prepare_tokens(ocr_words)
    corpus_tokens = prepare_tokens(get_corpus())
    ocr_tokens = [t for t in ocr_tokens if t in corpus_tokens]
    
    return ocr_tokens

# Clusterize given tokens and save result into given cluster file
def clusterize_ocr(ocr_tokens, cluster_file_path):
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
    # Increment number of processed frames' images for cluster
    cluster_frames_images_processed = 1
    cluster_tmp_file_path = clusters_folder + recording_id + '.tmp'
    cluster_tmp_file = None
    if os.path.isfile(cluster_tmp_file_path):
        cluster_tmp_file = open(cluster_tmp_file_path, 'r+')
        cluster_frames_images_processed = int(cluster_tmp_file.read()) + 1
        cluster_tmp_file.seek(0)
    else:
        cluster_tmp_file = open(cluster_tmp_file_path, 'w')

    cluster_tmp_file.write(str(cluster_frames_images_processed))
    cluster_tmp_file.close()
    # Replace .tmp file by .final file to inform worker that cluster is completed
    rec_infos_file_name = recording_id + '_' + recording_infos_file
    rec_infos_file_path = recordings_folder + recording_id + '/' + rec_infos_file_name
    rec_infos_file = open(rec_infos_file_path, 'r')
    rec_infos_file_lines = rec_infos_file.read().splitlines()
    rec_infos_file.close()
    for line in rec_infos_file_lines:
        line_infos = line.split('|')
        if line_infos[0] == 'frames_images_count' and \
           int(line_infos[1]) == cluster_frames_images_processed:
            os.remove(cluster_tmp_file_path)
            open(clusters_folder + recording_id + '.final', 'w')
            return

# Program main function
def clusterize():
    ips_folder = detections_folder + 'ip/'
    ocrs_folder = detections_folder + 'ocr/'
    if not (os.path.exists(ips_folder) or os.path.exists(ocrs_folder)):
        return

    for ocr_file_name in os.listdir(ocrs_folder):
        ocr_file_name_parts = os.path.splitext(ocr_file_name)
        if not os.path.isfile(detections_folder + ocr_file_name_parts[0] + '.final') or \
           ocr_file_name_parts[-1] != '.json':
            continue

        recording_id = ocr_file_name_parts[0].split('_')[0]
        ocr_file_path = ocrs_folder + ocr_file_name
        cluster_file_path = clusters_folder + recording_id + '.txt'

        ocr_tokens = extract_ocr_tokens(recording_id, ocr_file_path) # Extract ocr tokens
        if ocr_tokens:
            clusterize_ocr(ocr_tokens, cluster_file_path) # K-means clustering
        save_progress(recording_id) # Save processed recording's frames

        # Remove detections files
        os.remove(ocr_file_path)
        os.remove(ocrs_folder + ocr_file_name_parts[0] + '.png')
        os.remove(ips_folder + ocr_file_name_parts[0] + '.json')
        os.remove(ips_folder + ocr_file_name_parts[0] + '.jpg')
        os.remove(detections_folder + ocr_file_name_parts[0] + '.final')

# Program's main
if __name__ == '__main__':
    while True:
        clusterize()