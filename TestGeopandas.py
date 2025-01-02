# ACM
#  to test if geopandas can find coordinates in a geopackage file from smash

import geopandas as gpd

dbfile = "E:/Wedgetail/Eugowra/FieldObs/Plots_week1/smash_export_20241007_212444.gpkg"
gdf = gpd.read_file(dbfile)

# For each point geometry, you can get coordinates like this:
for index, row in gdf.iterrows():
    point = row.geometry
    longitude = point.x  # or point.coords.xy[0][0]
    latitude = point.y   # or point.coords.xy[1][0]
    print(f"Longitude: {longitude}, Latitude: {latitude}")