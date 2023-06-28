# Description: query on server the validation file related to given 
# query type and recording id.

# Include required librairies
from authenticator import authenticate
import os
import shutil
import subprocess
import sys
import webbrowser

validations_folder = '~/projects/def-gabilode/gstdenis/database/validations/'
recordings_folder = '~/projects/def-gabilode/gstdenis/database/recordings/'
results_folder = './results/'

# Query results for evaluated accounts to request ...
def query_account(ssh_address, scp_base_args, recording_id, max_videos_count):
    return # TODO

# Query results for evaluated solutions to request with given recording id
def query_solution(ssh_address, scp_base_args, recording_id, max_videos_count):
    solutions_folder = results_folder + 'solutions/'
    os.mkdir(solutions_folder)
    solution_videos_folder = solutions_folder + recording_id + '/'
    os.mkdir(solution_videos_folder)

    cluster_file_name = recording_id + '.txt'
    cluster_file_local_path = solutions_folder + cluster_file_name
    scp_command = scp_base_args + [
        ssh_address + ':' + validations_folder + 'clusters/' + cluster_file_name,
        cluster_file_local_path
        ]
    subprocess.Popen(scp_command).wait()

    cluster_file_local = open(cluster_file_local_path, 'r')
    cluster_file_lines = cluster_file_local.read().splitlines()
    cluster_file_local.close()
    for i, line in enumerate(cluster_file_lines):
        if i > max_videos_count:
            break  

        recording_id = line.split('|')[0]
        solution_video_name = recording_id + '_screen_recording.mp4'
        scp_command = scp_base_args + [
            ssh_address + ':' + recordings_folder + recording_id + '/' + solution_video_name,
            solution_videos_folder + solution_video_name
            ]
        subprocess.Popen(scp_command).wait()

# Program's main function
def query(ssh_address, ssh_pwd, query_type, recording_id, max_videos_count):
    if os.path.exists(results_folder):
        shutil.rmtree(results_folder)
    os.mkdir(results_folder)

    scp_base_args = [
        'sshpass', '-p', ssh_pwd,
        'scp', '-o', 'StrictHostKeyChecking=no',
        '-l', '8192' # Limiting bandwidth to 1MB/s to avoid file transfer stalling
        ]

    if query_type == 'solutions':
        query_solution(ssh_address, scp_base_args, recording_id, max_videos_count)
    elif query_type == 'accounts':
        query_account(ssh_address, scp_base_args, recording_id, max_videos_count)

    webbrowser.open('http://localhost:8080/solutions/' + recording_id)

# Program's main
if __name__ == '__main__':
    if len(sys.argv) != 6:
        print('Wrong arguments')
    else:
        ssh_address = sys.argv[1]
        ssh_pwd = sys.argv[2]
        query_type = sys.argv[3]
        recording_id = sys.argv[4]
        max_videos_count = int(sys.argv[5])

        # Query file only if user can be authenticated
        if authenticate(ssh_address, ssh_pwd):
            query(ssh_address, ssh_pwd, query_type, recording_id, max_videos_count)