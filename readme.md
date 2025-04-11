*Project Status*

This Python project is in development and has reached a stage where I use it internally, but is not ready for release.

**Purpose**
I collect data using Smash Digital Mapper and want to review what I have collected before trusting that the GIS data is true.  If 500 points with photos have been collected, then reviewing such a dataset in a GIS is a painful process.  It is much easier to review the data as a web page, which is what this program creates.  

The second purpose of the program is to allow field data forms to be iterated.  The forms in Smash DM can be changed easily and even during a field survey.  Any changes do not effect data already collected.  This makes Smash ideal for testing new form designs, and once the form designs are finalised, they can be implemented in other GIS systems which are more widely used in industry.

**Process**
Smash uses SQLite databases to store the collected data.  Forms are designed with JSON and collected data is also in JSON, so there are no GIS tables inside.  This code takes data from the .gpap file and creates a web page to make the collected data readable.  The code will work with any JSON form data and does not need to be adjusted when form data changes.

**Road Map**
March 2025 – created working script in QGIS
April 2025 – adding tests, config file 
May 2025 – adding a user interface, where files can be dropped in