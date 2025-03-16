# encoding: utf-8

"""
Here stores your remote machines's information.
"""

class RemoteNode(object):
    HOST = ""
    PORT = 22
    USERNAME = "areyou"
    PASSWORD = "ok"

    @classmethod
    def get_para(cls):
        return (cls.HOST, cls.PASSWORD, cls.USERNAME, cls.PORT)

    @classmethod
    def get_para_dict(cls):
        return {"host": cls.HOST, "password": cls.PASSWORD,
                "username": cls.USERNAME, "port": cls.PORT }


class SomeRemoteMachine(RemoteNode):
    HOST = "1.2.3.4"
    SOME_HOST_SPECIFIC_VAR = "bahlabahla"
