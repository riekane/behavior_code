from support_classes import scp
import os


# def scp_command(host, filename, destination, user, password, timeout=30, bg_run=False, recursive=False):
#     """Scp's to a host using the supplied credentials and executes a command.
#     Throws an exception if the command doesn't return 0.
#     bgrun: run command in the background"""
#
#     options = '-q -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -oPubkeyAuthentication=no'
#     if recursive:
#         options += ' -r'
#     if bg_run:
#         options += ' -f'
#     scp_cmd = 'scp %s %s %s@%s:%s' % (options, filename, user, host, os.path.join(destination, filename))
#     return scp_cmd



if __name__ == '__main__':
    f_path = os.path.join('C:/', 'Users', 'Elissa', 'GoogleDrive', 'Code', 'Python', 'behavior_code', 'data')
    data_name = os.path.join('data')
    print(scp('192.168.137.1', data_name, f_path, 'Elissa', 'shuler', recursive=True))
