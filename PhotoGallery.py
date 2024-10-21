import os
from os import listdir

# from vegetation_clearing import a
# from qgis.utils import iface

def remove_file(f):
    try:
        os.remove(f)
    except:
        pass 
        
def write_file(t):
    f = open("C:/Temp/demofile7.html", "w")
    f.write(t)
    f.close()
    
def get_filepaths(directory):
    file_paths = ""

    for root, directories, files in os.walk(directory):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths += "<img height='300' src='" + filepath + "'>  </img>"

    return file_paths  # Self-explanatory.

folder = "C:/Vestas/iPhone/202407__"    
file_list = get_filepaths(folder)
remove_file("C:/Temp/demofile7.html")
web_text = file_list
write_file(web_text)
print("done")
