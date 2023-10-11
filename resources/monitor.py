from kubectl import load_context
from kubernetes import client, config

context = load_context()

def list_all_pods(namespace='cufft'):
    v1 = client.CoreV1Api(context)

    # Fetch pods from the specified namespace or from all namespaces if none is provided
    if namespace:
        pods = v1.list_namespaced_pod(namespace)
    else:
        pods = v1.list_pod_for_all_namespaces()

    for pod in pods.items:
        print(f"{pod.metadata.name} | {pod.status.phase}")

def stream_pod_logs(namespace, pod_name, container_name=None):
    v1 = client.CoreV1Api(api_client=context)

    try:
        for log_line in v1.read_namespaced_pod_log(pod_name, namespace, container=container_name, follow=True, _preload_content=False):
            print(log_line.strip().decode('utf-8'))

    except client.ApiException as e:
        print(f"Exception when streaming logs from {pod_name}: {e}")


if __name__ == '__main__':
    list_all_pods()
    pod_name = input("Enter pod name to stream logs: ")
    stream_pod_logs('cufft', pod_name)
