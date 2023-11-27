import os


def get_user_info():
    info_dict = {
        'initials': 'ES',
        'mouse_buttons': [['ES041', 'ES042', 'ES037'],
                          ['ES043', 'ES044', 'ES039'],
                          ['ES045', 'ES046', 'ES047']],
        'button_colors': [[3, 3, 1],
                          [3, 3, 2],
                          [4, 4, 4]],
        'mouse_assignments': {
            'ES036': 'single_reward',
            'ES037': 'single_reward',
            'ES039': 'cued_forgo',
            'ES040': 'cued_forgo',
            'ES041': 'single_reward',
            'ES042': 'single_reward',
            'ES043': 'single_reward',
            'ES044': 'single_reward',
            'ES045': 'cued_forgo',
            'ES046': 'cued_forgo',
            'ES047': 'cued_forgo',
            'testmouse': 'cued_forgo',
        },
        'mouse_colors': {
            'ES036': 1,
            'ES037': 1,
            'ES039': 2,
            'ES040': 2,
            'ES041': 3,
            'ES042': 3,
            'ES043': 3,
            'ES044': 3,
            'ES045': 4,
            'ES046': 4,
            'ES047': 4,
            'testmouse': 1,
        },
        'desktop_ip': '10.16.79.143',
        'desktop_user': 'Elissa',
        'desktop_password': 'shuler',
        'desktop_user_root': os.path.join('C:/', 'Users', 'Elissa'),
        'desktop_save_path': os.path.join('GoogleDrive', 'Code', 'Python', 'behavior_code', 'data'),
    }
    return info_dict
