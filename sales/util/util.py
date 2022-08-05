import yaml
from sales.exception import SalesException
import os, sys

def read_yaml(file_path: str)-> dict:
    """
    reads a yaml file path and gives the output as a dictionary
    
    """
    try:

        with open(file_path, 'rb') as yaml_file:
            return yaml.safe_load(yaml_file)

    except Exception as e:
        raise SalesException(e,sys) from e


