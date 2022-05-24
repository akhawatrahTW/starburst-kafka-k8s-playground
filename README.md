# Starburst playground over Minikube

The current setup contains the following components:
- Kafka cluster
- Schema registry
- Starburst cluster
- Test data generator

The playground creates a one-broker kafka cluster and one-worker Starburst cluster.
It also creates a test data generation deployment.
This will hopefully provide enough data to play with Starburst.
The test-data-generator deployment runs a python script that will
keep on generating test data until the pod is terminated. This deployment
can be used to send custom test events.

## Setup
Requirements:
* Minikube
* Kubectl
* Starburst license. This is to be added in [starburstdata.license](./manifests/starburst-cluster.yml) for both the coordinator and the worker nodes.

Run the following script to start the cluster (It seems to be better to run this in a new terminal window each time, to
avoid missing up docker-env var):
```
{project-root} > ./scripts/create-playground.sh
```

All k8s components will be created under the `starburst-playground` namespace.

Wait a couple of minutes until all pods are created:
```
❯ kubectl get pods --namespace starburst-playground
NAME                                     READY   STATUS    RESTARTS        AGE
kafka-0                                  1/1     Running   0               6m33s
schema-registry-6f8b49f868-xgf5m         1/1     Running   3 (5m25s ago)   6m33s
starburst-coordinator-7557875c9f-4l8gb   1/1     Running   0               6m33s
starburst-worker-59dbf4df6f-q9k22        1/1     Running   0               6m33s
test-data-generator-bf74cfbf9-jxwn2      1/1     Running   0               6m33s
zookeeper-0                              1/1     Running   0               6m33s
```
The `test-data-generator` pod will be the last to be created after the kafka cluster is ready. It
checks the schema-registry endpoint.
# Interaction with Starburst
You can run queries against the starburst cluster through the web ui. Configure port forwarding first:
```
kubectl port-forward {coordinator-pod-name} 8080:8080 --namespace starburst-playground
```
Now the web ui can be accessed through `http://localhost:8080`. Type anything as the user name to login.

## Cleanup
Run the following script to terminate the cluster:
```
{project-root} > ./scripts/delete-playground.sh
```
