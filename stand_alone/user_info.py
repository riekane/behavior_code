import os


def get_user_info():
    info_dict = {
        'initials': 'ES',
        'mouse_buttons': [['ES036', 'ES037', 'ES038'],
                          ['ES039', 'ES040', 'None']],
        'mouse_assignments': {
            'ES036': 'single_reward',
            'ES037': 'single_reward',
            'ES038': 'single_reward',
            'ES039': 'cued_forgo',
            'ES040': 'cued_forgo',
            'testmouse': 'cued_forgo',
        },
        'desktop_ip': '10.16.79.143',
        'desktop_user': 'Elissa',
        'desktop_password': 'shuler',
        'desktop_user_root': os.path.join('C:/', 'Users', 'Elissa'),
        'desktop_save_path': os.path.join('GoogleDrive', 'Code', 'Python', 'behavior_code', 'data'),
    }
    return info_dict
