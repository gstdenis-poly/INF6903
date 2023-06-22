# Description: register new account to database

# Include required librairies
import os
import subprocess
import sys

accounts_folder = '~/projects/def-gabilode/gstdenis/database/accounts/'

# Read account credentials in given account file
def read_credentials(account_file_path):
    acc_name, acc_pwd = None, None
    try:
        account_file = open(account_file_path, 'r')
        account_file_lines = account_file.read().splitlines()
        account_file.close()
        for line in account_file_lines:
            line_infos = line.split('|')
            if line_infos[0] == 'acc_name':
                acc_name = line_infos[1]
            elif line_infos[0] == 'acc_pwd':
                acc_pwd = line_infos[1]
    except Exception as e:
        print(e)

    return acc_name, acc_pwd

# Program main function
def authenticate(ssh_address, ssh_pwd):
    acc_name, acc_pwd = read_credentials('./account.txt')
    if acc_name == None or acc_pwd == None:
        print('User not registered')
        return False

    scp_base_args = [
        'sshpass', '-p', ssh_pwd,
        'scp', '-o', 'StrictHostKeyChecking=no'        
        ]
    db_account_file_name = acc_name + '.txt'
    db_account_file_path = ssh_address + ':' + accounts_folder + db_account_file_name

    scp_command = scp_base_args + [db_account_file_path, db_account_file_name]
    subprocess.Popen(scp_command).wait()
    if not os.path.isfile(db_account_file_name):
        print('Unexisting account')
        return False
    else:
        db_acc_name, db_acc_pwd = read_credentials(db_account_file_name)
        os.remove(db_account_file_name)

        if acc_name == db_acc_name and acc_pwd == db_acc_pwd:
            print('Authentication completed')
            return acc_name
        else:
            print('Wrong password')
            return False

# Program's main
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Wrong arguments')
    else:
        ssh_address = sys.argv[1]
        ssh_pwd = sys.argv[2]

        authenticate(ssh_address, ssh_pwd)