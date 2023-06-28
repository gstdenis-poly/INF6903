from aiohttp import web
from configurator import *
import os

async def handle(request):
    html = ''

    recording_id = request.match_info.get('recording_id')
    results_file_path = res_clusters_folder + recording_id + '.txt'

    if os.path.isfile(results_file_path):
        results_file = open(results_file_path, 'r')
        results_file_lines = results_file.read().splitlines()
        results_file.close()

        results = ''
        for i, line in enumerate(results_file_lines):
            line_infos = line.split('|')
            
            res_vid_file_name = line_infos[0] + '_' + screen_recording_file
            res_vid_file_path = '/recordings/' + line_infos[0] + '/' + res_vid_file_name
            results += '<h2>Solution #' + str(i + 1) + ': ' + line_infos[0] + '</h2>' + \
                '<h3>Distance: ' + line_infos[1] + '</h3>' + \
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
app.add_routes([web.get('/solutions/{recording_id}', handle), 
                web.static('/recordings', recordings_folder)])

if __name__ == '__main__':
    web.run_app(app)