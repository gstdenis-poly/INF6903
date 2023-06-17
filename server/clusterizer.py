# Description: extract, tokenize, stem, remove stop words and tokens without 
#              at least one letter or one number and clusterize text previously 
#              detected in uploaded images.

# Include required libraries
import os
import json
import nltk
import numpy as np
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

stemmer = PorterStemmer()
stop_words = stopwords.words('french') + stopwords.words('english')
vectorizer = TfidfVectorizer(stop_words=stop_words)
K = 1 # Number of clusters (more than 1 is currently not supported)

def has_alpha_num(string):
    for c in string:
        if c.isalnum():
            return True
    return False

tmp_root = app_root + '/tmp'

while True:
    for folder in os.listdir(tmp_root):
        client_tmp = tmp_root + '/' + folder # tmp of specific client
        ocrs_path = client_tmp + '/detections'
    
    if not os.path.exists(ocrs_path):
        continue

    ocrs = os.listdir(ocrs_path)

    for ocr in ocrs:
        ocr_name = os.path.splitext(ocr)[0]
        ocr_ext = os.path.splitext(ocr)[-1]
        # tmp files' prefix identify one uploaded video
        # tmp files' suffix should be '-X' where X identifies the video's frame
        ocr_prefix = ocr_name.split('-')[0]

        ocr_path = ocrs_path + '/' + ocr
        # One lock file per uploaded video
        lock_file_path = ocrs_path + '/' + ocr_prefix + '.lock'

        if os.path.exists(lock_file_path):
            continue
        elif ocr_ext == '.json':
            lock_file = open(lock_file_path, 'w') # Create .lock file
            lock_file.close()

            ocr_text = open(ocrs_path + '/' + ocr, 'r').read()
            ocr_json = json.loads(ocr_text)

            ocr_tokens = []
            for ocr_content in ocr_json['texts']:
                content = ocr_content['content'].lower() # Lowercased content
                tokens = word_tokenize(content) # Tokens of lowercased content
                tokens = [stemmer.stem(t) for t in tokens] # Porter stemmed tokens
                # Tokens with at least one alphanumeric character
                tokens = [t for t in tokens if has_alpha_num(t)]

                ocr_tokens += tokens

            output_root = app_root + '/database/' + folder + '/clusters'
            if not os.path.exists(output_root):
                os.mkdir(output_root)

            output_file_name = ocr_prefix + '.txt'
            output_file_path = output_root + '/' + output_file_name

            km_init = 'k-means++' # Default init parameter for KMeans
            if os.path.exists(output_file_path):
                # A cluster already exists so we init KMeans with its centroid
                cluster_vectors = open(output_file_path, 'r').read().splitlines()
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
            output_file = open(output_file_path, 'w')
            for centroid in km.cluster_centers_:
                for term, vector in zip(terms, centroid):
                    output_file.write(term + ' | ' + str(vector) + '\n')
                output_file.close()

            os.remove(ocr_path) # Remove .json file
            os.remove(lock_file_path) # Remove .lock file
            break # Process one frame per client at each time