import os
import json
# from vegetation_clearing import a
from qgis.utils import iface

def remove_file(f):
    try:
        os.remove(f)
    finally:
        pass 
        

def get_contents():
    layer = iface.activeLayer()

    features = layer.getFeatures()
    s = " "

    for feat in features:
        attrs = feat.attributes()
        try:
            j = json.loads(str(attrs[5]))
        except:
            pass
            
        n = (attrs[4]) 
        
        s = "<h2>" + n + "</h2>"
               
        if type(j) == "dict":
            s = str(j)
        # elif type(n) == "list":
            
        # elif type (n) == "tuple"
                        
        # s += "<p>" + (attrs[4]) + "</p>" + "\n"
        # s += str((attrs[5])) + "\n"

        
    return s
    
def vegetation_clearing(j):
    t = ""
    for key in j.keys():
        if key == "sectionname":
            values = j.items()
            for value in values:
                print(type(value))
                t += "<h2>" + str(value[0]) + "</h2>"
                t += "<p>" + str(value[1]) + "</p>"
                print(len(value))
            # for key2 in k:
            #     t += str(k) + "<br>"  + "<br>"
        elif key == "sectiondescription":
            pass
            # t += str(j.values()) + "<br>" + "<br>"
        elif key == "forms":
            pass
            # t += str(j.values()) + "<br>" + "<br>"
            
    return t
    
def write_file(t):
    f = open("C:/Temp/demofile2.html", "w")
    f.write(t)
    f.close()
    print("here")
    
    
# remove_file("C:/Temp/demofile2.html")

t = get_contents()
write_file(t)
print("done")
