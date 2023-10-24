import os


def get_user_info():
    info_dict = {
        'initials': 'SZ',
        'mouse_buttons': [['SZ036', 'SZ037', 'SZ038'],
                          ['SZ039', 'SZ040', 'SZ041'],
                          ['SZ042', 'SZ043', 'SZ044']],
        'mouse_assignments': {
            'SZ036': 'cued_forgo',
            'SZ037': 'cued_forgo',
            'SZ038': 'cued_forgo',
            'SZ039': 'cued_forgo',
            'SZ040': 'cued_forgo',
            'SZ041': 'cued_forgo',
            'SZ042': 'cued_forgo',
            'SZ043': 'cued_forgo',
            'SZ044': 'cued_forgo',
            'testmouse': 'cued_forgo',
        },
        'desktop_ip': '10.16.80.130',
        'desktop_user': 'Shichen',
        'desktop_password': 'shuler_914WBSB',
        'desktop_user_root': os.path.join('C:/', 'Users', 'Shichen'),
        'desktop_save_path': os.path.join('OneDrive - Johns Hopkins', 'ShulerLab', 'behavior_code', 'data'),
    }
    return info_dict
