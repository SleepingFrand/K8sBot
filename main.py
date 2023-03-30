from kuberapi import *


pods = get_namespased_items('longhorn-system', 'pod')
print(print_pods_status(get_node())) 