# encoding: utf-8

import os
import tarfile

def notify(*msg, **kwargs):
    print("---", *msg, **kwargs)

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
    """ Tar a directory `dir_path` to a tar file. """
    mode = __tar_mode_helper(tar_path)
    with tarfile.open(tar_path, mode) as tar:
        tar.add(dir_path, arcname=os.path.basename(dir_path), **kwargs)

def tar_files(tar_path: str, *files):
    mode = __tar_mode_helper(tar_path)
    with tarfile.open(tar_path, mode) as tar:
        for fn in filter(lambda x: os.path.exists(x), files):
            tar.add(fn, arcname=os.path.basename(fn))

def untar_file(tar_path, target_dir):
    with tarfile.open(tar_path, "r") as tar:
        tar.extractall(target_dir)

def test_tar():
    tar_dir("./", "/home/yychi/my.tar.gz")
    untar_file("/home/yychi/my.tar.gz", "/home/yychi/mytar_gz_extracted")


if __name__ == "__main__":
    test_tar()