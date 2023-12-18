#!/sw/freetools/python/3.9.12/rh70_64/bin/python
import re
import pandas as pd
import os
from glob import glob
import subprocess

# create bin_.tcl files
def bin_gen_tcl(src_dir, bin):
    df = pd.read_csv(glob(f'{src_dir}/COMMON/*.map')[0], header = 3, sep = "\s+").rename(columns = lambda x : x.replace('#', '')) # content start from 3rd row ==> header = 3 change if needed
    print(df)
    
    piget = subprocess.check_output("piGetInfo {} {}".format("$DKITROOT", "lyrFilIn"), shell = True)
    piget = piget.decode('utf-8').strip()
    with open(piget, 'r') as l:
        layer = l.read()
    l.close()
           
    poly_res = input("Do you want to add polyResistor (y/n):").lower()
    new_res = None
    if poly_res in ['y', 'yes', '1']:
        new_res = input("Enter polyResistor : ")
        print(f'Using polyResistor {new_res}')
    elif poly_res in ['n', 'no', '0']:
        res = re.findall(r'(siprot)\s*drawing', layer)
        print(f'Using polyResistor {res}')
    
    for metopt, metext in df[['metalOption','metext']].itertuples(index= False): # remember to check column names
        if os.path.isfile(f'{src_dir}/LEF/{metext}.lef'):
            with open(f'{src_dir}/LEF/{metext}.lef', 'r') as f1:
                lef = f1.read()
                f1.close()
            # metalRouting
            metal = re.findall(r'LAYER\s*(\w+)\s*TYPE\s*ROUTING\s*', lef)
            # viaRouting
            v = re.findall(r'LAYER\s*(\w+)\s*TYPE\s*CUT\s*', lef)
            v_ignore = ['contact', 'CO', 'CA'] # not considering these via's
            via = [item for item in v if item not in v_ignore]
            # polySilicon
            p = re.findall(r'LAYER\s*(\w+)\s*TYPE\s*MASTERSLICE\s*', lef)
            p_ignore = 'TYPE DIFFUSION' # not considering layer if contain this
            poly = [item for item in p if p_ignore not in str(re.findall(r'LAYER\s*'+ item + r'\s*TYPE\s*MASTERSLICE\s*[\s\S]*?\s*END\s*' + item, lef))]
            # diffusion
            diff = [item for item in p if p_ignore in str(re.findall(r'LAYER\s*'+ item + r'\s*TYPE\s*MASTERSLICE\s*[\s\S]*?\s*END\s*' + item, lef))]
            # contactPolySilicon
            cpoly = [item for item in v if item in v_ignore]
            # contactDiffusion
            cdiff = [item for item in v if item in v_ignore]
            # polyResistor
            res = [new_res] if new_res else re.findall(r'(siprot)\s*drawing', layer)
            # polyCutMask
            cut = ['-']
            # passivation
            pasv = ['-']
            # usedLabelDatatype
            lab = ['pintext'] if 'pintext' in layer and 'label' in layer else ['label'] if 'label' in layer else ['pin']
            # soiSubstrateOpening
            sub = ['-']
            # exposurePurpose
            expo = ['-']
            with open(f'{bin}/bin{metopt}.tcl', 'w') as f2:
                f2.write(f"metalRouting {' '.join([f'{{{i} drawing}}' for i in metal])}\n")
                f2.write(f"viaRouting {' '.join([f'{{{i} drawing}}' for i in via])}\n")
                f2.write(f"polySilicon {' '.join(poly)}\n")
                f2.write(f"diffusion {' '.join(diff)}\n")
                f2.write(f"contactPolySilicon {' '.join([f'{{{i} drawing}}' for i in cpoly])}\n")
                f2.write(f"contactDiffusion {' '.join([f'{{{i} drawing}}' for i in cdiff])}\n")
                f2.write(f"polyResistor {' '.join(res)}\n")
                f2.write(f"polyCutMask {' '.join(cut)}\n")
                f2.write(f"passivation {' '.join(pasv)}\n")
                f2.write(f"usedLabelDatatype {' '.join(lab)}\n")
                f2.write(f"soiSubstrateOpening {' '.join(sub)}\n")
                f2.write(f"exposurePurpose {' '.join(expo)}\n")
                f2.close()
        else:
            print(f'{metext}.lef does not exists')
    print('bin_.tcl files Created Successfully in "BIN_TCL" directory.\n')
    bin_gen_fldr(bin)
    
# create bin_ folders and files inside them
def bin_gen_fldr(bin_fldr):
    tcl_file = [ name for name in os.listdir(bin_fldr) if not os.path.isdir(os.path.join(bin_fldr, name)) ]
    bin_name = ['ST_IO', 'ST_Corner', 'ST_Core', 'ST_Block']
    for i in tcl_file:
        metopt = i.split('.')[0].lstrip('bin')
        os.makedirs(os.path.join(bin_fldr, f'bin{metopt}'), exist_ok=True)
        bin_met = os.path.abspath(os.path.join(bin_fldr, f'bin{metopt}'))
        for j in bin_name:
            with open(os.path.join(bin_met, f"bin.{j.lstrip('ST_')}.tcl"), 'w') as f1:
                subprocess.call(['bin_generator', j, os.path.abspath(os.path.join(bin_fldr, i)), '-o', os.path.join(bin_met, 'bin.{}.tcl'.format(j.lstrip('ST_')))]) #f"bin.{j.lstrip('ST_')}.tcl")])
                pass
            if 'ST_IO' in j or 'ST_Corner' in j:
                with open(os.path.join(bin_met, f"bin.{j.lstrip('ST_')}_detailed.tcl"), 'w') as f2:
                    subprocess.call(['bin_generator', j, os.path.abspath(os.path.join(bin_fldr, i)), '-o', os.path.join(bin_met, 'bin.{}_detailed.tcl'.format(j.lstrip('ST_')))]) #f"bin.{j.lstrip('ST_')}_detailed.tcl")])
                    pass
        print('##### Folder {} Created... #####\n'.format(i.split('.')[0]))
    print('bin generation complete...\n')
        
if __name__ == '__main__':
    src_dir = input('Enter smarttechkit root path : ')
    bin_dst = input('Enter destination path : ')
    bin_gen_tcl(src_dir, bin_dst)
