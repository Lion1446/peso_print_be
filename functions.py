## FUNCTIONS
from math import log2
import os


def convert_size(size_bytes):
    """
    Converts the file size in bytes to the highest possible unit (e.g., MB, GB, etc.)
    """
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    index = int(log2(size_bytes) / 10) if size_bytes > 0 else 0
    size = size_bytes / (1024 ** index) if size_bytes > 0 else 0
    size_str = '{:.2f} {}'.format(size, units[index])
    return size_str



def get_directory_structure(folder_path):
    """
    Recursively scans the directory structure and returns a nested dictionary
    representing the file system structure, including only directories that
    contain PDF or DOCX files. Directories are placed first in the list, followed
    by PDF files, and then followed by DOCX files.
    """
    directory_structure = []
    dir_items = []
    pdf_items = []
    docx_items = []
    
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            dir_contents = get_directory_structure(item_path)
            if dir_contents:
                num_files = sum(1 for content in dir_contents if content['type'] == 'file' and (content['name'].lower().endswith('.pdf') or content['name'].lower().endswith('.docx')))
                directory_item = {
                    'type': 'directory',
                    'name': item,
                    'num_files': num_files,
                    'contents': dir_contents
                }
                dir_items.append(directory_item)
        elif item.lower().endswith('.pdf'):
            file_size = os.path.getsize(item_path)
            file_size_str = convert_size(file_size)
            directory_item = {
                'type': 'file',
                'name': item,
                'size': file_size_str
            }
            pdf_items.append(directory_item)
        elif item.lower().endswith('.docx'):
            file_size = os.path.getsize(item_path)
            file_size_str = convert_size(file_size)
            directory_item = {
                'type': 'file',
                'name': item,
                'size': file_size_str
            }
            docx_items.append(directory_item)
    
    directory_structure.extend(dir_items)
    directory_structure.extend(pdf_items)
    directory_structure.extend(docx_items)
    
    return directory_structure
