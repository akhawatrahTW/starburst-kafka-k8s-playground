#!/bin/bash

set -e

minikube start --cpus 4 --memory 8192 --disk-size 20GB

kubectl apply -f manifests/namespace.yml

kubectl apply -f manifests/kafka-cluster.yml

kubectl create configmap schema --from-file=schema --namespace starburst-playground

kubectl apply -f manifests/starburst-cluster.yml

kubectl create configmap test-data --from-file=test-data --namespace starburst-playground

kubectl apply -f manifests/test-data-generator.yml
