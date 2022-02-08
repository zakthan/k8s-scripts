import argparse
import numpy as np
# importing the sys module
from sys  import path as syspath
  
# appending the directory of mod.py 
# in the sys.path list
syspath.append('../') 
from functions import runcommand
from functions import output_command
from functions import look_for_other_nfs_servers
from functions import write_to_a_file


##Get a list of the namespaces. 
get_namespaces_command="kubectl get ns --no-headers -o jsonpath='{.items[*].metadata.name}'"
list_of_namespaces = output_command(get_namespaces_command)
##debug##print(type(list_of_namespaces))
##debug##print(list_of_namespaces)

##counter for values bigger than threshold
counter = 0

##For all the namespaces
for current_namespace in list_of_namespaces:
  ##Get a list of pods per namespace
  if current_namespace=="default" or current_namespace=="velero" or current_namespace=="anchore" or current_namespace=="filebeat" or current_namespace=="dynatrace" or current_namespace=="busybox" or current_namespace=="istio-cosmote"  or current_namespace=="istio-system" or current_namespace=="kube-system" or current_namespace=="metricbeat" or current_namespace=="monitoring":
   continue
  get_po_per_namespace_command="kubectl -n %s  get po -o jsonpath='{.items[*].metadata.name}'"%current_namespace
  list_of_pods_per_namespace = output_command(get_po_per_namespace_command,"True")
  for pod in list_of_pods_per_namespace:
     list_mounts_command = "kubectl -n %s exec -it %s -- ps -ef|grep java "%(current_namespace, pod)
     mounts_per_pod = output_command(list_mounts_command,"False","False")
     if len(mounts_per_pod) > 1:
        listToStr = ' '.join(map(str, mounts_per_pod))
        ##print (listToStr)
        substring="MaxRAMPercentage"
        if substring not in listToStr:
          print ("Now checking POD:",pod," for namespace ",current_namespace)
          arr = listToStr.split()
          print (' '.join(map(str,arr)))
