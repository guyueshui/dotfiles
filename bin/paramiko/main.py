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


if __name__ == "__main__":
    deploy_package()
