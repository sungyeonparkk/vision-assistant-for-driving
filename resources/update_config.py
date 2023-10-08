import argparse

import yaml
from kubernetes import client, config, utils

from resources.kubectl import load_context

context = load_context()


def update_config_map(config_map_name, file_path, namespace="cufft"):
    # Load the file content
    with open(file_path, 'r') as f:
        file_content = yaml.safe_load(f)

    api_instance = client.CoreV1Api(api_client=context)

    # Retrieve the existing ConfigMap
    config_map = api_instance.read_namespaced_config_map(name=config_map_name, namespace=namespace)
    config_map.data = {'drive_finetune.yaml': yaml.dump(file_content)}

    # Replace the data in the ConfigMap
    # Update the ConfigMap
    try:
        response = api_instance.replace_namespaced_config_map(config_map_name, namespace, config_map)
        print(response)
        print(f"ConfigMap {config_map_name} replaced with content from {file_path}")
    except client.exceptions.ApiException as e:
        print(e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-path', type=str, help='Name of the configmap to update', required=True)
    args = parser.parse_args()
    update_config_map('train-config', args.config_path)
