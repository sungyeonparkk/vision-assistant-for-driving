#!/bin/sh

kubectl delete pod vision-assistant-experiment
kubectl create -f ./resources/pod/experiment.yaml