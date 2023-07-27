from support_classes import scp
import os
from user_info import get_user_info

info_dict = get_user_info()

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
    # f_path = os.path.join('C:/', 'Users', 'Elissa', 'GoogleDrive', 'Code', 'Python', 'behavior_code', 'data')
    f_path = os.path.join(info_dict['desktop_user_root'], info_dict['desktop_save_path'])
    data_name = os.path.join('data')
    print(scp(info_dict['desktop_ip'], data_name, f_path, info_dict['desktop_user'], info_dict['desktop_password'],
              recursive=True))
