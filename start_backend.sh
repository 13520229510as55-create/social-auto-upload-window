#!/bin/bash
# 后端服务启动脚本（设置 DISPLAY 环境变量）

export DISPLAY=:99
export PYTHONUNBUFFERED=1

cd /home/ubuntu/social-auto-upload

exec /home/ubuntu/miniconda3/envs/social-auto-upload/bin/python3 sau_backend.py
