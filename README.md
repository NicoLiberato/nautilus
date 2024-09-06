![nautilus](images/output.jpg)
=============

# nautilus
CLI or command line tool for communicating with a Kubernetes cluster. This project is a basic exercise designed to simplify the way Kubernetes commands are typed and executed. It provides a limited set of commands to interact with a Kubernetes cluster, making it easier for beginners to understand and use Kubernetes.

## Prerequisites

- Python 3.x
- Kubernetes Python client library (`kubernetes`)
- PyYAML library (pyyaml)

You can install the Kubernetes client library using pip:

```sh
pip install kubernetes 
```

## Usage

The script can be run with a few simple command-line arguments to retrieve different pieces of information about the Kubernetes cluster.

### Command-Line Arguments

--namespace: Set the namespace to get the information.
--cluster-info or --cluster: Print the cluster information.
--api-versions: Print the API versions.


### Examples

1. **Print Cluster Information:**

   ```sh
   python3 nautilus.py --cluster-info
   ```

2. **Apply a Configuration File:**

   ```sh
   python3 nautilus.py --apply config.yaml
   ```

3. **Create a Deployment:**

   ```sh
   python3 nautilus.py --create deployment my-app my-image:latest --replicas 3
   ```

4. **Create a Service:**
   ```sh
   python3 nautilus.py --create service my-service
   ```

4. **Switch Context:**
   ```sh
   python3 nautilus.py --switch-context my-context
   ```

### How to test commands

For example, install kind in your  Linux box:
```sh
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.24.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```
Create a cluster and test the commands
```sh
kind create cluster --name my-cluster
```
Test the nodes coomnd , running 
```sh
python3 nautilus.py --nodes
```

## Documentation and references

For more information, refer to the following resources:

- Kubernetes Documentation  : <https://kubernetes.io/docs/home/>
- Kubernetes v1 API Reference  : <https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.24/>
- Kubernetes Python Client : : <https://github.com/kubernetes-client/python>

