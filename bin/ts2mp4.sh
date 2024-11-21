#!/bin/bash
# merge ts files to mp4
#
#: In case of aes encrypted stream like
#:	#EXT-X-KEY:METHOD=AES-128,URI="https://example.com/key",IV=0x217a7da32d1a2587d35bb745d6642f27
#: please refer to https://idof.medium.com/download-and-decrypt-aes-128-m3u8-playlists-495c12d6543a

set -e
fongmi_path="storage/shared/Android/data/com.fongmi.android.tv/files/Video/Download/"

# cd $fongmi_path
# specific download directory
# cd xxx


merge()
{
	find *.ts -printf "file %p\n" | sort -n -t_ -k2 > file.list
	[ -s file.list ] && ffmpeg -f concat -safe 0 -i file.list -c copy out.mp4
}

cd_and_merge()
{
	cd $1
	merge
}

cd_and_merge $1
