#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os

from kubernetes import client, config, watch

class DescribeK8s:
    def __init__(self, namespace):        
        config.load_kube_config()
        self.namespace = namespace
        self.v1 = client.CoreV1Api()

    def get_cluster_info(self):
        info = self.v1.get_api_resources()
        return info

    # def get_controller_info(self):
    #     controllers = self.v1.list_namespaced_replication_controller(self.namespace)
    #     return controllers  
    
    def get_api_server(self):
        apiserver = self.v1.api_client.configuration.host
        cluster_info= "Kubernetes control plane is running" + str(apiserver)

    def get_kube_dns_info(self):
        kube_dns = self.v1.list_namespaced_service(self.namespace)
        return kube_dns
    
    #KubeDNS is running at https://127.0.0.1:33521/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy
    def get_kube_dns_url(self):
        kube_dns = self.get_kube_dns_info()
        for i in kube_dns.items:
            if i.metadata.name == "kube-dns":
                return i.spec.cluster_ip
    

def main():
    
    k8s_cluster = DescribeK8s("kube-system")
    
    parser = argparse.ArgumentParser(description="Nautilus:  navigate the cluster manager with Python./n")
    subparsers = parser.add_subparsers(dest="command")
    
    for method_name in ['get_api_server', 'get_kube_dns_url']:
        subparser = subparsers.add_parser(method_name)
        subparser.add_argument('name')
        subparser.set_defaults(func=method)
        
    args = parser.parse_args()
    if args.command:
        args.func(args.name)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()