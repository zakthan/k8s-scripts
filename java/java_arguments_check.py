import argparse
import numpy as np
# importing the sys module
from sys  import path as syspath
from sys  import exit as sysexit
  
# appending the directory of mod.py 
# in the sys.path list
syspath.append('../') 
from functions import runcommand
from functions import output_command
from functions import look_for_other_nfs_servers
from functions import write_to_a_file


# Create the parser
parser = argparse.ArgumentParser()

# Add an argument
parser.add_argument('--namespace', type=str, required=True)

# Parse the argument. If argument is empty or not good put default argument 
try:
  args = parser.parse_args()
  ##The usage threshold if none is given as an argument
  ##The ip of the NFS server
  list_of_namespaces_string  = args.namespace
  ##stupid solution to parse namespace later correct. Need to code this in a more elegant way
  list_of_namespaces=[list_of_namespaces_string,""]
except:
  ##Get a list of the namespaces. 
  get_namespaces_command="kubectl get ns --no-headers -o jsonpath='{.items[*].metadata.name}'"
  list_of_namespaces = output_command(get_namespaces_command)



##substring to search
substring="MaxRAMPercentage"


##For all the current_namespaces
for current_namespace in list_of_namespaces:
  ##stupid control for case namespace argument is selected. Need to code this in a more elegant way
  if not current_namespace:
     continue

  ##counter for values bigger than threshold
  java_pods_counter = 0
  jcmd_pods_counter = 0
  ps_pod_counter = 0
  ##Get a list of pods per current_namespace
  if current_namespace=="default" or current_namespace=="velero" or current_namespace=="anchore" or current_namespace=="filebeat" or current_namespace=="dynatrace" or current_namespace=="busybox" or current_namespace=="istio-cosmote"  or current_namespace=="istio-system" or current_namespace=="kube-system" or current_namespace=="metricbeat" or current_namespace=="monitoring"  or current_namespace=="tracing" or current_namespace=="kube-public" or current_namespace=="minio" or current_namespace=="kube-node-lease":
   continue
  get_po_per_current_namespace_command="kubectl -n %s  get po -o jsonpath='{.items[*].metadata.name}'"%current_namespace
  list_of_pods_per_current_namespace = output_command(get_po_per_current_namespace_command,"True")
  for pod in list_of_pods_per_current_namespace:
     ps_java_command = "kubectl -n %s exec -it %s -- ps -ef|grep java "%(current_namespace, pod)
     java_per_pod = output_command(ps_java_command,"False","False")
     returncode, out ,err = runcommand(ps_java_command)
     ##If pod has NOT the ps binary installed
     if returncode != 0:
        jcmd_java_command = "kubectl -n %s exec -it %s -- jcmd 1 VM.flags"%(current_namespace, pod)
        jcmd_per_pod = output_command(jcmd_java_command,"False","False")
        returncode2, out2 ,err2 = runcommand(jcmd_java_command)
        ##If pod HAS the jcmd binary installed and set in PATH
        if returncode2 == 0 :
           matches = []
           java_pods_counter+=1
           print ("Now checking POD:",pod," for current_namespace ",current_namespace)
           listToStr = ' '.join(map(str, jcmd_per_pod))
           arr = listToStr.split()
           print (' '.join(map(str,arr)))
           for match in jcmd_per_pod:
               if substring in match:
                   matches.append(match)
                   java_pods_counter+=1
                   if len(matches) == 0:
                      print ("Now checking POD:",pod," for current_namespace ",current_namespace)
                      print (f"undefined {substring}")
                      print ("Arguments are: ", jcmd_per_pod)
                      jcmd_pods_counter +=1
      
     ## If any pods with java found using ps
     if len(java_per_pod) > 1:
        listToStr = ' '.join(map(str, java_per_pod))
        java_pods_counter+=1
        print ("Now checking POD:",pod," for current_namespace ",current_namespace)
        arr = listToStr.split()
        print (' '.join(map(str,arr)))
        ##print (listToStr)
        if substring not in listToStr:
          ps_pod_counter+=1

  if java_pods_counter == 0:
     print("-----------------------------------------------------------------------------------------------------------------------------------------")
     print(f"For current_namespace {current_namespace} : No java pods were found (or no ps/jcmd binares installed)")
     print("-----------------------------------------------------------------------------------------------------------------------------------------")
  if ps_pod_counter == 0 and jcmd_pods_counter==0 and java_pods_counter > 0:
     print("-----------------------------------------------------------------------------------------------------------------------------------------")
     print(f"For current_namespace {current_namespace} : No pods without {substring} were found. Total number of java pods found: {java_pods_counter}")
     print("-----------------------------------------------------------------------------------------------------------------------------------------")
  if ps_pod_counter != 0 or jcmd_pods_counter!=0:
     print("-----------------------------------------------------------------------------------------------------------------------------------------")
     print(f"For current_namespace {current_namespace} : Found {jcmd_pods_counter + ps_pod_counter} pods  without {substring} defined. Total number of java pods found: {java_pods_counter}")
     print("-----------------------------------------------------------------------------------------------------------------------------------------")
