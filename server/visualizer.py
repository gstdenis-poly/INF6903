# Description: Http server providing Web pages for visualizing results.

# Include required libraries
from aiohttp import web
from configurator import *
import functools
import json
import os

# Handle http requests to index page
async def handle_index(request):
    html = ''

    account_id = request.match_info.get('account_id')
    requests = ''
    for rec_folder in os.listdir(recordings_folder):
        if account_id not in rec_folder:
            continue

        req_vid_file_name = rec_folder + '_' + screen_recording_file
        req_vid_file_path = '/recordings/' + rec_folder + '/' + req_vid_file_name
        requests += '<h2><a href="/solutions/' + rec_folder + '">Request: ' + rec_folder + '</a></h2>' + \
            '<video style="width:100%" controls src="' + req_vid_file_path + '" type="video/mp4"></video>'

    html = '<!DOCTYPE html>' + \
        '<html>' + \
            '<head>' + \
                '<title>Solutions</title>' + \
            '</head>' + \
            '<body>' + \
                '<h1>Welcome ' + account_id + ' !</h1>' + \
                requests + \
            '</body>' + \
        '</html>'
   
    return web.Response(text = html, content_type = 'text/html')

# Get all account registered on database
def get_accounts():
    accounts = []
    for account_file_name in os.listdir(accounts_folder):
        account_file_path = accounts_folder + account_file_name
        account_file = open(account_file_path, 'r')
        account_file_lines = account_file.read().splitlines()
        account_file.close()

        account = {}
        for line in account_file_lines:
            line_parts = line.split('|')
            account[line_parts[0]] = line_parts[1]

        accounts += [account]

    return accounts

# Get all recording infos of given recording in a dictionnary format
def get_recording_infos(recording):
    rec_db_folder = recordings_folder + recording + '/'
    rec_infos_file_path = rec_db_folder + recording + '_' + recording_infos_file
    rec_infos_file = open(rec_infos_file_path, 'r')
    rec_infos_file_lines = rec_infos_file.read().splitlines()
    rec_infos_file.close()

    rec_infos = {}
    for line in rec_infos_file_lines:
        line_parts = line.split('|')
        rec_infos[line_parts[0]] = line_parts[1]

    return rec_infos
        
# Get all global statistics of given recording in a dictionnary format
def get_recording_stats(recording):
    rec_stats_file_path = res_statistics_folder + recording + '.json'
    rec_stats_file = open(rec_stats_file_path, 'r')
    rec_stats = json.loads(rec_stats_file.read())
    rec_stats_file.close()

    return rec_stats

# Get all ergonomic comparison criterias of given recording
def get_recording_criterias(recording):
    criterias = []

    rec_infos = get_recording_infos(recording)
    rec_stats = get_recording_stats(recording)

    criterias += [rec_stats['mouse_events_count']]
    criterias += [rec_stats['keyboard_events_count']]
    criterias += [rec_stats['mouse_events_distance']]
    criterias += [rec_stats['text_elements_count'] / rec_infos['frames_images_count']]
    criterias += [rec_stats['text_sizes_count'] / rec_infos['frames_images_count']]
    criterias += [rec_stats['text_sentiment_score'] / rec_infos['frames_images_count']]
    criterias += [rec_infos['frames_count'] / rec_infos['frame_rate'] * 1000000000] # Duration in nanoseconds

    return criterias

# Compare ergonomic criterias of two providers' solutions given in format 
# recording_id|distance
def cmp_solutions_score(s1, s2):
    s1_rec_id, s2_rec_id = s1.split('|')[0], s2.split('|')[0]
    s1_criterias = get_recording_criterias(s1_rec_id)
    s2_criterias = get_recording_criterias(s2_rec_id)

    s1_score, s2_score = 0, 0
    for s1_criteria, s2_criteria in zip(s1_criterias, s2_criterias):
        if s1_criteria > s2_criteria:
            s1_score += 1
        elif s2_criteria > s1_criteria:
            s2_score += 1
    
    print('S1 score: ' + s1_score + ' ; ' + 'S2 score: ' + s2_score)
    return 1 if s1_score > s2_score else 0 if s1_score == s2_score else -1


# Handle http requests to solutions page
async def handle_solutions(request):
    html = ''

    recording_id = request.match_info.get('recording_id')
    results_file_path = val_clusters_folder + recording_id + '.txt'

    if os.path.isfile(results_file_path):
        results_file = open(results_file_path, 'r')
        results_file_lines = results_file.read().splitlines()
        results_file.close()

        providers_count = len([a for a in get_accounts() if a['acc_type'] == 'provider'])
        cmp_key = functools.cmp_to_key(cmp_solutions_score)
        sorted_result_file_lines = sorted(results_file_lines, key = cmp_key)

        results = ''
        for i, line in enumerate(sorted_result_file_lines):
            if i == providers_count:
                break

            line_infos = line.split('|')
            
            res_vid_file_name = line_infos[0] + '_' + screen_recording_file
            res_vid_file_path = '/recordings/' + line_infos[0] + '/' + res_vid_file_name
            results += '<h2>Solution #' + str(i + 1) + ': ' + line_infos[0] + '</h2>' + \
                '<h3>Score: ' + line_infos[1] + '</h3>' + \
                '<video style="width:100%" controls src="' + res_vid_file_path + '" type="video/mp4"></video>'

        req_vid_file_name = recording_id + '_' + screen_recording_file
        req_vid_file_path = '/recordings/' + recording_id + '/' + req_vid_file_name
        html = '<!DOCTYPE html>' + \
            '<html>' + \
                '<head>' + \
                    '<title>Solutions</title>' + \
                '</head>' + \
                '<body>' + \
                    '<h1>Request: ' + recording_id + '</h1>' + \
                    '<video style="width:100%" controls src="' + req_vid_file_path + '" type="video/mp4"></video>' + \
                    results + \
                '</body>' + \
            '</html>'
   
    return web.Response(text = html, content_type = 'text/html')


app = web.Application()
app.add_routes([web.get('/index/{account_id}', handle_index),
                web.get('/solutions/{recording_id}', handle_solutions), 
                web.static('/recordings', recordings_folder)])

if __name__ == '__main__':
    web.run_app(app)