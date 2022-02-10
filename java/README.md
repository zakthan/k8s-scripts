# Scripts related to java

## java_arguments_check.py 

### Python script to calculate if a substring exist at the java arguments of a java proccess of a pod

$ python3 java_arguments_check.py -h
usage: java_arguments_check.py [-h] [--namespace NAMESPACE] --string_to_search
                               STRING_TO_SEARCH

optional arguments:
  -h, --help            show this help message and exit
  --namespace NAMESPACE Namespace to search. Default is all namespaces
  --string_to_search STRING_TO_SEARCH Default substring to search. Default is MaxRAMPercentage
