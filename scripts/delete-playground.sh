#!/bin/bash

set -e

kubectl delete namespace starburst-playground

minikube stop
