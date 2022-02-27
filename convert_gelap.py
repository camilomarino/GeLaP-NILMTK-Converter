import tarfile
import warnings
from os.path import join

import numpy as np
import pandas as pd
from nilm_metadata import save_yaml_to_datastore
from nilmtk.datastore import Key
from nilmtk.measurement import LEVEL_NAMES
from nilmtk.utils import get_datastore

warnings.simplefilter(action="ignore", category=FutureWarning)


def convert_gelap(
    gelap_path: str, output_filename: str, uncompress_tars: bool = True
) -> None:
    """
    Parameters
    ----------
    gelap_path : str
        The root path of the GeLaP.
    output_filename : str
        The destination filename (including path and suffix).
    """

    store = get_datastore(output_filename, "HDF", mode="w")

    # Convert raw data to DataStore
    _convert(gelap_path, store, uncompress=uncompress_tars)

    metadata_path = "metadata"

    # Add metadata
    save_yaml_to_datastore(metadata_path, store)
    store.close()

    print("Done converting GeLaP to HDF5!")


def _uncompress_tar(tar_path: str, output_path: str) -> None:
    tar = tarfile.open(tar_path)
    tar.extractall(output_path)
    tar.close()


def _uncompress_houses_tar(gelap_path: str) -> None:
    houses_tar_path = {
        house_number: join(gelap_path, f"hh-{house_number:02}.tar.xz")
        for house_number in range(1, 21)
    }
    for house_number, house_tar_path in houses_tar_path.items():
        print(f"Uncompressing {house_tar_path} ...")
        _uncompress_tar(house_tar_path, join(gelap_path, f"hh-{house_number:02}"))


def _prepare_df(
    df: pd.DataFrame, sort_index: bool, drop_duplicates: bool
) -> pd.DataFrame:
    df = df.astype(np.float32)
    df = df.tz_localize("GMT").tz_convert("Europe/Berlin")
    columns = pd.MultiIndex.from_tuples(
        [
            ("power", "active"),
        ]
    )
    df.columns = columns
    df.columns.set_names(LEVEL_NAMES, inplace=True)
    df.dropna(inplace=True)

    if sort_index:
        df.sort_index(inplace=True)
    return df


def _read_site_meter_csv(
    csv_path: str, sort_index: bool, drop_duplicates: bool
) -> pd.DataFrame:
    df = pd.read_csv(csv_path, index_col=0)
    df.index = pd.to_datetime(df.index, unit="ms")

    # sum 3 phases of power
    # TODO:  Load each phase separately and include it in the metadata
    df = pd.DataFrame(df.sum(axis=1))

    df = _prepare_df(df, sort_index, drop_duplicates)
    return df


def _read_elec_csv(
    csv_path: str, sort_index: bool, drop_duplicates: bool
) -> pd.DataFrame:
    df = pd.read_csv(csv_path, usecols=[1, 2], index_col=0)
    df.index = pd.to_datetime(df.index, unit="ms")
    df = _prepare_df(df, sort_index, drop_duplicates)

    return df


def _convert_house(
    house_path: str, house_number: int, store, sort_index: bool, drop_duplicates: bool
):
    # calculate csvs paths
    site_meter_csv = join(house_path, "smartmeter.csv")
    elecs_csv_path = {
        elec_number: join(house_path, f"label_{elec_number:03}.csv")
        for elec_number in range(1, 11)
    }

    # reading csv
    print(f"Reading site_meter from: {site_meter_csv} ...")
    df_site_meter = _read_site_meter_csv(site_meter_csv, sort_index, drop_duplicates)
    site_meter_number = 11
    key = Key(building=house_number, meter=site_meter_number)
    store.put(str(key), df_site_meter)

    for elec_number, elec_csv_path in elecs_csv_path.items():
        print(f"Reading elec {elec_number} from: {elec_csv_path} ...")
        df_elec = _read_elec_csv(elec_csv_path, sort_index, drop_duplicates)
        key = Key(building=house_number, meter=elec_number)
        store.put(str(key), df_elec)


def _convert(
    gelap_path: str,
    store,
    sort_index: bool = True,
    drop_duplicates: bool = False,
    uncompress: bool = True,
) -> None:
    if uncompress:
        _uncompress_houses_tar(gelap_path)
    num_houses = 4
    for house_number in range(1, num_houses + 1):
        print(f"Converting house {house_number}...")
        house_path = join(gelap_path, f"hh-{house_number:02}")
        _convert_house(house_path, house_number, store, sort_index, drop_duplicates)
