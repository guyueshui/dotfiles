# encoding: utf-8

import os
import tarfile

def notify(*msg, **kwargs):
    print("--- ", *msg, **kwargs)

def tar_dir(dir_path, tar_path):
    """ Tar a directory `dir_path` to a tar file. """
    if tar_path.endswith(".gz") or tar_path.endswith(".tgz"):
        mode = "w:gz"
    elif tar_path.endswith(".bz2"):
        mode = "w:bz2"
    elif tar_path.endswith(".xz"):
        mode = "w:xz"
    else:
        mode = "w"
    with tarfile.open(tar_path, mode) as tar:
        tar.add(dir_path, arcname=os.path.basename(dir_path))

def untar_file(tar_path, target_dir):
    with tarfile.open(tar_path, "r") as tar:
        tar.extractall(target_dir)

def test_tar():
    tar_dir("./", "/home/abc/my.tar.gz")
    untar_file("/home/abc/my.tar.gz", "/home/abc/mytar_gz_extracted")