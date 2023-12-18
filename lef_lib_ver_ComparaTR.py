import pandas as pd
import numpy as np
import re
import sys
from tabulate import tabulate

# lef pins and directions (except pg_pins)
def lef_pin(a): # take strings
    df = pd.DataFrame()
    pin = re.findall(r'PIN\s+(\w+(?:\[\d+\])?)', a)
    dirn = re.findall(r'DIRECTION\s+(\w+)', a)
    df['PIN'] = pin
    df['LEF_DIRN'] = dirn
    df = df.sort_values('PIN').reset_index(drop=True) # just for precaution
    new_df = df[~df['PIN'].str[0].str.islower().fillna(False)] # remove lowercase pin row (pg_pins)
    return new_df 

# lib pins and directions (except pg_pins)
def lib_pin(a): #  take string
    df = pd.DataFrame()
    pin = re.findall(r'pin\(([A-Z]\w+(?:\[\d+\])?)\)', a) # ignore lowercased pg_pins (doesn't have direction)
    dirn = re.findall(r'pin\([A-Z][^)]+\)\s*{[^}]+direction\s*:\s*(\w+)', a) # more generalized
    # earlier : re.findall(r'direction\s*:\s*"([^"]+)"', a)
    df['PIN'] = pin
    df['LIB_DIRN'] = dirn
    df['LIB_DIRN'] = df['LIB_DIRN'].str.upper() # lowercased directions in .lib
    new_df = df.sort_values('PIN').reset_index(drop=True) # just for precaution
    return new_df
 
# verilog pins and directions
def ver_pin(a): #take string
    df = pd.DataFrame()
    ext = re.findall(r'((?:input|output|inout)\s*)(.*?)(?=;)', a) # select only uppercased pins # |output reg 
    # earlier : re.findall('\b(?:input|output)\s+(?:(?:\[[^\]]+\])?\s*[A-Z]\w+)\s*', a)
    ext_ = []
    #for i in range(len(ext)):
    #    ext_.append(ext[i].split(' ', 1))
    # more generalized even for multiple pins in same string
    for i in range(len(ext)):    
        if len(ext[i][1].split(',')) != 1:
            for j in range(len(ext[i][1].split(','))):
                ext_.append((ext[i][0], ext[i][1].split(',')[j]))        
        else:
            ext_.append(ext[i])
    
    df[['VER_DIRN', 'PIN']] = ext_  
    for i in range(len(df)):
        if df['PIN'].str.contains(r'\[.*\]')[i] == True:
            pbkt, pname = df['PIN'][i].split(' ')
            #pbkt = re.findall(r'[a-z]\w+', pbkt)       
            #size = re.findall(r'localparam\s+' + re.escape(pbkt[0]) + r'\s*=\s*(\d+)\s*;', a) 
            #size = int(''.join(filter(str.isdigit, size))) - 1
            size = int(re.findall(r'\d', pbkt)[0]) - int(re.findall(r'\d', pbkt)[1]) + 1
            odr = f'{pname} {[size]}' # reordering, same as lef & lib
            df['PIN'][i] = odr
        else:
            pass
    
    xtnd = [] # creating copies based on size of pins
    for idx, row in df.iterrows():
        if df['PIN'].str.contains(r'\[.*\]')[idx] == True:
            gname, count = df['PIN'][idx].split(' ')
            count = int(count[1:-1])
            for i in range(count): # range(count + 1)
                new_row = row.copy()
                new_row['PIN'] = f"{gname}[{i}]"
                xtnd.append(new_row)
        else:
            xtnd.append(row)
    new_df = pd.DataFrame(xtnd)
    new_df['PIN'] = new_df['PIN'].str.replace(' ', '')
    df_ = new_df.sort_values('PIN').reset_index(drop=True) # just for precaution
    df_['VER_DIRN'] = df_['VER_DIRN'].str.upper() # making every file diections uppercased
    df_['VER_DIRN'] = ' ' + df_['VER_DIRN']
    df_ = df_[['PIN', 'VER_DIRN']]
    return df_

# check directions of pins
def chk(a, b, c): # take lef, lib, ver pins dataframes in that order
    df = pd.merge(b, c, how = 'outer', sort = True)
    df_ = pd.merge(a, df, how = 'outer', sort = True) # combined dataframe
    df_['LEF_DIRN'] = df_['LEF_DIRN'].str.replace(' ', '')
    df_['LIB_DIRN'] = df_['LIB_DIRN'].str.replace(' ', '')
    df_['VER_DIRN'] = df_['VER_DIRN'].str.replace(' ', '')
    df_['CHECK'] = df_.apply(lambda x: x['LEF_DIRN'] == x['LIB_DIRN'] == x['VER_DIRN'], axis = 1) # compare directions in all 3 files
    chk = df_[df_.CHECK.astype(str).str.contains('False')]
    return tabulate(chk, headers = 'keys', tablefmt='psql') if not chk.empty else '######    EVERYTHING LOOKS FINE  ^_^    ######' # return tabulate(df_,headers='keys',tablefmt='psql') # 
    
# takes out string of specific macro
def fnd_lef(a, b): # order : macro, lef file
    new_str = re.findall(r'MACRO\s*' + re.escape(a) + r'(.*?)\s*END\s*' + re.escape(a), b, re.DOTALL)
    return new_str[0]

# takes out string of specific cell
def fnd_lib(a, b): # order : cell, lib file
    try:
        new_str = re.findall(r'cell\s*\(\s*' + re.escape(a) + r'\)(.*?)cell\(', b, re.DOTALL)
        # earlier : re.findall(r'cell\s*\(\s*' + re.escape(a) + r'\s*\)\s*(.*?)\s*\}\n\s*cell\(', b, re.DOTALL)
        return new_str[0]
    except Exception as e:
        e = re.findall(r'cell\s*\(\s*' + re.escape(a) + r'(.*?)\s*}\n\s*}\n\s*}', b, re.DOTALL)
        # earlier : re.findall(r'cell\s*\(\s*' + re.escape(a) + r'\s*\)\s*(.*?)\s*library \*\/\n', b, re.DOTALL)
        return e[0]

# takes out string of specific module
def fnd_ver(a, b): # order : module, ver file
    new_str = re.findall(r'module\s*' + re.escape(a) + r'(.*?)\s*endmodule', b, re.DOTALL) # from module to endmodule
    return new_str[0]

# match all cells in the files & return all matched cells if no error found
def match_cells(a, b, c): # order : lef, lib, ver
    #df = pd.DataFrame()
    try:    
        macro = re.findall(r'MACRO\s*(\w+)\s*\n', a, re.DOTALL)
        cell = re.findall(r'cell\s*\(\s*(\w+)\s*\)\s*\{', b, re.DOTALL)
        mod = re.findall(r'module\s*(\w+)\s*\(', c, re.DOTALL)
        mod = [up for up in mod if up.isupper()]
        # sorting for precaution
        macro.sort()
        cell.sort()
        mod.sort()
        df = pd.DataFrame({'LEF_MACRO': macro, 'LIB_CELL': cell, 'VER_MOD': mod})
        df['CHECK'] = df.apply(lambda x: x['LEF_MACRO'] == x['LIB_CELL'] == x['VER_MOD'], axis = 1)
        check = df[df.CHECK.astype(str).str.contains('False')]
        if not check.empty:
            return print(tabulate(check, headers = 'keys', tablefmt='psql'),'\n\n!!!!     Different Cell Names Detected     !!!!')
            sys.exit(1)
        else:
            return df['LEF_MACRO'].to_list()
        
    except Exception:
        ed1 = pd.DataFrame(macro, columns = ['LEF_MACRO'])
        ed2 = pd.DataFrame(cell, columns = ['LIB_CELL'])
        ed3 = pd.DataFrame(mod, columns = ['VER_MOD'])
        ed = pd.merge(ed1, ed2, how = 'outer', sort = True, left_index = True, right_index = True)
        ed = pd.merge(ed, ed3, how = 'outer', sort = True, left_index = True, right_index = True)
        print(tabulate(ed, headers = 'keys', tablefmt='psql'),'\n\n!!!!         Missing Cells Detected        !!!!')
        e = '\n???? Is the Cell Name or File Order Proper ????\n!!!!  Reminder : lef_file lib_file v_file  !!!!'
        return print(e)

# check pins & directions of each and every cell
def tnt(m, a, b, c):
    try:    
        for i in range(len(m)):
            c1 = fnd_lef(m[i], a)
            #print(c1)
            c2 = fnd_lib(m[i], b)
            #print(c2)
            c3 = fnd_ver(m[i], c)
            #print(c3)
            d1 = lef_pin(c1)
            #print(d1)
            d2 = lib_pin(c2)
            #print(d2)
            d3 = ver_pin(c3)
            #print(d3)
            print(f'Cell {i+1}:\t', m[i])
            print(chk(d1, d2, d3), '\n')
        return '\b'
    except Exception as e:
        e = '\b'
        return e

# read files from paths
def read(lef, lib, ver):
    f1= open(lef, 'r')
    a = f1.read()
    f2 = open(lib, 'r')
    b = f2.read()
    f3 = open(ver, 'r')
    c = f3.read()
    f1.close()
    f2.close()
    f3.close()
    return a, b, c
    
# main function
if __name__ =='__main__':
    if len(sys.argv) != 4:
        print("Use python compare.py lef_file_path lib_file_path ver_file_path")
        sys.exit(1)
    
    lef_file = sys.argv[1]
    lib_file = sys.argv[2]
    ver_file = sys.argv[3]
    a, b, c = read(lef_file, lib_file, ver_file)
    m = match_cells(a, b, c)
    result = tnt(m, a, b, c)
        
    if isinstance(result , pd.DataFrame):
        print(result)
    else:
        print(result)
        


