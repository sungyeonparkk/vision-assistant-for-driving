import argparse
import time

import yaml
from kubernetes import client, config

from resources.kubectl import load_context

context = load_context()


def create_pod(pod_file_path, namespace="cufft"):
    api_instance = client.CoreV1Api(api_client=context)

    # Load the pod manifest from file
    with open(pod_file_path, 'r') as f:
        pod_manifest = yaml.safe_load(f)

    pod_name = pod_manifest['metadata']['name']
    pod_manifest['metadata']['name'] = f"{pod_name}-{time.time()}"
    try:
        api_response = api_instance.create_namespaced_pod(body=pod_manifest, namespace=namespace)
        print(f"Pod {api_response} created | file_path {pod_file_path}")
    except client.exceptions.ApiException as e:
        print(e)


if __name__ == '__main__':
    create_pod('pod/experiment.yaml')
