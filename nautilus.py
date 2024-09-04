#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse

from kubernetes import client, config


class DescribeK8s:
    """Initialize the DescribeK8s object with the given namespace."""  
    def __init__(self, namespace):
        config.load_kube_config()
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
        print(f"KubeDNS is running at http://{host}/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy")
        print(f"Kubernetes control plane is running at {host}")


def main():
    parser = argparse.ArgumentParser(description="Describe Kubernetes cluster information")
    parser.add_argument("--namespace", help="Set the namespace to get the information")
    parser.add_argument("--cluster-info", "--cluster", help="Print the cluster information", action="store_true")
    parser.add_argument("--api-versions", help="Print the API versions", action="store_true")

    args = parser.parse_args()

    k8s_cluster = DescribeK8s("kube-system")

    if args.namespace:
        k8s_cluster.set_namespace(args.namespace)

    if args.cluster_info:
        k8s_cluster.print_cluster_info()
    elif args.api_versions:
        k8s_cluster.print_api_versions()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()