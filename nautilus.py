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

    

    def switch_context(self, context_name):
        """Switch the active context."""
        try:
            contexts, active_context = config.list_kube_config_contexts()
            if context_name not in [ctx['name'] for ctx in contexts]:
                print(f"Context '{context_name}' not found.")
                return False
            
            config.load_kube_config(context=context_name)
            print(f"Switched to context '{context_name}'")
            return True
        except Exception as e:
            print(f"Error switching context: {e}")
            return False

    def apply(self, filename):
        """Apply a configuration file to create or update resources."""
        try:
            with open(filename, 'r') as f:
                docs = yaml.safe_load_all(f)
                for doc in docs:
                    kind = doc.get("kind", "").lower()
                    name = doc["metadata"]["name"]
                    
                    if kind == "deployment":
                        api_instance = self.apps_v1
                        api_func = api_instance.create_namespaced_deployment
                        update_func = api_instance.patch_namespaced_deployment
                    elif kind == "service":
                        api_instance = self.v1
                        api_func = api_instance.create_namespaced_service
                        update_func = api_instance.patch_namespaced_service
                    else:
                        print(f"Unsupported resource kind: {kind}")
                        continue
                    
                    try:
                        api_func(body=doc, namespace=self.namespace)
                        print(f"{kind.capitalize()} '{name}' created.")
                    except client.ApiException as e:
                        if e.status == 409:  # Conflict, resource already exists
                            update_func(name=name, namespace=self.namespace, body=doc)
                            print(f"{kind.capitalize()} '{name}' updated.")
                        else:
                            print(f"Error applying {kind} '{name}': {e}")
        except Exception as e:
            print(f"Error applying configuration: {e}")

    def create(self, resource_type, name, image=None, replicas=None):
        """Create a new resource."""
        try:
            if resource_type.lower() == "deployment":
                body = client.V1Deployment(
                    metadata=client.V1ObjectMeta(name=name),
                    spec=client.V1DeploymentSpec(
                        replicas=replicas,
                        selector=client.V1LabelSelector(
                            match_labels={"app": name}
                        ),
                        template=client.V1PodTemplateSpec(
                            metadata=client.V1ObjectMeta(labels={"app": name}),
                            spec=client.V1PodSpec(
                                containers=[client.V1Container(
                                    name=name,
                                    image=image
                                )]
                            )
                        )
                    )
                )
                self.apps_v1.create_namespaced_deployment(namespace=self.namespace, body=body)
                print(f"Deployment '{name}' created.")
            elif resource_type.lower() == "service":
                body = client.V1Service(
                    metadata=client.V1ObjectMeta(name=name),
                    spec=client.V1ServiceSpec(
                        selector={"app": name},
                        ports=[client.V1ServicePort(port=80)]
                    )
                )
                self.v1.create_namespaced_service(namespace=self.namespace, body=body)
                print(f"Service '{name}' created.")
            else:
                print(f"Unsupported resource type: {resource_type}")
        except client.ApiException as e:
            print(f"Error creating {resource_type}: {e}")

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
    parser.add_argument("--switch-context", help="Switch to a different context")
    parser.add_argument("--apply", help="Apply a configuration file")
    parser.add_argument("--create", nargs=3, metavar=("RESOURCE_TYPE", "NAME", "IMAGE"),
                        help="Create a new resource (deployment or service)")
    parser.add_argument("--replicas", type=int, help="Number of replicas for deployment")
    args = parser.parse_args()

    k8s_cluster = DescribeK8s("default")

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
    elif args.switch_context:
        k8s_cluster.switch_context(args.switch_context)
    elif args.apply:
        k8s_cluster.apply(args.apply)
    elif args.create:
        resource_type, name, image = args.create
        k8s_cluster.create(resource_type, name, image, args.replicas)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
