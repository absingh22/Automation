#!/sw/freetools/python/3.9.12/rh70_64/bin/python
import re
import os
import sys
import subprocess
import shutil
from datetime import date

###################################### dkSetup Convertor ######################################
# copy files from .dkSetup and convert
def copy_file(src_dir, dest_dir, file_ext, bin_dst, techno, ver):
    with open(file_ext, 'r') as file:
        filenames = file.read().splitlines()
    
    for filename in filenames:
        src_file = os.path.join(src_dir, f'.dkSetup_{filename}')
        
        if os.path.exists(src_file) == True:
            dir_name = [ name for name in os.listdir(src_file) if os.path.isdir(os.path.join(src_file, name)) ]
            dk_ref = [ i for i in dir_name if i.startswith('DK_REFLIB_') ]
            
            # Copy and modify cds.lib
            shutil.copy2(os.path.join(src_file, 'cds.lib'), os.path.join(dest_dir,f'technocds{filename}.lib'))
            modify_cds(os.path.join(dest_dir,f'technocds{filename}.lib'), filename)
            
            # Copy and modify cds.lib_MACROCELLS_ESD_BCD8sP
            shutil.copy2(os.path.join(src_file, 'cds.lib_MACROCELLS_ESD_BCD8sP'), os.path.join(dest_dir, f'cds.lib_MACROCELLS_ESD_BCD8sP_{filename}'))
            modify_cds_m(os.path.join(dest_dir, f'cds.lib_MACROCELLS_ESD_BCD8sP_{filename}'))
            
            # Copy and modify ITDB_bcd8sp
            shutil.copytree(os.path.join(src_file, dk_ref[0]), os.path.join(dest_dir, f'itdb{filename}', 'ITDB_bcd8sp'), dirs_exist_ok=True)
            for i in os.listdir(os.path.join(dest_dir, f'itdb{filename}', 'ITDB_bcd8sp')):
                if (i.endswith('.il')):
                    subprocess.call(['update_libinit_il.pl', os.path.join(os.path.join(dest_dir, f'itdb{filename}', 'ITDB_bcd8sp'), i)])
                elif (i.endswith('.db')):
                    pass
                else:
                    os.remove(os.path.join(os.path.join(dest_dir, f'itdb{filename}', 'ITDB_bcd8sp'), i))
            os.remove(os.path.join(os.path.join(dest_dir, f'itdb{filename}', 'ITDB_bcd8sp'), 'bck_libInit.il'))
            print(f'Converting Metal Option: {filename}')
        else:
            print(f'Metal Option {filename} Not Found')
    print('dkSetup file conversion complete...')
    
    # Copy folders from bin_dst to dest_dir
    for item in os.listdir(bin_dst):
        bin_item = os.path.join(bin_dst, item)
        if os.path.isdir(bin_item):
            dest_item = os.path.join(dest_dir, item)
            shutil.copytree(bin_item, dest_item, dirs_exist_ok=True)
    
    # Copy and update common files 
    cad_file = '/work/LIPAT/USER_AREAS/ABHISHEK/BCD_GNTR/resource/cadence_files'
    for i in os.listdir(cad_file):
        if 'TECHNO' in i :
            with open(os.path.join(cad_file, i), 'r') as f:
                data = f.read()
                data = data.replace('<TECHNO>', techno.lower()).replace('<VERSION>', ver).replace('<DATE>', date.today().strftime("%d-%b-%Y"))
            j = i.replace('TECHNO', techno.lower())
            with open(os.path.join(dest_dir,j), 'w') as k:
                k.write(data)
        else:
            with open(os.path.join(cad_file, i, 'TECHNO.lef'), 'r') as f:
                lef = f.read()
            os.makedirs(os.path.join(dest_dir, i), exist_ok=True)
            with open(os.path.join(dest_dir, i, f'{techno.lower()}.lef'), 'w') as k:
                k.write(lef)
    
    print('\nlibderiv_cadence creation complete...\n')

# make changes in cds.lib files
def modify_cds(d_cds, filename):
    try:    
        r_cds = open(d_cds, 'r')
        mod_cds = r_cds.read()
        r_cds.close()
        mod_cds = mod_cds.split('\n')
        data_cds = re.sub(r'SOFTINCLUDE\s*.*?\s*_BCD8sP', f'SOFTINCLUDE ./cds.lib_MACROCELLS_ESD_BCD8sP_{filename}', str(mod_cds))
        data_cds = re.sub(r'(ASSIGN|DEFINE)\s*DK_REFLIB_(.*?)\,', '', data_cds)
        data_cds = data_cds.replace("['", "'").replace("', ' ' ", "', ").replace("']", "'").replace("'", "")
        r_cds = open(d_cds, 'w')
        
        for item in data_cds.split(", "):
	        r_cds.write(item+"\n")
        r_cds.close()
        return None
    except Exception as e:
        sys.exit(1)

def modify_cds_m(d_cds_m):
    try:
        r_cds_m = open(d_cds_m, 'r')
        mod_cds_m = r_cds_m.read()
        r_cds_m.close()
        mod_cds_m = mod_cds_m.split('\n')
        data_cds_m = re.sub(r'([ASSIGN|DEFINE]+\s*MACROCELLS_\s*.*?[\,|\]])', '', str(mod_cds_m))
        data_cds_m = data_cds_m.replace(", ' '", "").replace("'", "").replace("[", "")
        r_cds_m = open(d_cds_m, 'w')
        
        for item in data_cds_m.split(", "):
	        r_cds_m.write(item+"\n")
        r_cds_m.close()
        return None
    except Exception as e:
        sys.exit(1)

if __name__ == '__main__':
    src_dir = input('Enter opus directory path : ')
    dest_dir = input('Enter destination path : ')
    file_ext = input('Enter metal options path : ')
    bin_dst = input('Enter cadence bin path : ')
    techno = input('Enter techno name : ')
    ver = input('Enter version name : ')
    copy_file(src_dir, dest_dir, file_ext, bin_dst, techno, ver)
