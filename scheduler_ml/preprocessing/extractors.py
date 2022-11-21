import logging
import typing as tp

import numpy as np
import pandas as pd
from dateutil import parser
from scheduler_ml.preprocessing import readers, transformers, writers


class HistDataExtractor:
    def __init__(
            self, 
            reader_params: tp.Dict[str, tp.Any], 
            writer_params: tp.Dict[str, tp.Any],
            transformer_params: tp.Dict[str, tp.Any], 
            dt_from: str, 
            dt_to: str, 
            filename_fmt: str,
            filename_to_save: str):
        self.dt_from = dt_from
        self.dt_to = dt_to
        self.filename_fmt = filename_fmt
        self.filename_to_save = filename_to_save
        self.separated_file_for_each_shop = False

        self.transformer_params = transformer_params
        self.reader_params = reader_params
        self.writer_params = writer_params

        if "columns" in self.transformer_params.keys():
            self.reader_params['csv_params']["index_col"] = False
            self.reader_params["csv_params"]["names"] = self.transformer_params["columns"]

        self.reader = readers.Minio2PandasCSVReader(**self.reader_params)
        self.writer = writers.Array2MinioWriter(**self.writer_params)
        self.transformer = transformers.HistDataTransformer(**self.transformer_params)

        self._init_cached_data()


    def _init_cached_data(self) -> None:
        self.cached_data = {}

    def get_filename(self, dt, shop_code=None):
        kwargs = dict(
            data_type=self.transformer_params["data_type"],
            year=dt.year,
            month=dt.month,
            day=dt.day,
        )
        if self.separated_file_for_each_shop:
            kwargs['shop_code'] = shop_code
        return self.filename_fmt.format(**kwargs)

    def get_dates_range(self):
        print(f"dt_from: {self.dt_from}")
        dt_from = parser.parse(self.dt_from)
        dt_to = parser.parse(self.dt_to)
        return list(pd.date_range(dt_from, dt_to).date)

    def get_dt_and_filename_pairs(self):
        dt_and_filename_pairs = []
        for dt in self.get_dates_range():
            if self.separated_file_for_each_shop:
                for shop_code in self.cached_data.get('generic_shop_ids').keys():
                    dt_and_filename_pairs.append(
                        (dt, self.get_filename(dt, shop_code=shop_code)))
            else:
                dt_and_filename_pairs.append((dt, self.get_filename(dt)))
        return dt_and_filename_pairs


    def extract(self):
        errors = set()
        dt_and_filename_pairs = self.get_dt_and_filename_pairs()
        for dtt, filename in dt_and_filename_pairs:
            logging.error(f"{filename}, {dtt}")
            reader_generator = self.reader.read(filename)
            objects, load_errors = self.transformer.transform(
                reader_generator, dtt, filename)
            if load_errors:
                errors = errors.union(load_errors)
        res = {
            'errors': list(errors),
        }
        logging.error(res)
        self.writer.write(objects, self.filename_to_save)
        return res
