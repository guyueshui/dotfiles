import platform
from smb.SMBConnection import SMBConnection
from getpass import getpass

class SMBProxy(object):
    def __init__(self, server, username, password):
        self.conn = SMBConnection(
            username, password,
            platform.uname().node,
            server,
            is_direct_tcp=True
        )
        assert self.conn.connect(server, 445), "connect %s failed" % server

    def download(self, remote_path: str, local_file):
        rp = remote_path.replace('\\', '/').split('/', maxsplit=1)
        with open(local_file, 'wb') as lf:
            self.conn.retrieveFile(rp[0], rp[1], lf, show_progress=True)

    def upload(self, local_file, remote_path):
        with open(local_file, 'rb') as f:
            rp = remote_path.replace('\\', '/').split('/', maxsplit=1)
            self.conn.storeFile(rp[0], rp[1], f, show_progress=True)


SHFILE = None
def get_shfile_proxy():
    global SHFILE
    if SHFILE is None:
        secret = getpass("Enter your SMB password: ")
        SHFILE = SMBProxy("shfile", "user1", secret)
    return SHFILE
