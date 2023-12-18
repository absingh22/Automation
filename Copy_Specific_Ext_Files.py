import os
import shutil

def copy_file(src_dir, dest_dir, file_ext):
    try:
        os.makedirs(dest_dir, exist_ok=True)
        for filename in os.listdir(src_dir):
            if any(filename.endswith(ext) for ext in file_ext):
                src_file = os.path.join(src_dir, filename)
                dest_file = os.path.join(dest_dir, filename)
                shutil.copy2(src_file, dest_file)
                print(f'Copied: {filename}')
            else:
                print(f'Not Copied : {filename}')
        print('Copy completed')
        
    except Exception as e:
        print('Error Occured', str(e))

if __name__ == "__main__":
    src_dir = input('Enter Srouce Directory : ')
    dest_dir = input('Enter Destination Directory : ')
    file_ext = ['.txt']#, '.csv', '.xlsx']
    copy_file(src_dir, dest_dir, file_ext)