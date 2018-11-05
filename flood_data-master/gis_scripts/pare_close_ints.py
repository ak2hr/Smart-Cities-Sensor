# coding: utf-8
# this script is to thin intersection points so that they are at least a certain distance apart
from main import gis_data_dir 
from gis_utils import read_shapefile_attribute_table 
import matplotlib.pyplot as plt
import pandas as pd

first_time = True
num = 0
threshold = 100  # map units. in this case feet
city = 'nor' 
# city = 'vab' 
while True:
    num += 1
    print num
    out_file = '{}_intersections_filt{}.shp'
    out_file_name = out_file.format(city, num)
    if first_time:
        if city == 'nor':
            intersection_shapefile_name = 'nor_intersections_diss_jn.shp'
            mil_filt = "VDOT = 9"
            where_clause = """ "FID" IN ({}) AND NOT {} """.format(",".join(map(str, unique_idx)), mil_filt)
        elif city == 'vab':
            intersection_shapefile_name = 'vab_intersections_jn.shp'
            where_clause = """ "FID" IN ({})""".format(",".join(map(str, unique_idx)))
            elev_raster = Raster('C:/Users/Jeff/Google Drive/research/Hampton Roads Data/Geographic Data/'
                                 'Raster/USGS VABeach DEM/mosaic/usgs_mosaic_float.tif')
            raster_list = [[elev_raster, 'elev']] 
            ExtractMultiValuesToPoints(intersection_shapefile_name, raster_list, "NONE")
        first_time = False
    else:
        intersection_shapefile_name = out_file.format(city, num-1)
    inter_shp_pth = "{}{}".format(gis_data_dir, intersection_shapefile_name)
    df = read_shapefile_attribute_table(inter_shp_pth)
    df.set_index('index', inplace=True)
    df['NEAR_DIST'] = pd.to_numeric(df['NEAR_DIST'])
    big_indicies = list(df[df.NEAR_DIST>threshold].index)
    df = df[df.NEAR_DIST<threshold]
    if df.empty:
        break
    unique_idx = list(df[~df.NEAR_DIST.duplicated()].index)
    unique_idx.extend(big_indicies)
    print "Select_analysis"
    arcpy.Select_analysis(intersection_shapefile_name, out_file_name, where_clause)
    arcpy.Near_analysis(out_file_name, out_file_name)
for i in range(num-2):
    i += 1
    arcpy.Delete_management(out_file.format(city, i))
