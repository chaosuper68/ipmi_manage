#!/bin/bash

pkill -f sensors_api
pkill -f call_ipmi
pkill -f main_page.py

sleep 1

# Step 2
echo "Step 2: Starting backend.py"
nohup python sensors_api.py > backend.out &

CONDA_PATH='/home/ubuntu/anaconda3/condabin/conda'
echo "Step 1: Starting ipmi tools "
source /home/ubuntu/anaconda3/etc/profile.d/conda.sh
conda activate ai_medpaper
nohup python call_ipmi.py > call_ipmi.out &
sleep 3

echo "Step 2: Starting main_page.py"
nohup streamlit run main_page.py --server.port=8503 > web_page.out &

