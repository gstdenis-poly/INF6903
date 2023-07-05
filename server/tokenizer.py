# Description: extract tokens from text previously detected in 
# uploaded images.

# Include required libraries
from configurator import *
import json
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize
import os

stemmer = PorterStemmer()
stop_words = stopwords.words('french') + stopwords.words('english')

# Return True if given string is fully alphabetical.
def is_alphabetical(string):
    for c in string:
        if not c.isalpha():
            return False
    return True

# Return account type of given account name.
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

# Tokenize given words by removing words with only one character, non alphabetical or
# corresponding to stop words then by porter stemming them.
def tokenize_words(words):
    tokens = [w for w in words if len(w) > 1] # Tokens of 2 characters words minimum
    tokens = [t for t in tokens if is_alphabetical(t)] # Tokens of alphabetical words only
    tokens = [t for t in tokens if t not in stop_words] # Remove stop words from tokens
    tokens = [stemmer.stem(t) for t in tokens] # Porter stemmed tokens
    return tokens

# Extract and save tokens from given det detection file. If the account 
# related to the given recording id is of type 'provider', its corpus is
# updated.
def tokenize_detection(recording_id, det_file_path):
    detection_file = open(det_file_path, 'r')
    detection_json = json.loads(detection_file.read())
    detection_file.close()

    det_words = []
    for det_content in detection_json['texts']:
        det_words += word_tokenize(det_content['content'].lower())

    account = recording_id.split('-')[0]
    if get_account_type(account) == 'provider':
        update_corpus(recording_id, det_words)
    
    det_tokens = tokenize_words(det_words)

    tokens_file_path = tokens_folder + recording_id + '.txt'
    tokens_file = open(tokens_file_path, 'a')
    tokens_file.write('|'.join(det_tokens) + '\n')
    tokens_file.close()

# Save progress of tokenizing given recording's frames
def save_progress(recording_id):
    # Increment number of processed frames' images for recording
    rec_frames_images_processed = 1
    tokens_tmp_file_path = tokens_folder + recording_id + '.tmp'
    tokens_tmp_file = None
    if os.path.isfile(tokens_tmp_file_path):
        tokens_tmp_file = open(tokens_tmp_file_path, 'r+')
        rec_frames_images_processed = int(tokens_tmp_file.read()) + 1
        tokens_tmp_file.seek(0)
    else:
        tokens_tmp_file = open(tokens_tmp_file_path, 'w')

    tokens_tmp_file.write(str(rec_frames_images_processed))
    tokens_tmp_file.close()
    # Replace .tmp file by .final file to inform worker that tokenizing is completed
    rec_infos_file_name = recording_id + '_' + recording_infos_file
    rec_infos_file_path = recordings_folder + recording_id + '/' + rec_infos_file_name
    rec_infos_file = open(rec_infos_file_path, 'r')
    rec_infos_file_lines = rec_infos_file.read().splitlines()
    rec_infos_file.close()
    for line in rec_infos_file_lines:
        line_infos = line.split('|')
        if line_infos[0] == 'frames_images_count' and \
           int(line_infos[1]) == rec_frames_images_processed:
            os.remove(tokens_tmp_file_path)
            open(tokens_folder + recording_id + '.final', 'w')
            return

# Program main function
def tokenize():
    for det_file_name in os.listdir(detections_folder):
        det_file_name_parts = os.path.splitext(det_file_name)
        if not os.path.isfile(detections_folder + det_file_name_parts[0] + '.final') or \
           det_file_name_parts[-1] != '.json':
            continue

        recording_id = det_file_name_parts[0].split('_')[0]
        det_file_path = detections_folder + det_file_name

        tokenize_detection(recording_id, det_file_path) # Extract tokens from detection
        save_progress(recording_id) # Save processed recording's frames

        # Remove detections files
        os.remove(det_file_path)
        os.remove(detections_folder + det_file_name_parts[0] + '.png')
        os.remove(detections_folder + det_file_name_parts[0] + '.final')

# Program's main
if __name__ == '__main__':
    while True:
        tokenize()