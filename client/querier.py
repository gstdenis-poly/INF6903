# Description: query on server the validation file related to given 
# query type and recording id.

# Include required librairies
from authenticator import authenticate
import os
import subprocess
import sys
import webbrowser

validations_folder = '~/projects/def-gabilode/gstdenis/database/validations/'
results_folder = './results/'

# Program's main function
def query(ssh_address, ssh_pwd, query_type, recording_id):
    if not os.path.exists(results_folder):
        os.mkdir(results_folder)
    query_results_folder = results_folder + query_type + '/'
    if not os.path.exists(query_results_folder):
        os.mkdir(query_results_folder)

    queried_file = recording_id + '.txt'
    scp_command = [
        'sshpass', '-p', ssh_pwd,
        'scp', '-o', 'StrictHostKeyChecking=no',
        ssh_address + ':' + validations_folder + query_type + '/' + queried_file,
        query_results_folder + queried_file
        ]
    subprocess.Popen(scp_command).wait()
    webbrowser.open('file://' + os.path.realpath('./displayer.html'))

# Program's main
if __name__ == '__main__':
    if len(sys.argv) != 5:
        print('Wrong arguments')
    else:
        ssh_address = sys.argv[1]
        ssh_pwd = sys.argv[2]
        query_type = sys.argv[3]
        recording_id = sys.argv[4]

        # Query file only if user can be authenticated
        if authenticate(ssh_address, ssh_pwd):
            query(ssh_address, ssh_pwd, query_type, recording_id)