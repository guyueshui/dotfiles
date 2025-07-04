# encoding: utf-8
# This file serves as a handy import file for all the scripts.

from tool.ssh_connection import SSHConnection
from tool import remote_node as N
from tool import utils
from tool import *
import os


# projects directory
MDL_SRC = os.path.expanduser("~/code/mdl_src")
DBALCHEMY = os.path.expanduser("~/code/dbalchemy")
NEWAPI = os.path.expanduser("~/code/newapi")


def transfer_feeder_to(node_cls: Type[N.RemoteNode], tarname: str):
    utils.notify(f"transfer feeder to {node_cls.get_desc()}")
    status = 0
    with SSHConnection(*N.SomeRemoteMachine.get_para()) as r:
        # scp 不支持密码输入，必须用 sshpass
        status = r.excute(f"""
cd code/mdl_src/build/make/bin
tar -caf {tarname} feeder_handler libmdl_api.so
sshpass -p {node_cls.PASSWORD} scp {tarname} {node_cls.USERNAME}@{node_cls.HOST}:
rm -f {tarname}
""")
    return status