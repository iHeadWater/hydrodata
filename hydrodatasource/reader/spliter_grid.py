import os

import pandas as pd
import xarray as xr
from pandas.core.indexes.api import default_index
from hydrodatasource.processor.mask import gen_single_mask
import hydrodatasource.configs.config as conf


def query_path_from_metadata(time_start=None, time_end=None, bbox=None, data_source='gpm'):
    # query path from other columns from metadata.csv
    metadata_df = pd.read_csv('metadata.csv')
    paths = metadata_df
    if time_start is not None:
        paths = paths[paths['time_start'] >= time_start]
    if time_end is not None:
        paths = paths[paths['time_end'] <= time_end]
    if data_source == 'gpm':
        if bbox is not None:
            paths = paths[
                (paths['bbox'].apply(lambda x: string_to_list(x)[0] <= bbox[0])) &
                (paths['bbox'].apply(lambda x: string_to_list(x)[1] >= bbox[1])) &
                (paths['bbox'].apply(lambda x: string_to_list(x)[2] >= bbox[2])) &
                (paths['bbox'].apply(lambda x: string_to_list(x)[3] <= bbox[3]))]
    elif data_source == 'gfs':
        path_list_predicate = paths[paths['path'].isin(choose_gfs(paths, time_start, time_end))]
        paths = paths[path_list_predicate['bbox'].apply(lambda x: string_to_list(x)[0] <= bbox[0]) &
                      (paths['bbox'].apply(lambda x: string_to_list(x)[1] >= bbox[1])) &
                      (paths['bbox'].apply(lambda x: string_to_list(x)[2] >= bbox[2])) &
                      (paths['bbox'].apply(lambda x: string_to_list(x)[3] <= bbox[3]))]
    for path in paths['path']:
        path_ds = xr.open_dataset(conf.FS.open(path))
        if data_source == 'gpm':
            tile_ds = path_ds.sel(time=slice(time_start, time_end), lon=slice(bbox[0], bbox[1]),
                                  lat=slice(bbox[3], bbox[2]))
        # 会扰乱桶，注意
        elif data_source == 'gfs':
            tile_ds = path_ds.sel(time=slice(time_start, time_end), longitude=slice(bbox[0], bbox[1]),
                                  latitude=slice(bbox[2], bbox[3]))
        else:
            tile_ds = path_ds
        tile_path = path.rstrip('.nc4') + '_tile.nc4'
        temp_df = pd.DataFrame(
            {'bbox': str(bbox), 'time_start': time_start, 'time_end': time_end, 'res_lon': 0.25, 'res_lat': 0.25,
             'path': tile_path}, index=default_index(1))
        metadata_df = pd.concat([metadata_df, temp_df], axis=0)
        if data_source == 'gpm':
            conf.FS.write_bytes(tile_path, tile_ds.to_netcdf())
        elif data_source == 'gfs':
            tile_ds.to_netcdf('temp.nc4')
            conf.FS.put_file('temp.nc4', tile_path)
            os.remove('temp.nc4')
    metadata_df.to_csv('metadata.csv', index=False)
    return paths


def choose_gfs(paths, start_time, end_time):
    """
        This function chooses GFS data within a specified time range and bounding box.
        Args:
            start_time (datetime, YY-mm-dd): The start time of the desired data.
            end_time (datetime, YY-mm-dd): The end time of the desired data.
            bbox (list): A list of four coordinates representing the bounding box.
        Returns:
            list: A list of GFS data within the specified time range and bounding box.
        """
    path_list = []
    produce_times = ['00', '06', '12', '18']
    if start_time is None:
        start_time = paths['time_start'].iloc[0]
    if end_time is None:
        end_time = paths['time_end'].iloc[-1]
    time_range = pd.date_range(start_time, end_time, freq='1D')
    for date in time_range:
        date_str = date.strftime('%Y/%m/%d')
        for i in range(len(produce_times)):
            for j in range(6 * i, 6 * (i + 1)):
                path = 's3://grids-origin/GFS/GEE/30m/' + date_str + '/' + produce_times[i] + '/gfs20220103.t' + \
                       produce_times[i] + 'z.nc4.0p25.f' + '{:03d}'.format(j)
                path_list.append(path)
    return path_list


def string_to_list(x: str):
    return list(map(float, x[1:-1].split(',')))


def generate_bbox_from_shp(basin_shape_path):
    basin_id = basin_shape_path.split('/')[-1].split('.')[0]
    mask = gen_single_mask(basin_id=basin_id, shp_path=basin_shape_path, dataname='gfs', mask_path='temp_mask', minio=True)
    bbox = [mask['lon'].values.min(), mask['lon'].values.max(), mask['lat'].values.max(), mask['lat'].values.min()]
    return mask, bbox