#!/bin/bash
source ~/.bashrc 2>/dev/null || true
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" 2>/dev/null || true

cd /home/ubuntu/social-auto-upload
pm2 delete sau-backend 2>/dev/null || true
sleep 1
export DISPLAY=:99
pm2 start ~/miniconda3/envs/social-auto-upload/bin/python3 --name sau-backend -- sau_backend.py
pm2 save
sleep 2
pm2 status sau-backend
