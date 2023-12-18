#!/sw/freetools/python/3.9.12/rh70_64/bin/python
import pandas as pd
import re
import os
import yaml
import ast
from tabulate import tabulate

def yaml_df(path):
    with open(path, 'r') as f:
        waive_file = yaml.safe_load(f)
        f.close()
    waive_file = str(waive_file)
    waive_file = re.sub(r'{\'waive rules\':\s*', '', waive_file)
    waive_file = waive_file[:-1]
    waive = ast.literal_eval(waive_file)
    waive = [{'waive rules': k, **v} for k, v in waive.items()]
    df = pd.json_normalize(waive)
    df.index += 1
    with open(os.path.join(os.getcwd(), 'waive_yaml_dataframe'), 'w') as f:
        f.write(tabulate(df, headers='keys', tablefmt='plsql'))
        f.close()
    print('File Created : ', os.path.join(os.getcwd(), 'waive_yaml_dataframe'))

if __name__ == '__main__':
    input = input("Enter waive.yaml/cfs file : ")
    yaml_df(input)
