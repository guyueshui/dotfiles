# encoding: utf-8

"""
Here stores your remote machines's information.
"""

class RemoteNode(object):
    HOST = ""
    PORT = 22
    USERNAME = "areyou"
    PASSWORD = "ok"

class SomeRemoteMachine(RemoteNode):
    HOST = "1.2.3.4"
