#!/bin/sh

pip install -r requirement.txt
torchrun --nproc_per_node=1 python /root/vision-assistant-for-driving/train.py --cfg-path ./train_configs/drive_finetune.yaml