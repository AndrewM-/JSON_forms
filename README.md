## Converting data captured with a mobile GIS into a web page
Geopapparazzi and Smash mobile GIS have a great ability to capture data in the field.  This ability is similar to ESRI’s Survey123.  Sometimes I want to print out the data as a report, rather than view the data is a GIS.  

The code in this repo converts the json that is stored in a geopackage into a html report.  To use, I export the data from Smash as a geopackage.  I run the code in the python script window in QGIS, however it also runs from my preferred Python editors.  Just change the lines for the *input geopackage* to your geopackage and the name and location of the *output html file*, then run the code.  A web page is created, which you can open in LibreOffice or ms-Word and save as a PDF.

## Example use case 
I worked on a large wind farm construction project and would have to inspect each foundation for each turbine once per week.  With Smash, I can easily create a custom data collection form that captures all the information I need to collect. 

New forms are created using JSON in a text editor or by using the integrated forms editor.  I have created a ms-access based form designer with a GUI, but ms-access is not GIT friendly, so I have not uploaded it.

## Limitations
 I need to open the exported geopackage in QGIS to add and fill fields for Latitude and Longitude.  Smash exports point geometry objects which contain Latitude and Longitude but which I cannot unpack yet, without adding in a library dependency.  This limitation does not apply to ExportInspection_gpap.py which reads the native data format of Smash.  There is an assumption that you have exported the images from the gpap file, into an image folder that needs to be updated in the code.  Smash stores the photo data inside the SQLite database as blobs, which need to be extracted first before a web page can be created.
