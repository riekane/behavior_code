import os
import paramiko

def upload_to_pi(pi_host_name):
    local_path = os.path.join(os.getcwd(), "stand_alone")
    pi_user_name = 'pi'
    remote_path = '\home\pi'
    password = 'shuler'
    # command = f'scp -r {os.path.join(local_path, "stand_alone")} {pi_user_name}@{pi_host_name}:{remote_path}'
    ssh = paramiko.SSHClient()
    ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
    ssh.connect(pi_host_name, username=pi_user_name, password=password)
    sftp = ssh.open_sftp()

    [_, _, files] = list(os.walk(local_path))[0]
    for f in files:
        if f != 'durations.pkl':
            sftp.put(os.path.join(local_path, f), os.path.join(remote_path, f))
    sftp.close()
    ssh.close()


if __name__ == '__main__':
    pi_names = ['elissapi0', 'elissapi2']
    for name in pi_names:
        upload_to_pi(name)
