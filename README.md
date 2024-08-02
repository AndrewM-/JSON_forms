## Converting data captured with a mobile GIS into a web page
Geopapparazzi and Smash mobile GIS have a great ability to capture data in the field.  This ability is similar to ESRI’s Survey123.  Sometimes I want to print out the data as a report, rather than view the data is a GIS.  

The code in this repo converts the json that is stored in a geopackage into a html report.  To use, I export the data from Smash as a geopackage.  I run the code in the python script window in QGIS, however it also runs from my preferred Python editors.  Just change the lines for the *input geopackage* to your geopackage and the name and location of the *output html file*, then run the code.  A web page is created, which you can open in LibreOffice or ms-Word and save as a PDF.

## Example use case 
I worked on a large wind farm construction project and would have to inspect each foundation for each turbine once per week.  With Smash, I can easily create a custom data collection form that captures all the information I need to collect.  At the time of writing, Smash’s ability to handle photos has been broken by an OS update, so the code I have created does not handle photos.  I take photos using another app and drag and drop them into a report after I have opened it in a word processor.
