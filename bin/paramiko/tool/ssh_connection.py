# encoding: utf-8
author = "bingbing.hu"

from tool.utils import notify
from threading import Thread
import os
import time
import paramiko
import paramiko.util
paramiko.util.log_to_file("paramiko.log")


class CommandRunException(Exception):
    pass


class SSHConnection(object):
    def __init__(self, host="", password="", username="bingbing.hu", port=22) -> None:
        self.host = host
        self.password = password
        self.username = username
        self.port = port
        self._client = None      # type: paramiko.SSHClient | None
        self._sftp_client = None # type: paramiko.SFTPClient | None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        exc_type and print("type: %s" % exc_type)
        exc_val and print("val: %s" % exc_val)
        exc_tb and print("tb: %s" % exc_tb)
        self.close()

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

    def __excute_successive_cmds(self, cmd):
        client = self.get_client()
        chan = client.invoke_shell()
        chan.set_combine_stderr(True)
        stdin = chan.makefile_stdin("wb", -1)
        stdout = chan.makefile("r", -1)
        # chan.send("sudo -i\n")
        # chan.sendall(self.password + "\n")
        # time.sleep(.5)
        # stdin.flush()
        stdin.write("ls -al\n")
        stdin.write(f"""
sudo -i
{self.password}
""")
        time.sleep(0.5)
#         chan.send("""
# pwd
# echo $HOME
# echo $USER
# """.encode())
        # chan.sendall("pwdx 15391\n".encode())
        chan.send("exit\n".encode())
        chan.send("./a.out\n".encode())
        chan.send("exit\n".encode())
        while True:
            if chan.recv_ready():
                print(chan.recv(1024).decode())
                continue
            if chan.exit_status_ready():
                exit_status = chan.recv_exit_status()
                break
            if chan.closed or chan.eof_received or not chan.active:
                break
            time.sleep(0.5)
        print("exit_status:", exit_status)

    @staticmethod
    def __handle_cmd_output(stdout: paramiko.ChannelFile, stderr: paramiko.ChannelFile, cmd: str) -> int:
        for line in stdout:
            print(line, end="")
        status = stdout.channel.recv_exit_status()
        if status != 0:
            raise CommandRunException(
                "Excute '%s' failed with status %d.\n\n%s"
                % (cmd, status, stderr.read().decode()))
        return status

    def get_cmd_chain(self, timeout=0):
        return CommandChain(self.get_client(), timeout)

    def get_cmd_context(self):
        return CommandContext(self.get_client())

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
        cb = lambda x, y: print(f"\rDownloaded {x}/{y}", end="", flush=True)
        sftp.get(remote_path, local_file, callback=cb)

    def __ensure_remote_path(self, remote_path):
        self.excute(f"""
            if [ ! -d {remote_path} ]; then
                mkdir -p {remote_path}
            fi
            """)


class CommandChain(object):
    def __init__(self, ssh_client: paramiko.SSHClient, timeout=0):
        assert ssh_client is not None
        self._client = ssh_client
        self._chan = ssh_client.invoke_shell(self.__class__.__name__) # type: paramiko.Channel
        time.sleep(1) # wait the channel to be ready
        # self._chan.setblocking(0)
        # self._chan.set_combine_stderr(True)
        self._stdin = self._chan.makefile_stdin("wb", -1)
        self._exit_status = 0
        self._timeout = timeout

        self._trd = Thread(target=self._retrieve_output)
        self._trd.start()

    def _retrieve_output(self):
        output = b""
        while not self._chan.exit_status_ready():
            if self._chan.recv_ready():
                bmsg = self._chan.recv(4096)
                output += bmsg
            if self._chan.recv_stderr_ready():
                output += self._chan.recv_stderr(4096)
            if output.count(b'\n') > 0:
                print(output.decode(), end="")
                output = b""
        st = self._chan.recv_exit_status()
        notify("exit with", st)
        return st

    def over(self):
        time.sleep(0.5) # essential, otherwise the command will be blocked
        # while not self._chan.exit_status_ready():
        #     self.execute("exit")
        # self.__handle_output()
        self._stdin.close()
        self._chan.close()
        self._client = None
        self._trd.join()

    def execute(self, one_line_cmd: str):
        one_line_cmd = one_line_cmd.rstrip('\n') + '\n'
        self._chan.send(one_line_cmd.encode())
        time.sleep(0.5) # essential for the command to execute
        return self

    def write_input(self, text: str):
        text = text.rstrip('\n') + '\n'
        self._stdin.write(text.encode())
        self._stdin.flush()
        time.sleep(0.5) # essential for the command to execute
        return self

    def __handle_output(self):
        chan = self._chan
        # If you don't set timeout, the stdout.read will block,
        # or you can send multiple "exit" to remote node,
        # this will make chan.exit_status_ready returns true.
        if self._timeout > 0:
            chan.settimeout(self._timeout)
        stdout = chan.makefile("r", -1)
        try:
            for line in stdout:
                print(line, end="")
        except Exception as e:
            notify("no data in %ss, channel will be closed!" % self._timeout)


import selectors as sl

class CommandContext(object):
    SELECTOR = sl.DefaultSelector()
    def __init__(self, ssh_client: paramiko.SSHClient):
        self._cmdq = []
        self._output = b""
        self._ssh = ssh_client
        self._chan = ssh_client.invoke_shell(self.__class__.__name__) # type: paramiko.Channel
        # self._chan.setblocking(0)
        # self._chan.set_combine_stderr(True)
        self._stdin = self._chan.makefile_stdin("wb", -1)
        self._stdout = self._chan.makefile("rb", -1)
        self._stderr = self._chan.makefile_stderr('rb', -1)

        self.__class__.SELECTOR.register(self._chan, sl.EVENT_READ | sl.EVENT_WRITE)

    def execute(self, cmd):
        self._cmdq.append(cmd)
        return self

    def process_events(self, mask):
        if mask & sl.EVENT_READ:
            try:
                if self._chan.recv_stderr_ready():
                    data = self._stderr.read(1024)
                else:
                    data = self._stdout.read(1024)
                if data:
                    print(data.decode(), end="")
                    self._output += data
                else:
                    notify("close channel")
                    self.SELECTOR.unregister(self._chan)
                    self._chan.close()
                    return 0
            except Exception as e:
                notify("%s read error: %s" % (self.__class__.__name__, str(e)))

        if mask & sl.EVENT_WRITE and self._cmdq:
            try:
                cmd = self._cmdq.pop(0)
                cmd = cmd.rstrip('\n') + '\n'
                self._chan.send(cmd)
            except Exception as e:
                notify("%s write error: %s" % (self.__class__.__name__, str(e)))

        return 1

    def over(self):
        while True:
            events = self.SELECTOR.select(1)
            for key, mask in events:
                notify(key, mask)
                flag = self.process_events(mask)
                if flag == 0:
                    break
        return flag


def test_connection():
    from tool.node import NewApiDevNode
    conn = SSHConnection()
    conn.re_init(NewApiDevNode)

    conn.excute("pwd;df -h")
    conn.excute_with_sudo("apt list --upgradable | head -n5")
    conn.excute("""
cd /tmp
mkdir -p test
cd test
pwd
touch {a,b,c}
ls -l""")

    conn.upload("main.py", "./areyouok/")
    # conn.excute("./a.out")
    # node.get_sftp_client().put("main.py", "main.py")
    conn.download("./api_etc.tar", "./from_remote.tar")
    conn.close()


def test_cmd_chain():
    from node import NewApiDevNode
    conn = SSHConnection()
    conn.re_init(NewApiDevNode)

    conn.get_cmd_chain().execute("echo $USER")\
        .execute("sudo -i").write_input(conn.password)\
        .execute("echo $USER").execute("apt list --upgradable|head -5")\
        .over()


if __name__ == "__main__":
    # test_connection()
    test_cmd_chain()