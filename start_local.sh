#!/bin/bash
cd /Users/a58/Desktop/social-auto-upload
eval "$(conda shell.zsh hook)"
conda activate social-auto-upload
export PATH="/opt/homebrew/Caskroom/miniconda/base/envs/social-auto-upload/bin:$PATH"
python3 sau_backend.py
