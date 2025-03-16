This is a simple wrapper for python paramiko library.

You can use it to execute commands in remote host via ssh tunnel, or
upload/download files to/from your remote host.

For example usage, see `main.py <main.py>`_. It is recommended to put
multiple scripts in project root, keep the wrapper class and some other
stuff in the ``tool`` package.