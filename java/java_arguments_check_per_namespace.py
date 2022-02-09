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
  namespace  = args.namespace
except:
  sysexit("No --namespace argument. Exiting")  


##counter for values bigger than threshold
java_pods_counter = 0
jcmd_pods_counter = 0
ps_pod_counter = 0
##substring to search
substring="MaxRAMPercentage"


get_po_per_namespace_command="kubectl -n %s  get po -o jsonpath='{.items[*].metadata.name}'"%namespace
list_of_pods_per_namespace = output_command(get_po_per_namespace_command,"True")
for pod in list_of_pods_per_namespace:
     ps_java_command = "kubectl -n %s exec -it %s -- ps -ef|grep java "%(namespace, pod)
     java_per_pod = output_command(ps_java_command,"False","False")
     returncode, out ,err = runcommand(ps_java_command)
     ##If pod has NOT the ps binary installed
     if returncode != 0:
        jcmd_java_command = "kubectl -n %s exec -it %s -- jcmd 1 VM.flags"%(namespace, pod)
        jcmd_per_pod = output_command(jcmd_java_command,"False","False")
        returncode2, out2 ,err2 = runcommand(jcmd_java_command)
        ##If pod HAS the jcmd binary installed and set in PATH
        if returncode2 == 0 :
           ##print(jcmd_per_pod)
           matches = []
           for match in jcmd_per_pod:
               if substring in match:
                   matches.append(match)
                   java_pods_counter+=1
                   if len(matches) == 0:
                      print ("Now checking POD:",pod," for namespace ",namespace)
                      print (f"undefined {substring}")
                      print ("Arguments are: ", jcmd_per_pod)
                      jcmd_pods_counter +=1
      
     ## If nay pods with java found using ps
     if len(java_per_pod) > 1:
        listToStr = ' '.join(map(str, java_per_pod))
        java_pods_counter+=1
        ##print (listToStr)
        if substring not in listToStr:
          print ("Now checking POD:",pod," for namespace ",namespace)
          arr = listToStr.split()
          print (' '.join(map(str,arr)))
          ps_pod_counter+=1

if java_pods_counter == 0:
   print(f"For namespace {namespace} : No java pods were found (or no ps/jcmd binares installed)")
if ps_pod_counter == 0 and jcmd_pods_counter==0 and java_pods_counter > 0:
   print(f"For namespace {namespace} : No pods without {substring} were found. Total number of java pods found: {java_pods_counter}")
if ps_pod_counter != 0 or jcmd_pods_counter!=0:
   print(f"For namespace {namespace} : Found {jcmd_pods_counter + ps_pod_counter} pods  without {substring} defined. Total number of java pods found: {java_pods_counter}")
