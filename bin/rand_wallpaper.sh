#!/bin/bash
#shopt -s nullglob
 
#===change these config start===

#wallpapers directory path
path=/home/yychi/Downloads/chromeDownloads/faraway

#time interval
interval=45m

#===change these config end===

cd $path

while true; do
	files=()

	for i in *.jpg *.png; do
		[[ -f $i ]] && files+=("$i")
	done
	range=${#files[@]}
	
	((range)) && feh --bg-fill "${files[RANDOM % range]}"
	
	sleep $interval
done


# another script  refer https://wiki.archlinux.org/index.php/Feh_(%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87)
# while true; do
# 	find ~/.wallpaper -type f \( -name '*.jpg' -o -name '*.png' \) -print0 |
# 		shuf -n1 -z | xargs -0 feh --bg-scale
# 	sleep 15m
# done
