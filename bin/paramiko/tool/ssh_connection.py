# encoding: utf-8

from tool.utils import notify
from threading import Thread
import os
import re
import sys
import time
import select
import asyncio
import paramiko
import paramiko.util
paramiko.util.log_to_file("paramiko.log")


class CommandRunException(Exception):
    pass


class SSHConnection(object):
    def __init__(self, host="", password="", username="yychi", port=22) -> None:
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
        print("%s.close" % self.__class__.__name__)

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

    async def aexecute(self, cmd, output=False, ignore_fail=False):
        loop = asyncio.get_event_loop()
        stdin, stdout, stderr = await loop.run_in_executor(
            None, self.get_client().exec_command, cmd
        )
        exit_code, out, err = await asyncio.gather(
            loop.run_in_executor(None, stdout.channel.recv_exit_status),
            loop.run_in_executor(None, stdout.read().decode),
            loop.run_in_executor(None, stderr.read().decode),
        )
        return exit_code, out, err

    def excute_silent(self, cmd):
        stdin, stdout, stderr = self.get_client().exec_command(cmd)
        status = stdout.channel.recv_exit_status()
        if status != 0:
            raise CommandRunException(
                "Excute '%s' failed with status %d.\n\n%s"
                % (cmd, status, stderr.read().decode()))
        return status

    def excute_with_sudo(self, cmd):
        stdin, stdout, stderr = self.get_client().exec_command("sudo -S %s" % cmd)
        stdin.write(self.password + "\n")
        stdin.flush()
        return self.__handle_cmd_output(stdout, stderr, cmd)

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

    def get_achain(self):
        return AsyncCommandChain(self.get_client())

    def upload(self, local_path, remote_path):
        if not os.path.exists(local_path):
            raise FileNotFoundError("Local file %s not found." % local_path)
        if remote_path[-1] == '/': # treat remote_path as a directory
            self._ensure_remote_path(remote_path)
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

    def _ensure_remote_path(self, remote_path):
        self.excute(f"""
            if [ ! -d {remote_path} ]; then
                mkdir -p {remote_path}
            fi
            """)


class CommandChain(object):
    PROMPT = re.compile(r'[$#]\s*$')

    def __init__(self, ssh_client: paramiko.SSHClient, timeout=0):
        assert ssh_client is not None
        self._client = ssh_client
        self._chan = ssh_client.invoke_shell() # type: paramiko.Channel
        time.sleep(1) # wait the channel to be ready
        # self._chan.setblocking(0)
        # self._chan.set_combine_stderr(True)
        self._stdin = self._chan.makefile_stdin("wb", -1)
        self._exit_status = 0
        self._timeout = timeout
        self._closed = False
        self._output_trd = Thread(target=self.__retrieve_output)
        self._input_trd = Thread(target=self.__input_loop)
        self._output_trd.start()
        self._input_trd.start()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        exc_type and print("type: %s" % exc_type)
        exc_val and print("val: %s" % exc_val)
        exc_tb and print("tb: %s" % exc_tb)
        self.execute(f"exit {self._exit_status}").over()

    def over(self):
        time.sleep(0.5) # essential, otherwise the command will be blocked
        # while not self._chan.exit_status_ready():
        #     self.execute("exit")
        # self.__handle_output()
        self._output_trd.join()
        self._stdin.close()
        self._chan.close()
        self._client = None
        self._closed = True
        self._input_trd.join()
        print("%s.over" % self.__class__.__name__)

    def execute(self, one_line_cmd: str):
        one_line_cmd = one_line_cmd.rstrip('\n') + '\n'
        self._chan.send(one_line_cmd.encode())
        time.sleep(0.5) # essential for the command to execute
        return self

    def write_input(self, text: str):
        text = text.rstrip('\n') + '\n'
        self._stdin.write(text.encode())
        self._stdin.flush()
        time.sleep(0.5)
        return self

    def __retrieve_output(self):
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
        st = self._exit_status = self._chan.recv_exit_status()
        print("exit with", st)

    def __input_loop(self):
        notify("enter %s REPL..." % self.__class__.__name__)
        while not self._closed:
            try:
                rlist,_,_ = select.select([sys.stdin], [], [], 0.1)
                if rlist:
                    user_input = sys.stdin.readline()
                    if not user_input:
                        notify("EOF receieved")
                        self.execute("exit")
                    else:
                        self.execute(user_input)
            except KeyboardInterrupt:
                notify("exit %s REPL..." % self.__class__.__name__)
                return
            except Exception as e:
                notify("unknow exception occured", str(e))
                import traceback
                traceback.print_exc()
                return

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


class AsyncCommandChain(object):
    def __init__(self, ssh_client: paramiko.SSHClient, timeout=0):
        assert ssh_client is not None
        self._client = ssh_client
        self._chan = ssh_client.invoke_shell() # type: paramiko.Channel
        time.sleep(1) # wait the channel to be ready
        # self._stdin = self._chan.makefile_stdin("wb", -1)
        self._exit_status = 0
        self._tasks = []
        self._consumer_cancel_evt = asyncio.Event()

        self.loop = asyncio.get_event_loop()
        self.cmdq = asyncio.Queue(1024)

    async def append_cmd(self, cmd: str):
        if self._consumer_cancel_evt.is_set():
            return
        cmd = cmd.rstrip('\n') + '\n'
        # await self.cmdq.put(cmd)
        self._chan.send(cmd.encode())
        await asyncio.sleep(0.5)

    async def _consume_cmd(self, event: asyncio.Event):
        while not event.is_set():
            cmd = await self.cmdq.get()
            notify("send cmd", cmd)
            self._chan.send(cmd)
            await asyncio.sleep(0.5)
        notify(f"{self.__class__.__name__}.{self._consume_cmd.__name__} exit")

    async def retrieve_output(self):
        output = b""
        while True:
            bmsg = await self.loop.run_in_executor(None, self._chan.recv, 4096)
            notify("get output")
            output += bmsg
            output += await self.loop.run_in_executor(None, self._chan.recv_stderr, 4096)
            notify("get err")
            if output.count(b'\n') > 0:
                print(output.decode(), end="")
                output = b""
        # st = self._exit_status = self._chan.recv_exit_status()

    async def retrieve_outputv2(self):
        output = b""
        while not self._chan.exit_status_ready():
            if self._chan.recv_ready():
                bmsg = self._chan.recv(4096)
                # notify("get output")
                output += bmsg
            if self._chan.recv_stderr_ready():
                output += self._chan.recv_stderr(4096)
                notify("get err")
            if output.count(b'\n') > 0:
                print(output.decode(), end="")
                output = b""
            await asyncio.sleep(0.1)
        st = self._exit_status = self._chan.recv_exit_status()
        notify("exit with", st)
        self._consumer_cancel_evt.set()
        notify(f"{self.__class__.__name__}.{self.retrieve_outputv2.__name__} exit")

    async def start(self, *tasks):
        self._tasks = [
            # asyncio.create_task(self._consume_cmd(self._consumer_cancel_evt)),
            asyncio.create_task(self.retrieve_outputv2()),
            # asyncio.create_task(self.exit())
        ]
        self._tasks.extend(tasks)
        await asyncio.gather(*self._tasks) # is equivalent to
        # await asyncio.create_task(self.retrieve_outputv2())
        # for t in tasks:
        #     await t

    async def exit(self):
        count = 0
        while not self._consumer_cancel_evt.is_set():
            await self.append_cmd("exit")
            count += 1
            notify("sent exit cmd, count=%s, pending cmds=%s" % (count, self.cmdq.qsize()))
            await asyncio.sleep(count)
        return self._exit_status

    async def foo(self, cmd: str):
        loop = asyncio.get_event_loop()
        stdin, stdout, stderr = await loop.run_in_executor(
            None, self._client.exec_command, cmd
        )
        exit_code, output, err = await asyncio.gather(
            loop.run_in_executor(None, stdout.channel.recv_exit_status),
            loop.run_in_executor(None, stdout.read),
            loop.run_in_executor(None, stderr.read),
        )
        return exit_code, output.decode(), err.decode()


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
