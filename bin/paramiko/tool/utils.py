# encoding: utf-8

import os
import tarfile
import zipfile
import urllib.request
import subprocess

def notify(*msg, **kwargs):
    print("---", *msg, **kwargs)

def __find_tar_member(member_shot_name: str, tar: tarfile.TarFile, reserve_path) -> tarfile.TarInfo:
    tarinfo = None
    err = "member %r not found" % member_shot_name
    try:
        tarinfo = tar.getmember(member_shot_name)
    except KeyError as e:
        err = e
        for t in tar.getmembers():
            if t.isfile() and member_shot_name == os.path.basename(t.name):
                tarinfo = t
                break
    assert tarinfo is not None, err
    if not reserve_path:
        tarinfo.name = member_shot_name
    return tarinfo

def __tar_mode_helper(tar_path: str):
    if tar_path.endswith(".gz") or tar_path.endswith(".tgz"):
        mode = "w:gz"
    elif tar_path.endswith(".bz2"):
        mode = "w:bz2"
    elif tar_path.endswith(".xz"):
        mode = "w:xz"
    else:
        mode = "w"
    return mode

def tar_dir(dir_path: str, tar_path: str, **kwargs):
    """ Tar a directory `dir_path` to a tar ball. """
    mode = __tar_mode_helper(tar_path)
    with tarfile.open(tar_path, mode) as tar:
        tar.add(dir_path, arcname=os.path.basename(dir_path), **kwargs)

def tar_files(tar_path: str, *files):
    """ Tar individual files to a tar ball. """
    mode = __tar_mode_helper(tar_path)
    with tarfile.open(tar_path, mode) as tar:
        for fn in filter(lambda x: os.path.exists(x), files):
            tar.add(fn, arcname=os.path.basename(fn))

def untar_file(tar_path, target_dir, *members, reserve_path=True):
    with tarfile.open(tar_path, "r") as tar:
        if not members:
            tar.extractall(target_dir)
        else:
            for m in members:
                info = __find_tar_member(m, tar, reserve_path)
                tar.extract(info, target_dir)

def zip_dir(dir_path: str, zip_path: str, reserve_path=True):
    """ Zip a directory `dir_path` to a zip file. """
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                fp = os.path.join(root, file)
                arcname = None if reserve_path else os.path.basename(file)
                z.write(fp, arcname=arcname)

def zip_files(zip_path: str, *files):
    """ Zip individual files to a zip file. """
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for fn in filter(lambda x: os.path.exists(x), files):
            arcname = None if os.path.isabs(fn) else os.path.basename(fn)
            z.write(fn, arcname=arcname)

def unzip_file(file_path, target_dir, *members):
    with zipfile.ZipFile(file_path) as z:
        if not members:
            z.extractall(target_dir)
        else:
            for m in members:
                z.extract(m, target_dir)

def download_file(url, filename):
    """ Download url to local file. """

    def __progress(count, block_size, total_size):
        downloaded = count * block_size
        if total_size > 0:
            percent = downloaded / total_size * 100
            print(f"\rDowloaded {percent:.2f}%", end="", flush=True)

    try:
        urllib.request.urlretrieve(url, filename, reporthook=__progress)
        print() # for newline
    except Exception as e:
        print("failed to download %s" % filename)
        print(e)
        return False
    return True

def get_last_commited_files(repo_dir: str):
    print("areyo uok")
    cmd = 'git log -1 --name-only --pretty=format:""'
    cmd_list = cmd.split()
    out = subprocess.check_output(cmd_list, cwd=repo_dir)
    for line in out.decode().splitlines():
        p = os.path.normpath(os.path.join(repo_dir, line))
        if os.path.exists(p):
            yield line

def test_tar():
    tar_dir("./", "/home/yychi/my.tar.gz")
    untar_file("/home/yychi/my.tar.gz", "/home/yychi/mytar_gz_extracted")


if __name__ == "__main__":
    test_tar()
