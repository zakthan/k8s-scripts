import subprocess
import sys
import os

nfsserver="10.53.187.250"
usage_threshold=70
##Get a list of the namespaces. 
##subprocess.check_output is returing bytes , so we conver bytes to string with decode and string to list with split
list_of_namespaces = subprocess.check_output("kubectl get ns --no-headers -o jsonpath='{.items[*].metadata.name}'",shell=True).decode(sys.stdout.encoding).split(" ")
#debug#print(type(list_of_namespaces))
#debug#print(list_of_namespaces)

##Get a list of pods per namespace
##Use the same convertion like namespaces to convert from bytes to a list
for current_namespace in list_of_namespaces:
 ##print(current_namespace)
 list_of_pods_per_namespace = subprocess.check_output("kubectl -n %s  get po -o jsonpath='{.items[*].metadata.name}'" % current_namespace,shell=True).decode(sys.stdout.encoding).split(" ")
 #debug#print(type(list_of_pods_per_namespace))
 #debug#print(list_of_pods_per_namespace)
 if len(list_of_pods_per_namespace) > 0 and len(list_of_pods_per_namespace[0]) >0 :
  for pod in list_of_pods_per_namespace:
   returned_code = os.system("kubectl -n {0} exec -it {1} -- mount 2>/dev/null|grep {2}".format(current_namespace,pod,nfsserver))
   #debug#print(current_namespace,pod)
   if returned_code == 0:
    command_mount = 'kubectl -n {0} exec -it {1} -- mount 2>/dev/null|grep {2}'
    mounts_per_pod = subprocess.check_output(command_mount.format(current_namespace,pod,nfsserver),shell=True).decode(sys.stdout.encoding).split(" ")
    
    substring = "var/lib/kubelet/pods"
    if not substring in mounts_per_pod[2]:
     command_df = 'kubectl -n {0} exec -it {1} -- df -hP {2}'
     df_usage= subprocess.check_output(command_df.format(current_namespace,pod,mounts_per_pod[2]),shell=True).decode(sys.stdout.encoding).split(" ")
     if int(df_usage[-2].replace("%", "")) >= usage_threshold:
      print("You need to check usage for mount point ", df_usage[-1]," .The usage is ", df_usage[-2],"The pod is ",pod," and the namespace is ",current_namespace)
