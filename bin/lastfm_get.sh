#!/bin/bash

# This script replace last.fm API_URL with your custom API_KEY.

API_KEY="249aaf8efc65b21289ee0d0acb33e7c1"
API_SECRET="473d16aafa31ef74a311ece47fe6521f"

URL=$(echo $1 | sed s/YOUR_API_KEY/$API_KEY/g)
curl $URL
