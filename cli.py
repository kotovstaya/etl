import logging

import click
from scheduler_ml.preprocessing import extractors


@click.group()
def messages():
  pass


@click.command()
@click.option('--host', type=str, default="minio:9000")
@click.option('--access-key', type=str, default="admin")
@click.option('--secret-key', type=str, default="admin123")
def delivery_extractor(host, access_key, secret_key):
    logging.error("DELIVERY EXTRACTOR")

    hde = extractors.HistDataExtractor(
        reader_params={
            "host": host,
            "access_key": access_key,
            "secret_key": secret_key,
            "bucket_name": "data-science",
            "base_path": "/Upload",
            "csv_params": {
                "sep": ";", 
                "dtype": str, 
                "chunksize": 10000, 
                "index_col": False,
            }
        },
        transformer_params={
            "system_code": 'pobeda',
            "separated_file_for_each_shop": False,
            "data_type": 'delivery',
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
        dt_from='2022-11-14',
        dt_to='2022-11-14',
        filename_fmt='{data_type}_{year:04d}{month:02d}{day:02d}.csv',
    )

    hde.extract()


messages.add_command(delivery_extractor)

if __name__ == '__main__':
    messages()