# Description: clusterize previously extracted tokens.

# Include required libraries
from collections import Counter
from configurator import *
import os
import shutil
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from tokenizer import tokenize_words

vectorizer = TfidfVectorizer()
K = 1 # Number of clusters (more than 1 is currently not supported)

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

# Extract tokens from given text file and filter tokens that do not
# exist in given corpus' tokens.
def extract_tokens(tokens_file_path, corpus_tokens):
    tokens_file = open(tokens_file_path, 'r')
    tokens_file_lines = tokens_file.read().splitlines()
    tokens_file.close()

    tokens = []
    for line in tokens_file_lines:
        for token in line.split('|'):
            if token in corpus_tokens:
                tokens += [token]
    
    return tokens

# Clusterize given tokens and save result into cluster file of given recording
def clusterize_tokens(recording_id, tokens):
    # tf-idf vectors with terms
    vectors = vectorizer.fit_transform([' '.join(tokens)])
    terms = vectorizer.get_feature_names_out()
    # Flat clustering using KMeans
    km = KMeans(n_clusters = K)
    km.fit(vectors)
    # Save centroid into file (term:tf-idf pairs) for next step of pipeline
    cluster_file = open(clusters_folder + recording_id + '.txt', 'w')
    for centroid in km.cluster_centers_:
        for term, vector in zip(terms, centroid):
            cluster_file.write(term + '|' + str(vector) + '\n')
    cluster_file.close()    

# Save temporary tokens files to database and return True if at
# least one tokens file was saved to database
def save_tokens():
    tokens_saved = False
    for file_name in os.listdir(tokens_folder):
        file_path = tokens_folder + file_name
        file_name_parts = os.path.splitext(file_name)
        if file_name_parts[1] != '.final':
            continue

        res_tokens_file_path = res_tokens_folder + file_name_parts[0] + '.txt'
        if os.path.isfile(res_tokens_file_path):
            os.remove(res_tokens_file_path) # Delete res tokens file if already exists

        tokens_file_path = tokens_folder + file_name_parts[0] + '.txt'
        shutil.move(tokens_file_path, res_tokens_folder)
        os.remove(file_path) # Remove .final file

        tokens_saved = True

    return tokens_saved

# Program main function
def clusterize():
    tokens_to_clusterize = save_tokens()
    if not tokens_to_clusterize:
       return

    corpus_tokens = tokenize_words(get_corpus())

    for tokens_file_name in os.listdir(res_tokens_folder):
        tokens_file_name_parts = os.path.splitext(tokens_file_name)
        recording_id = tokens_file_name_parts[0].split('_')[0]
        tokens_file_path = res_tokens_folder + tokens_file_name_parts[0] + '.txt'

        tokens = extract_tokens(tokens_file_path, corpus_tokens) # Extract tokens
        if tokens:
            clusterize_tokens(recording_id, tokens) # K-means clustering

        # Save .final file for each new cluster file to inform worker that clusterizing is completed
        open(clusters_folder + tokens_file_name_parts[0] + '.final', 'w').close()

# Program's main
if __name__ == '__main__':
    while True:
        clusterize()