#!/bin/sh

docker build -t registry.ferrari.snucse.org:30443/attention-x/drive-vision-assistant-experiment:latest .
docker push registry.ferrari.snucse.org:30443/attention-x/drive-vision-assistant-experiment:latest
kubectl delete pod vision-assistant-experiment
kubectl create -f ./resources/pod/experiment.yaml
