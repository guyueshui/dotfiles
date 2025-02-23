#!/usr/bin/env python

import os, sys, re, subprocess
import shutil
import time

author = "yychi (guyueshui002@gmail.com)"
USAGE = f"""
This script helps you copy a markdown file in obsidian as a hugo post. It
automatically copy the local attachments referenced by that md file to
proper directory in your hugo site.

Usage:

  {sys.argv[0]} md_file hugo_post_dir

"""
# cf. https://stackoverflow.com/a/44227600
ATTACHMENT_PATTERN = re.compile(
    r"!\[[^\]]*\]\((?P<filename>.*?)(?=\"|\))(?P<optionalpart>\".*\")?\)"
)
# hugo post frontmatter
FRONTMATTER = """---
title: "%s"
date: %s
tags: []

---

"""


def notify(*args):
    print("--", *args)


def guess_attachment_path(host_file: str, attachment_file: str) -> str:
    """
    Guess the attachment file path of markdown link.
    - `host_file`: the file where the markdown link comes from.
    - `attachment_file`: the markdown link.
    """
    host_file = os.path.normpath(os.path.abspath(host_file))
    parent_dir = os.path.dirname(host_file)
    filename = os.path.basename(attachment_file)
    retry = 0
    while retry < 2:
        cmd_ret = subprocess.run(
            ["find", parent_dir, "-name", filename, "-printf", "%p"],
            capture_output=True, text=True
        )
        if cmd_ret.returncode == 0 and cmd_ret.stdout:
            return os.path.normpath(os.path.abspath(cmd_ret.stdout))
        parent_dir = os.path.dirname(parent_dir)
        retry += 1
    return ""


class AttachmentHandler(object):
    def __init__(self, src_file: str, dst_path: str):
        self.host_file = src_file
        self.dst_path = dst_path

    def replace_link(self, match: re.Match) -> str:
        """ Replace each attachment. """
        matched_str = match.group() # type: str
        attachment_file = match.group('filename')
        attachment_path = guess_attachment_path(self.host_file, attachment_file)
        if not attachment_path:
            notify(f"{attachment_file} not found, skip it.")
            return matched_str
        self.put_attachment(attachment_path)
        return matched_str.replace(attachment_file, os.path.basename(attachment_file))

    def put_attachment(self, attachment_path):
        filename = os.path.basename(self.host_file)
        filename = os.path.splitext(filename)[0]
        asset_path = os.path.join(self.dst_path, filename)
        if not os.path.exists(asset_path):
            os.makedirs(asset_path)
        notify(f"{self.__class__.__name__}: copy {attachment_path} to {asset_path}")
        shutil.copy(attachment_path, asset_path)


def copy_as_hugo_post(src_file: str, dst_path: str):
    """
    Copy a md file to hugo post, handle the attachments if has.
    """
    src_file, dst_path = map(
        lambda x: os.path.normpath(os.path.abspath(x)),
        (src_file, dst_path)
    )
    if not os.path.isfile(src_file):
        notify(f"{src_file} is not a regular file.")
        exit(1)
    if not os.path.exists(dst_path):
        os.makedirs(dst_path)
    notify(f"copy {src_file} to {dst_path}")
    content = None
    with open(src_file, 'r') as fr:
        a = AttachmentHandler(src_file, dst_path)
        content, n = ATTACHMENT_PATTERN.subn(a.replace_link, fr.read())
    basename = os.path.basename(src_file)
    dst_file = os.path.join(dst_path, basename)
    with open(dst_file, 'w') as fw:
        # add frontmatter as needed
        if not content.startswith('---'):
            fw.write(FRONTMATTER % (
                os.path.splitext(basename)[0],
                time.strftime("%FT%T%z", time.localtime())))
        fw.write(content)
    return 0

def test():
    s = """
    hello how [abc](https://baidu.com),
    let's see a image that do
    and ![image](/path/to/img.jpg)
    010-1234, now a days that
    fuskkdfasdf![](relative/path/to/img.png "alt desc")![xsom](justimg.JPEG)haha
    hehe
    """
    # m = ATTACHMENT_PATTERN.search(s)
    # print(m and m.groupdict())
    for m in ATTACHMENT_PATTERN.finditer(s):
        print(m.group())

    a = AttachmentHandler("", "")
    subret, n = ATTACHMENT_PATTERN.subn(a.replace_link, s)
    print(subret, n)
    subprocess.run("""
cd ~
pwd
sleep 2
echo done
    """, shell=True)


if __name__ == "__main__":
    arg1 = "/home/yychi/Documents/learn2live/__zettel/202501082036suckless-windows.md"
    arg2 = "/home/yychi/Documents/BlogHugo//content/post/"
    copy_as_hugo_post(arg1, arg2)
    exit(0)
    if len(sys.argv) == 3:
        notify("args: ", *sys.argv)
        copy_as_hugo_post(sys.argv[1], sys.argv[2])
    else:
        print(USAGE)
