from common import *
import os
import tarfile


class CompileTask1604(object):
    """ Compile on ubuntu 16.04. """
    def __init__(self) -> None:
        self.conn = SSHConnection()
        self.conn.re_init(N.SomeRemoteMachine)

    def destroy(self):
        if self.conn is not None:
            self.conn.close()
        self.conn = None

    @staticmethod
    def filter_src_files(tarinfo: tarfile.TarInfo):
        name = tarinfo.name
        if '.git' in name or ".vscode" in name or ".cache" in name:
            return None
        if name.startswith('.'):
            return None
        if tarinfo.isdir():
            if "3rd" in name or "build" in name or "doc" in name or "obj" in name or "bin" in name:
                return None
            return tarinfo
        if tarinfo.isfile() and (
            name.endswith(".h") or name.endswith(".cpp")
        ):
            return tarinfo
        return None

    def compile_mdl_src(self):
        conn = self.conn

        tar_name = "mdl_src.tar.bz2"
        utility.tar_dir(MDL_SRC, tar_name, filter=self.__class__.filter_src_files)
        conn.upload(tar_name, "./code/")
        conn.excute(f"""
cd code
tar -xavf {tar_name}
rm -f {tar_name}
echo; echo
cd mdl_src/build/make
make -j4
""")
        os.remove(tar_name)

    def compile_dbalchemy(self):
        conn = self.conn

        def _filter(tarinfo: tarfile.TarInfo):
            name = tarinfo.name
            if 'build.sh' in name or "makefile" in name:
                return tarinfo
            return self.__class__.filter_src_files(tarinfo)

        tar_name = "dbalchemy.tar.bz2"
        utility.tar_dir(DBALCHEMY, tar_name, filter=_filter)
        conn.upload(tar_name, "./code/")
        conn.excute(f"""
set -e
cd code
tar -xavf {tar_name}
rm -f {tar_name}
echo; echo
cd dbalchemy/
bash -e build.sh
""")
        os.remove(tar_name)


if __name__ == '__main__':
    task = CompileTask1604()
    task.compile_mdl_src()
    task.destroy()