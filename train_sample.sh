#!/bin/sh

torchrun --nproc_per_node=1 train.py --cfg-path ./train_configs/drive_finetune_test.yaml