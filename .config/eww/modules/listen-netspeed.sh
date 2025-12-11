#!/bin/bash

# 检查参数
if [ -z "$1" ]; then
  echo "用法: $0 <网卡名称> (如 eth0 或 wlan0)"
  exit 1
fi

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
  
  if [ $RX -lt 1024 ]; then
    RX="${RX}B/s"
  elif [ $RX -gt 1048576 ]; then
    RX=$(echo "$RX / 1048576" | bc -l | awk '{printf "%.1fMB/s", $1}')
  else
    RX=$(echo "$RX / 1024" | bc -l | awk '{printf "%.1fKB/s", $1}')
  fi
  
  if [ $TX -lt 1024 ]; then
    TX="${TX}B/s"
  elif [ $TX -gt 1048576 ]; then
    TX=$(echo "$TX / 1048576" | bc -l | awk '{printf "%.1fMB/s", $1}')
  else
    TX=$(echo "$TX / 1024" | bc -l | awk '{printf "%.1fKB/s", $1}')
  fi
  
  #echo -e "\t RX\t TX"
  #echo -e "$ethn\t $RX\t $TX"
  if (( ++count % mod == 0 )); then
    echo "{\"RX\": \"$RX\", \"TX\": \"$TX\"}"
  fi
done

