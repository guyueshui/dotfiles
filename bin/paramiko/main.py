# env: python3
# encoding: utf-8

from common import *
import subprocess


def deploy_package():
    # init ssh connection
    conn = SSHConnection()
    conn.re_init(N.RemoteNode)

    # code_root = os.path.expanduser("~/code/project")
    # print(code_root)

    args = ["/opt/project/bin", "demo.tar.gz"]
    subprocess.check_call(["make", "-C", *args])
    local_file = '/'.join(args)

    conn.upload(local_file, './')
    conn.excute(f"""
    mkdir ttt
    tar -xavf {args[1]} -C ttt
""")
    conn.close()


def run_on_dellinspiron():
    conn = SSHConnection(*N.DellInspiron.get_para())
    chain = conn.get_cmd_chain().execute("sudo -i").write_input(conn.password)
    chain.execute("ls -al")\
        .execute("whoami && id")\
        .execute("cat /etc/hostname")
    chain.execute("exit 23").execute("exit 34").over()


if __name__ == "__main__":
    run_on_dellinspiron()
