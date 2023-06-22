# Description: register new account to database

# Include required librairies
import os
import subprocess
import sys

accounts_folder = '~/projects/def-gabilode/gstdenis/database/accounts/'

# Program main function
def register(ssh_address, ssh_pwd, acc_name, acc_pwd, acc_type):
    if acc_type not in ['requester', 'provider']:
        print('User type must be "requester" or "provider"')
        return

    local_account_file_path = './account.txt'
    account_file = open(local_account_file_path, 'w')
    account_file.write('acc_name|' + acc_name + '\n')
    account_file.write('acc_pwd|' + acc_pwd + '\n')
    account_file.write('acc_type|' + acc_type + '\n')
    account_file.close()

    scp_base_args = [
        'sshpass', '-p', ssh_pwd,
        'scp', '-o', 'StrictHostKeyChecking=no'        
        ]
    db_account_file_name = acc_name + '.txt'
    db_account_file_path = ssh_address + ':' + accounts_folder + db_account_file_name

    scp_command = scp_base_args + [db_account_file_path, db_account_file_name]
    subprocess.Popen(scp_command).wait()
    if not os.path.isfile(db_account_file_name):
        scp_command = scp_base_args + [local_account_file_path, db_account_file_path]
        subprocess.Popen(scp_command).wait()
        print('Registration completed')
    else:
        os.remove(db_account_file_name)
        print('Account already registered')

# Program's main
if __name__ == '__main__':
    if len(sys.argv) != 6:
        print('Wrong arguments')
    else:
        ssh_address = sys.argv[1]
        ssh_pwd = sys.argv[2]
        acc_name = sys.argv[3]
        acc_pwd = sys.argv[4]
        acc_type = sys.argv[5]

        register(ssh_address, ssh_pwd, acc_name, acc_pwd, acc_type)