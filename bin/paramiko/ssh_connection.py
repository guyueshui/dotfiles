# encoding: utf-8

from utility import notify
import os
import paramiko
import paramiko.util
paramiko.util.log_to_file("paramiko.log")


class CommandRunException(Exception):
    pass


class SSHConnection(object):
    """ Provide a ssh connection to excute commands, download/upload files with remote host. """
    def __init__(self, host="", password="", username="bingbing.hu", port=22) -> None:
        self.host = host
        self.password = password
        self.username = username
        self.port = port
        self._client = None      # type: paramiko.SSHClient | None
        self._sftp_client = None # type: paramiko.SFTPClient | None

    def close(self):
        if self._client is not None:
            self._client.close()
        if self._sftp_client is not None:
            self._sftp_client.close()
        self._client = None
        self._sftp_client = None

    def re_init(self, node_cls):
        """ Re-init the node with a NodeConf class. """
        self.host = node_cls.HOST
        self.password = node_cls.PASSWORD
        self.username = node_cls.USERNAME
        self.port = node_cls.PORT
        if self._client is not None:
            self._client.close()
            self._client = None
        self.get_client()

    def get_client(self):
        if self._client is None:
            self._client = ssh = paramiko.SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.host, self.port, self.username, self.password)
        return self._client

    def get_sftp_client(self):
        if self._sftp_client is None:
            self._sftp_client = self.get_client().open_sftp()
        return self._sftp_client

    def excute(self, cmd):
        stdin, stdout, stderr = self.get_client().exec_command(cmd)
        return self.__handle_cmd_output(stdout, stderr, cmd)

    def excute_with_sudo(self, cmd):
        stdin, stdout, stderr = self.get_client().exec_command("sudo -S %s" % cmd)
        stdin.write(self.password + "\n")
        stdin.flush()
        return self.__handle_cmd_output(stdout, stderr, cmd)

    @staticmethod
    def __handle_cmd_output(stdout: paramiko.ChannelFile, stderr: paramiko.ChannelFile, cmd: str) -> int:
        status = stdout.channel.recv_exit_status()
        if status != 0:
            raise CommandRunException(
                "Excute '%s' failed with status %d.\n\n%s"
                % (cmd, status, stderr.read().decode()))
        for line in stdout:
            print(line, end="")
        return status

    def upload(self, local_path, remote_path):
        if not os.path.exists(local_path):
            raise FileNotFoundError("Local file %s not found." % local_path)
        if remote_path[-1] == '/': # treat remote_path as a directory
            self.__ensure_remote_path(remote_path)
            filename = os.path.basename(local_path)
            remote_path += filename
        notify("Uploading %s to %s" % (local_path, remote_path))

        # \r is used to move cursor to the beginning of the line.
        cb = lambda x, y: notify(f"Uploaded {x}/{y}\r", end="", flush=True)
        self.get_sftp_client().put(local_path, remote_path, callback=cb)
        print('') # used to remove the last \r

    def download(self, remote_path, local_path):
        if remote_path[-1] == '/':
            raise ValueError("Remote path should be a file path.")
        local_file = local_path
        if local_path[-1] == '/':
            local_dir = local_path[:-1]
            local_file = os.path.join(local_path, os.path.basename(remote_path))
        else:
            local_dir = os.path.split(local_path)[0]
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)

        sftp = self.get_sftp_client()
        notify("Downloading %s to %s" % (remote_path, local_file))

        # \r is used to move cursor to the beginning of the line.
        cb = lambda x, y: notify(f"Downloaded {x}/{y}\r", end="", flush=True)
        sftp.get(remote_path, local_file, callback=cb)
        print('') # used to remove the last \r

    def __ensure_remote_path(self, remote_path):
        self.excute(f"""
            if [ ! -d {remote_path} ]; then
                mkdir -p {remote_path}
            fi
            """)


def test_connection():
    from remote_node import RemoteNode
    conn = SSHConnection()
    conn.re_init(RemoteNode)

    a = conn.excute("pwd;df -h")
    # conn.excute_with_sudo("apt list --upgradable | head -n5")
    conn.excute("""
cd /tmp
mkdir -p test
cd test
pwd
touch {a,b,c}
ls -l""")

    conn.excute("./a.out") # raise exception
    conn.upload("main.py", "./hahs/")
    conn.download("./hahs/main.py", "./from_remote.py")
    conn.close()

if __name__ == "__main__":
    test_connection()
