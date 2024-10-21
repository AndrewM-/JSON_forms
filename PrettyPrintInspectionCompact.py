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
                   
        s += json.dumps(j, indent=4)
        return s
    
def section_name_level(j):
    t = ""
    for key in j.keys():
        if key == "sectionname":
            form_text = ""
            values = j.items()
            for value in values:
                print(str(key))
                if str(value[0]) == "forms":
                    print("top")
                    form_text = form_name_level(value[1])
                    t += "<p>" + form_text + "</p>"
                else:
                    print("bottom")
                    t += str(key)
                    t += "<h2>" + str(value[0]) + "</h2>"
                    t += "<h2>" + str(value[1]) + "</h2>"

    return t
    
def form_name_level(i):
    form_level_text = ""
    
    for form_control in i:
        form_level_text += str(form_control) + " "
    form_level_text = "<p>" + form_level_text + "</p>"
    return form_level_text
    
    
def write_file(t):
    f = open("C:/Temp/demofile3.html", "w")
    f.write(t)
    f.close()
   
t = get_contents()
write_file(t)
print("done")
