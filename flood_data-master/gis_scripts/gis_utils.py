import shapefile
import pandas as pd

gis_proj_dir = "C:/Users/Jeff/Google Drive/research/Sadler_3rdPaper_GIS_data/"
gis_main_dir = "C:/Users/Jeff/Google Drive/research/Hampton Roads Data/Geographic Data/"
elev_raster = '{}Raster/USGS Nor DEM/mosaic/nor_mosaic.tif'.format(gis_main_dir)

def read_shapefile_attribute_table(sf_name):
    sf = shapefile.Reader(sf_name)
    records = sf.records()
    df = pd.DataFrame(records)
    sf_field_names = [i[0] for i in sf.fields]
    df.columns = sf_field_names[1:]
    df.reset_index(inplace=True)
    return df

# '/c/Users/Jeff/Google Drive/research/Sadler_3rdPaper_GIS_data/flood_events.shp'
