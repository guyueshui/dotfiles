#!/bin/bash

# 检查参数
if [ -z "$1" ]; then
  echo "用法: $0 <网卡名称> (如 eth0 或 wlan0)"
  exit 1
fi

format_speed() {
  local sp=$1
  if [ $sp -lt 10240 ]; then
    # < 10KB/s, set to 0
    echo "0KB/s"
  elif [ $sp -gt 1048576 ]; then
    echo "$sp / 1048576" | bc -l | awk '{printf "%.1fMB/s", $1}'
  else
    echo "$sp / 1024" | bc -l | awk '{printf "%.1fKB/s", $1}'
  fi
}

count=0
mod=3
ethn=$1
while true; do
  # 读取当前流量数据
  RX_pre=$(cat /proc/net/dev | grep "$ethn" | sed 's/:/ /g' | awk '{print $2}')
  TX_pre=$(cat /proc/net/dev | grep "$ethn" | sed 's/:/ /g' | awk '{print $10}')
  
  sleep 1
  
  RX_next=$(cat /proc/net/dev | grep "$ethn" | sed 's/:/ /g' | awk '{print $2}')
  TX_next=$(cat /proc/net/dev | grep "$ethn" | sed 's/:/ /g' | awk '{print $10}')
  
  #clear
  
  # 计算速率
  RX=$((${RX_next} - ${RX_pre}))
  TX=$((${TX_next} - ${TX_pre}))
  
  RX=$(format_speed $RX)
  TX=$(format_speed $TX)
  
  #echo -e "\t RX\t TX"
  #echo -e "$ethn\t $RX\t $TX"
  if (( ++count % mod == 0 )); then
    echo "{\"RX\": \"$RX\", \"TX\": \"$TX\"}"
  fi
done

