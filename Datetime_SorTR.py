#!/sw/freetools/python/3.9.12/rh70_64/bin/python

import pandas as pd
from tabulate import tabulate
import sys

def file(path):
    data = []
    with open(path, 'r') as f:
        for line in f:
            val = line.strip().split(",", 4)[:5]
            data.append(val)
    df = pd.DataFrame(data, columns= ['Product', 'Version', 'DateTime', 'Author', 'Description'])
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    new_df = df.sort_values(by = ['DateTime']).reset_index(drop=True)
    with open(path, 'w') as f:
        f.write(tabulate(new_df, headers = 'keys', tablefmt = 'psql'))
        f.close()
    r = new_df.to_csv(sep = ',', index = False, header = False)
    return r 

if __name__ == "__main__":
    path = sys.argv[1]
    result = file(path)
    
    if isinstance(result , pd.DataFrame):
        print(result)
    else:
        print(result)
