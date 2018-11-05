import geopandas as gpd
import pandas as pd
from gis_utils import gis_main_dir


def main():
    dfd = pd.read_csv('{}census/aff_download1/ACS_15_5YR_B19013_with_ann.csv'.format(gis_main_dir))
    dfs = gpd.read_file('{}census/va_block_groups/tl_2015_51_bg.shp'.format(gis_main_dir))

    dfd = dfd[dfd['marg_err'].str.contains('\d')]
    dfd = dfd.convert_objects(convert_numeric=True)
    dfs = dfs.convert_objects(convert_numeric=True)

    dfj = dfs.merge(dfd, left_on='GEOID', right_on='GEO_idd')
    dfj.to_file('{}LocalityData/Norfolk/nor_med_income'.format(gis_main_dir))


if __name__ == "__main__":
    main()
