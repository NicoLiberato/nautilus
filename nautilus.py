#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse

from kubernetes import client, config
from datetime import datetime, timezone


class DescribeK8s:
    """Initialize the DescribeK8s object with the given namespace."""

    def __init__(self, namespace):
        self.config = config.load_kube_config()
        self.namespace = namespace
        self.v1 = client.CoreV1Api()

    def set_namespace(self, namespace):
        """Set the namespace for the DescribeK8s object."""
        self.namespace = namespace

    def get_api_resources(self):
        """Get API resources information."""
        try:
            return self.v1.get_api_resources()
        except client.ApiException as e:
            print(f"Error getting API resources: {e}")
            return None

    def get_api_server(self):
        """Get the API server information."""
        apiserver = self.v1.api_client.configuration.host
        return f"Kubernetes control plane is running at {apiserver}"

    def get_kube_dns_info(self):
        """Get KubeDNS service information."""
        try:
            return self.v1.list_namespaced_service(self.namespace)
        except client.ApiException as e:
            print(f"Error getting KubeDNS info: {e}")
            return None

    def get_kube_dns_url(self):
        """Get the KubeDNS URL."""
        kube_dns = self.get_kube_dns_info()
        if kube_dns:
            for service in kube_dns.items:
                if service.metadata.name == "kube-dns":
                    return service.spec.cluster_ip
        return None

    def print_api_versions(self):
        """Print API versions information."""
        try:
            api_client = client.ApiClient()
            version_api = client.VersionApi(api_client)
            api_versions = version_api.get_code()
            print("Kubernetes API Versions:")
            print(f"Major: {api_versions.major}")
            print(f"Minor: {api_versions.minor}")
            print(f"Platform: {api_versions.platform}")
        except client.ApiException as e:
            print(f"Error getting API versions: {e}")

    def print_cluster_info(self):
        """Print cluster information."""
        api_resources = self.get_api_resources()
        if api_resources:
            print(f"API Resources: {len(api_resources.resources)}")

        host = self.v1.api_client.configuration.host
        print(
            f"KubeDNS is running at http://{host}/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy")
        print(f"Kubernetes control plane is running at {host}")

    def get_nodes(self):
        """Get information about all nodes in the cluster."""
        try:
            nodes = self.v1.list_node()
            return nodes.items
        except client.ApiException as e:
            print(f"Error getting nodes: {e}")
            return None

    # namespace commands
    def get_all_namespaces(self):
        """List all available namespaces in the Kubernetes cluster."""
        try:
            api_response = self.v1.list_namespace()
            namespaces = api_response.items
            return namespaces
        except client.ApiException as e:
            print(f"Exception when listing namespaces: {e}")
            return None

    def print_namespaces_info(self):
        """Print information about all namespaces in the cluster."""
        namespaces = self.get_all_namespaces()
        print("NAMESPACE\tSTATUS\tAGE")
        if namespaces:
            for namespace in namespaces:
                name = namespace.metadata.name
                status = namespace.status.phase if namespace.status else "Unknown"
                age = self.calculate_age(namespace.metadata.creation_timestamp)
                print(f"{name}\t{status}\t{age}")
        print()

    def print_nodes_info(self):
        """Print information about all nodes in the cluster."""
        nodes = self.get_nodes()
        if nodes:
            print("Cluster Nodes:")
            for node in nodes:
                print(f"  Name: {node.metadata.name}")
                print(f"    Status: {node.status.phase}")
                print(
                    f"    Kubernetes Version: {node.status.node_info.kubelet_version}")
                print(f"    OS Image: {node.status.node_info.os_image}")
                print(
                    f"    Container Runtime: {node.status.node_info.container_runtime_version}")
                print("    Addresses:")
                for address in node.status.addresses:
                    print(f"      {address.type}: {address.address}")
                print()
        else:
            print("No nodes found or error occurred while fetching nodes.")

    
    def switch_namespace(self, name):
        """Switch the active namespace in the current context."""
        try:
            # Load the current config
            kube_config = config.load_kube_config()  
            # Get the current context
            current_context = config.list_kube_config_contexts()[1]
            # Update the namespace in the current context
            current_context['context']['namespace'] = name        
            # Update the current context in the config
            kube_config.set_context(current_context['name'], current_context['context'])       
            # Save the config
            kube_config.persist_config()
            print(f"Switched to namespace '{name}'")
            return True
        except Exception as e:
            print(f"Error switching namespace: {e}")
            return False

    @staticmethod
    def calculate_age(creation_time):
        """Calculate the age of a resource based on its creation time."""
        now = datetime.now(timezone.utc)
        age = now - creation_time
        if age.days > 0:
            return f"{age.days}d"
        elif age.seconds >= 3600:
            return f"{age.seconds // 3600}h"
        elif age.seconds >= 60:
            return f"{age.seconds // 60}m"
        else:
            return f"{age.seconds}s"
        

def main():
    parser = argparse.ArgumentParser(
        description="Describe Kubernetes cluster information")
    parser.add_argument(
        "--namespace", help="Set the namespace to get the information")
    parser.add_argument("--cluster-info", "--cluster",
                        help="Print the cluster information", action="store_true")
    parser.add_argument(
        "--api-versions", help="Print the API versions", action="store_true")
    parser.add_argument(
        "--nodes", help="Print information about all nodes", action="store_true")
    parser.add_argument(
        "--list_namespaces", help="Print information about all namespaces", action="store_true")
    parser.add_argument("--switch-namespace", help="Switch context/namespace")
    args = parser.parse_args()

    k8s_cluster = DescribeK8s("kube-system")

    if args.namespace:
        k8s_cluster.set_namespace(args.namespace)

    if args.cluster_info:
        k8s_cluster.print_cluster_info()
    elif args.api_versions:
        k8s_cluster.print_api_versions()
    elif args.nodes:
        k8s_cluster.print_nodes_info()
    elif args.list_namespaces:
        k8s_cluster.print_namespaces_info()
    elif args.switch_namespace:
        k8s_cluster.switch_namespace(args.namespace)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
