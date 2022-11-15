import pandas as pd
from faker.providers.date_time import Provider as DateTimeProvider
from wfm_ml.preprocessing import readers, transformers


class HistDataExtractor:
    def __init__(self, reader_params, transformer_params, dt_from, dt_to, filename_fmt):
        self.dt_from = dt_from
        self.dt_to = dt_to
        self.filename_fmt = filename_fmt
        self.separated_file_for_each_shop = False

        self.transformer_params = transformer_params
        self.reader_params = reader_params

        if "columns" in self.transformer_params.keys():
            self.reader_params['csv_params']["index_col"] = False
            self.reader_params["csv_params"]["names"] = self.transformer_params["columns"]

        self.reader = readers.FTP2PandasCSVReader(**self.reader_params)
        self.transformer = transformers.HistDataTransformer(**self.transformer_params)

        self._dt_provider = DateTimeProvider(generator=None)

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
        dt_from = self._dt_provider._parse_date(self.dt_from)
        dt_to = self._dt_provider._parse_date(self.dt_to)
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
            print(filename, dtt)
            reader_generator = self.reader.read(filename)
            load_errors = self.transformer.transform(
                reader_generator, dtt, filename)
            if load_errors:
                errors = errors.union(load_errors)
        res = {
            'errors': list(errors),
        }
        return res


if __name__ == "__main__":

    hde = HistDataExtractor(
        reader_params={
            "host": "95.68.243.12",
            "username": "mm-bav",
            "password": "XRbTMp2N",
            "base_path": "/Upload",
            "csv_params": {"sep": ";", "chunksize": 10, "dtype": str}
        },
        transformer_params={
            "system_code": 'pobeda',
            "separated_file_for_each_shop": False,
            "data_type": 'Delivery',
            "columns": [
                'Какой-то guid',
                'Номер магазина id',
                'Дата и время',
                'Тип поставки',
                'Id SKU',
                'Количество товара',
            ],
            "shop_num_column_name": 'Номер магазина id',
            "dt_or_dttm_column_name": 'Дата и время',
            "receipt_code_columns":[
                'Какой-то guid',
                'Id SKU',
            ],
            "dt_or_dttm_format": '%d.%m.%Y %H:%M:%S',
        },
        dt_from=-1,
        dt_to=-1,
        filename_fmt='{data_type}_{year:04d}{month:02d}{day:02d}.csv',
    )


    hde.extract()