import time

import ujson
import xarray as xr
from distributed import LocalCluster
from kerchunk.hdf import SingleHdf5ToZarr


def test_read_blob():
    start_time = time.time()
    cluster = LocalCluster(dashboard_address=":10086")  # Fully-featured local Dask cluster
    client = cluster.get_client()
    # ds = xr.open_dataset('/home/forestbat/usgs-streamflow-nldas_hourly.nc')
    ds = xr.open_dataset('/home/forestbat/gpm_gfs.nc')
    # new_zarr = ds.to_zarr('usgs-streamflow-nldas_hourly.zarr', mode='w')
    print(time.time() - start_time)
    zarr_start_time = time.time()
    zds = xr.open_zarr(store='/home/forestbat/IdeaProjects/hydrodata/tests/gpm_gfs.zarr')
    print(time.time() - zarr_start_time)
    cluster = LocalCluster(dashboard_address=":10086")  # Fully-featured local Dask cluster
    client = cluster.get_client()
    dask_zarr_start_time = time.time()
    dzds = xr.open_zarr(store='/home/forestbat/IdeaProjects/hydrodata/tests/gpm_gfs.zarr')
    print(time.time() - dask_zarr_start_time)
    nc_to_zarr_time = time.time()
    nc_chunks = SingleHdf5ToZarr('/home/forestbat/gpm_gfs.nc')
    with open('gpm_gfs_nc.json', 'wb') as fp:
        fp.write(ujson.dumps(nc_chunks.translate()).encode())
    print(time.time() - nc_to_zarr_time)
    virtual_zarr_start_time = time.time()
    vds = xr.open_dataset("reference://", engine="zarr", backend_kwargs={
        "consolidated": False,
    })
    print(time.time() - virtual_zarr_start_time)
