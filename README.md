![My Image](images/output.jpg)

# nautilus
CLI or command line tool for communicating with a Kubernetes cluster. This project is a basic exercise designed to simplify the way Kubernetes commands are typed and executed. It provides a limited set of commands to interact with a Kubernetes cluster, making it easier for beginners to understand and use Kubernetes.

## Prerequisites

- Python 3.x
- Kubernetes Python client library (`kubernetes`)

You can install the Kubernetes client library using pip:

```sh
pip install kubernetes 
```

## Usage

The script can be run with a few simple command-line arguments to retrieve different pieces of information about the Kubernetes cluster.

### Command-Line Arguments

- `--namespace`: Set the namespace to get the information.
- `--cluster-info` or `--cluster`: Print the cluster information.
- `--api-versions`: Print the API versions.

### Examples

1. **Print Cluster Information:**

   ```sh
   python3 nautilus.py --cluster-info

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

## Documentation

For more information, refer to the following resources:

- Kubernetes Documentation
- Kubernetes v1 API Reference

