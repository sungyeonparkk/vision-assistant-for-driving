import yaml
from kubernetes import config


def load_context():
    # Load the existing kubeconfig
    with open('kubectx.yaml', 'r') as f:
        kubeconfig = yaml.safe_load(f)

    return config.new_client_from_config_dict(kubeconfig)
