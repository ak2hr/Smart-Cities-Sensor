import os
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
import arcpy
from gis_utils import read_shapefile_attribute_table, gis_proj_dir, gis_main_dir, elev_raster 
import numpy as np
from arcgisscripting import ExecuteError
import json
import pandas as pd
import sqlite3
from hr_db_scripts.main_db_script import get_db_table_as_df 
from db_scripts.main_db_script import db_filename
from arcpy import env
from arcpy.sa import Raster, Ln, Tan, RemapValue, Reclassify, PathDistance, PathAllocation, \
    ExtractMultiValuesToPoints, FocalStatistics, NbrRectangle
import math

arcpy.CheckOutExtension("spatial")
env.overwriteOutput = True
env.workspace = gis_proj_dir


def calculate_twi():
    slope_raster = Raster("slope_nor.tif")
    flacc = Raster("{}Raster/USGS Nor DEM/mosaic/nor_flacc".format(gis_main_dir))
    twi = Ln((flacc+1.)/(Tan((slope_raster+.0001)*math.pi/180.)))
    out_file_name = 'twi.tif'
    twi.save(out_file_name)


def reclassify_lulc(reclass_numbers, out_file_name):
    lulc_rast = Raster('nor_lulc_ext_prj.tif')
    remap_list = [[str(i), 1] for i in reclass_numbers]
    remap = RemapValue(remap_list)
    reclass_field = "VALUE"
    water_rast = Reclassify(lulc_rast, reclass_field, remap, "NODATA")
    water_rast.save(out_file_name)


def reclassify_lulc_for_water():
    out_file_name = 'nor_ow_wl.tif'
    reclassify_lulc([11, 91], out_file_name)
    return out_file_name


def reclassify_lulc_for_imperv():
    out_file_name = 'nor_imperv.tif'
    reclassify_lulc([21, 22, 31], out_file_name)
    return out_file_name


def imperviousness_raster():
    out_file_name = 'neigh_imp.tif'
    imp_rast = Raster('nor_imperv.tif')
    neighborhood = NbrRectangle(width=1500, height=1500, units="MAP")
    neigh_imp = FocalStatistics(imp_rast, neighborhood=neighborhood, statistics_type="SUM",
                                ignore_nodata="DATA")
    neigh_imp.save(out_file_name)
    return out_file_name


def path_allocation_basins():
    src_raster = '{}/Stormwater Infrastructure/sw_struct_basins.shp'.format(gis_proj_dir)
    elev_raster = Raster(elev_raster)
    out_file_name = 'path_allo_basins.tif'
    pth_all = PathAllocation(src_raster, source_field="FID", in_surface_raster=elev_raster,
                             in_vertical_raster=elev_raster)
    pth_all.save(out_file_name)
    return out_file_name


def path_dist_water():
    src_raster = "nor_ow_wl.tif"
    out_file_name = "pth_dist_to_wat.tif"
    calculate_dist_to_src(src_raster, out_file_name)


def path_dist_basins():
    src_raster = '{}/Stormwater Infrastructure/sw_struct_basins.shp'.format(gis_proj_dir)
    out_file_name = 'path_dist_basins.tif'
    calculate_dist_to_src(src_raster, out_file_name)


def calculate_dist_to_src(src_raster, out_file_name):
    """
    uses water raster as source should have run reclassify_lulc_for_water first
    :return: 
    """
    elev_raster = Raster(elev_raster)
    path_dist = PathDistance(in_source_data=src_raster, in_surface_raster=elev_raster,
                             in_vertical_raster=elev_raster)
    path_dist.save(out_file_name)


def merge_flood_non_flood():
    flood_pts = 'fld_pts_rd_data.shp'
    non_flood_pts = 'sampled_road_pts.shp'
    out_file_name = 'fld_nfld_pts.shp'
    print "Merge_management"
    arcpy.Merge_management([flood_pts, non_flood_pts], out_file_name)


def join_flooded_pts_with_rd_attributes(flood_pts='flooded_points.shp', road_lines='nor_roads_centerlines.shp', 
        out_file_name = 'fld_pts_rd_data.shp'):
    print "SpatialJoin_analysis"
    arcpy.SpatialJoin_analysis(flood_pts, road_lines, out_file_name, match_option='CLOSEST')


def join_sw_structures_with_pipe_data():
    data_dir = '{}Stormwater Infrastructure/'.format(gis_proj_dir)
    sw_str = '{}Norfolk_SW_Structures.shp'.format(data_dir)
    sw_pipe = '{}Norfolk_SW_Pipes.shp'.format(data_dir)
    out_file_name = '{}sw_structures_joined_pipes.shp'.format(data_dir)
    print "SpatialJoin_analysis"
    arcpy.SpatialJoin_analysis(sw_str, sw_pipe, out_file_name, match_option='CLOSEST')
    return out_file_name


def sample_road_points():
    fld_pts = '{}fld_pts_rd_data.shp'.format(gis_proj_dir)
    rd_pts = '{}rd_far_fld.shp'.format(gis_proj_dir)
    fld_pt_df = read_shapefile_attribute_table(fld_pts)
    rd_pts_df = read_shapefile_attribute_table(rd_pts)
    cls = fld_pt_df.groupby('VDOT')['count'].sum().sort_values(ascending=False)
    cls = cls / cls.sum() * 100
    cls = get_rd_classes(rd_pts)
    num_samples = (cls * 750 / 100).round()

    l = []
    for c, n in num_samples.iteritems():
        d = rd_pts_df[rd_pts_df['VDOT'] == c]
        if d.shape[0] > n:
            idx = d.sample(n=int(n)).index
        else:
            print "there are too few points. only {} when it's asking for {} for VDOT {}".format(
                d.shape[0],
                n,
                c
            )
            idx = d.index
        l.append(pd.Series(idx))
    sampled = pd.concat(l)
    out_file_name = 'sampled_road_pts.shp'
    where_clause = '"FID" IN ({})'.format(",".join(map(str, sampled.tolist())))
    print "Select_analysis"
    arcpy.Select_analysis(rd_pts, out_file_name, where_clause)
    return sampled


def make_basin_shapefile():
    sw_strct = '{}/Stormwater Infrastructure/sw_structures_joined_pipes.shp'.format(gis_proj_dir)
    basin_codes = filter_sw_struc_codes('basin')
    where_clause = '"Structure1" IN (\'{}\')'.format("','".join(map(str, basin_codes)))
    out_file_name = '{}/Stormwater Infrastructure/sw_struct_basins.shp'.format(gis_proj_dir)
    print "Select_analysis"
    arcpy.Select_analysis(sw_strct, out_file_name, where_clause)
    return out_file_name


def filter_sw_struc_codes(term='basin'):
    metadata_file_name = '{}/Stormwater Infrastructure/nor_sw_structures_metadata.txt'.format(
        gis_proj_dir)
    with open(metadata_file_name) as sw_data:
        d = json.load(sw_data)
    structure_types = d['fields'][3]['domain']['codedValues']
    basin_codes = []
    for s in structure_types:
        if term in s['name'].lower():
            basin_codes.append(s['code'])
    return basin_codes


def extract_values_to_points():
    target_shapefile = 'fld_nfld_pts.shp'
    elev_raster = Raster(elev_raster)
    raster_list = [['twi.tif', 'twi'],
                   [elev_raster, 'elev'],
                   ['path_dist_basins.tif', 'dist_to_basin'],
                   ['path_allo_basins.tif', 'basin_id'],
                   ['neigh_imp.tif', 'imp'],
                   ['pth_dist_to_wat.tif', 'dist_to_wat']]
    ExtractMultiValuesToPoints(target_shapefile, raster_list, "NONE")


def is_in_plygn(ply_shp, pts_shp, field_name):
    pts_lyr = 'pts_lyr'
    arcpy.MakeFeatureLayer_management(pts_shp, pts_lyr)
    try:
        arcpy.AddField_management(pts_lyr, field_name, "SHORT")
    except ExecuteError:
        arcpy.DeleteField_management(pts_lyr, field_name)
        arcpy.AddField_management(pts_lyr, field_name, "SHORT")
    arcpy.SelectLayerByLocation_management(pts_lyr, overlap_type='WITHIN',
                                           select_features=ply_shp)
    arcpy.CalculateField_management(pts_lyr, field_name, "1")


def add_is_downtown_field():
    fld_pts_shp = 'fld_nfld_pts.shp'
    dntn_ply = 'subset_polygon.shp'
    dntn_field = 'is_dntn'
    is_in_plygn(dntn_ply, fld_pts_shp, dntn_field)


def add_is_in_hague():
    fld_pts_shp = 'fld_nfld_pts.shp'
    hg_ply = 'ply_near_hague.shp'
    field = 'in_hague'
    is_in_plygn(hg_ply, fld_pts_shp, field)


def add_flood_pt_field():
    fld_pts_shp = 'fld_nfld_pts.shp'
    fld_pts_lyr = 'fld_pts_lyr'
    arcpy.MakeFeatureLayer_management(fld_pts_shp, fld_pts_lyr)
    field = 'flood_pt'
    try:
        arcpy.AddField_management(fld_pts_lyr, field, "SHORT")
    except ExecuteError:
        arcpy.DeleteField_management(fld_pts_lyr, field)
        arcpy.AddField_management(fld_pts_lyr, field, "SHORT")
    expresssion = '!count!>0'
    arcpy.CalculateField_management(fld_pts_lyr, field, expression=expresssion,
                                    expression_type='PYTHON')


def join_fld_pts_with_basin_attr():
    fld_pts_shp = 'fld_nfld_pts.shp'
    sw_table = '{}/Stormwater Infrastructure/sw_struct_basins.shp'.format(gis_proj_dir)
    arcpy.JoinField_management(fld_pts_shp, in_field='basin_id', join_table=sw_table,
                               join_field='FID')


def update_db():
    fld_loc = read_shapefile_attribute_table('{}fld_nfld_pts.shp'.format(gis_proj_dir))
    needed_attrs = ['location',
                    'xcoord',
                    'ycoord',
                    'count',
                    'twi',
                    'elev_1',
                    'dist_to_ba',
                    'imp',
                    'dist_to_wa',
                    'is_dntn',
                    'in_hague',
                    'Structure1',
                    'Rim_Elevat',
                    'Invert_Ele',
                    'Year_Insta',
                    'Pipe_Geome',
                    'Horizontal',
                    'Vertical_D',
                    'Pipe_Lengt',
                    'Pipe_Mater',
                    'Year_Ins_1',
                    'Condition',
                    'flood_pt'
                    ]
    filt = fld_loc[needed_attrs]
    filt_num = filt.apply(pd.to_numeric, errors='ignore')
    filt_num.ix[:, filt_num.columns != 'location'] = filt_num.ix[
                                                     :,
                                                     filt_num.columns != 'location'].replace(
        r'\s+', np.nan, regex=True)
    # filt_num = filt_num.replace(r'\s+', np.nan, regex=True)
    con = sqlite3.connect(db_filename)
    filt_num.to_sql(con=con, name='flood_locations', if_exists='replace')


def make_rand_road_pts():
    """
    makes the 'rd_far_fld.shp' file which is points on roads that are spaced at least 300 ft from
    each other and at least 200 ft from any flood points
    :return: 
    """
    road_shapefile = "nor_roads_centerlines.shp"
    arcpy.Densify_edit(road_shapefile, densification_method='DISTANCE', distance=30)
    road_pts_file = 'rd_pts_all_1.shp'
    arcpy.FeatureVerticesToPoints_management(road_shapefile, road_pts_file)
    rand_rd_pts_file = 'rand_road.shp'
    rand_rd_pts_lyr = 'rand_road_lyr'
    arcpy.CreateRandomPoints_management(gis_proj_dir, rand_rd_pts_file, road_pts_file,
                                        number_of_points_or_field=50000,
                                        minimum_allowed_distance=200)
    fld_pts_file = 'flooded_points.shp'
    fld_pts_buf = 'fld_pt_buf.shp'
    arcpy.Buffer_analysis(fld_pts_file, fld_pts_buf, buffer_distance_or_field=200,
                          dissolve_option='ALL')
    arcpy.MakeFeatureLayer_management(rand_rd_pts_file, rand_rd_pts_lyr)
    arcpy.SelectLayerByLocation_management(rand_rd_pts_lyr, overlap_type='WITHIN',
                                           select_features=fld_pts_buf,
                                           invert_spatial_relationship='INVERT')
    rd_pts_outside_buf = 'rd_far_fld.shp'
    arcpy.CopyFeatures_management(rand_rd_pts_lyr, rd_pts_outside_buf)
    arcpy.JoinField_management(rd_pts_outside_buf, in_field='CID', join_table=road_pts_file,
                               join_field='FID')


def main():
    # merge_flood_non_flood()
    # add_flood_pt_field()
    # add_is_downtown_field()
    # extract_values_to_points()
    # join_fld_pts_with_basin_attr()
    # add_is_in_hague()
    # update_db()


if __name__ == "__main__":
    main()
