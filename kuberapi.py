from kubernetes import client, config
from config import KUBER_CONFIG

 # Подключение к Kubernetes API
config.load_kube_config(KUBER_CONFIG)
 # Создание объекта API
v1 = client.CoreV1Api()
appv1 = client.AppsV1Api()
extv1 = client.ApiextensionsV1Api()

'''
ConfigMap - структура для хранения конфигурационных данных.
class kubernetes.client.V1ConfigMap(
    api_version=None,
    kind=None,
    metadata=None,
    data=None,
    binary_data=None
)

Secret - структура для хранения секретных данных.
class kubernetes.client.V1Secret(
    api_version=None,
    kind=None,
    metadata=None,
    data=None,
    string_data=None,
    type=None
)

Service - структура для описания сервисов.
class kubernetes.client.V1Service(
    api_version=None,
    kind=None,
    metadata=None,
    spec=None,
    status=None
)

Pod - структура для описания подов.
class kubernetes.client.V1Pod(
    api_version=None,
    kind=None,
    metadata=None,
    spec=None,
    status=None
)

Deployment - структура для описания деплойментов.
class kubernetes.client.V1Deployment(
    api_version=None,
    kind=None,
    metadata=None,
    spec=None,
    status=None
)

Namespace - структура для описания пространств имен.
class kubernetes.client.V1Namespace(
    api_version=None,
    kind=None,
    metadata=None,
    spec=None,
    status=None
)

Node - структура для описания узлов.
class kubernetes.client.V1Node(
    api_version=None,
    kind=None,
    metadata=None,
    spec=None,
    status=None
)

Event - структура для описания событий.
class kubernetes.client.V1Event(
    api_version=None,
    kind=None,
    metadata=None,
    involved_object=None,
    reason=None,
    message=None,
    source=None,
    first_timestamp=None,
    last_timestamp=None,
    count=None,
    type=None,
    event_time=None
)
'''

def get_namespaces():
    return v1.list_namespace()

def get_node() -> client.V1NodeList:
    return v1.list_node()

def print_namespase_list() -> str:
    return 'namespaces:\n' + '\n'.join(get_name(i) for i in get_namespaces().items)

def get_namespased_items(namespace='default', v1type='pod'):
    return {'pod':v1.list_namespaced_pod(namespace),
           'configmap':v1.list_namespaced_config_map(namespace),
           'endpoints':v1.list_namespaced_endpoints(namespace),
           'event':v1.list_namespaced_event(namespace),
           'limitrange':v1.list_namespaced_limit_range(namespace),
           'pvc':v1.list_namespaced_persistent_volume_claim(namespace),
           'podtemplate':v1.list_namespaced_pod_template(namespace),
           'replicationcontroller':v1.list_namespaced_replication_controller(namespace),
           'resourcequota':v1.list_namespaced_resource_quota(namespace),
           'secret':v1.list_namespaced_secret(namespace),
           'service':v1.list_namespaced_service(namespace),
           'serviceaccount':v1.list_namespaced_service_account(namespace),
           'deployment':appv1.list_namespaced_deployment(namespace),
           'controllerrevision':appv1.list_namespaced_controller_revision(namespace),
           'daemon_set':appv1.list_namespaced_daemon_set(namespace),
           'replicaset':appv1.list_namespaced_replica_set(namespace),
           'statefulset':appv1.list_namespaced_stateful_set(namespace)}.get(v1type)

def get_name(item=None) -> str:
    if item != None:
        try:
            return item.metadata.name
        except Exception as e:
            print('Ошибка: %s\n' % e)
    return ''

def print_items_status(items=None) -> str:
    if items != None:
        if type(items) in [client.V1PodList, client.V1NodeList, client.V1DeploymentList]:
            items = items.items
        elif type(items) != dict:
            return ''
        if len(items) == 0:
            return ''
        if type(items[0]) == client.V1Pod:
            return '\n'.join([i.metadata.name + ' Status: ' + i.status.phase for i in items])
        elif type(items[0]) == client.V1Deployment:
            return '\n'.join([i.metadata.name + ' Status: ' + f'{i.status.replicas}/{i.status.ready_replicas}' for i in items])
        elif type(items[0]) == client.V1Node:
            return '\n'.join([f"{i.metadata.name} Status: {'Reday' if i.status.conditions[-1].status else 'Not Ready'}" for i in items])

def get_metadata(item=None):
    if item != None:
        try:
            return item.metadata
        except Exception as e:
            print('Ошибка: %s\n' % e)

def delete_pod(pod = None):
    if pod != None:
        try:
            v1.delete_namespaced_pod(pod.metadata.name, pod.metadata.namespace)
        except Exception as e:
            print('Ошибка: %s\n' % e)

def Schedule_node_mode(node = None, Schedule = False):
    if node != None:
        # Настройка Schedule
        try:
            v1.patch_node(node, {"spec": {"unschedulable": Schedule}})
            print(f"{''if Schedule else 'No' }Schedule установлен на {node}")
        except ApiException as e:
            print('Ошибка: %s\n' % e)
            
def Drain_node(node = None):
    if node != None:
        try:
            pods = v1.list_pod_for_all_namespaces(field_selector=f"spec.nodeName={node}").items
            Schedule_node_mode(node, True)

            # Удалите каждый под:
            for pod in pods:
                v1.delete_namespaced_pod(
                    name=pod.metadata.name,
                    namespace=pod.metadata.namespace,

                    body=client.V1DeleteOptions())
            print("Pod удалины из node " + node)
        except Exception as e:
            print('Ошибка: %s\n' % e)

def get_logs_pod(pod = None, lines=10):
    if type(pod) == client.V1Pod:
        try:
            return pod.metadata.name + ' ' + pod.metadata.namespace + '\n' + v1.read_namespaced_pod_log(name=pod.metadata.name, namespace=pod.metadata.namespace, tail_lines=lines) 

        except Exception as e:
            return 'Ошибка в получении логов с ' + pod.metadata.name + ' ' + pod.metadata.namespace

def get_logs_pods(pods = None, lines=10):
    if type(pods) == client.V1PodList:
        pods_items = pods.items
        logs = []
        for pod in pods_items:
            logs.append(get_logs_pod(pod, lines))
        return logs

def get_pod_info(pod_name, namespace):
    return v1.read_namespaced_pod(name=pod_name, namespace=namespace)