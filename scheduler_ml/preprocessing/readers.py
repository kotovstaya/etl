import ftplib
import tempfile
import typing as tp

import pandas as pd
from minio import Minio


class BaseReader:
    def __init__(self, base_path: str):
        self.base_path = base_path

    def read(self, filename):
        raise NotImplementedError


class FTP2PandasCSVReader(BaseReader):
    def __init__(
            self,
            host: str,
            username: str,
            password: str,
            csv_params: tp.Dict[str, tp.Any],
            **kwargs):
        self.host = host
        self.username = username
        self.password = password
        self.csv_params = csv_params
        super().__init__(**kwargs)
        self.ftp = self._init_ftp()

    def _init_ftp(self):  # TODO: нужно ли закрывать коннекшн?
        ftp = ftplib.FTP(host=self.host, user=self.username, passwd=self.password)
        ftp.cwd(self.base_path)
        return ftp

    def read(self, filename: str):
        tmp_f = tempfile.NamedTemporaryFile(mode='wb+')
        try:
            self.ftp.retrbinary(f'RETR {filename}', tmp_f.write)
        except (*ftplib.all_errors,):
            self.ftp = self._init_ftp()
            self.ftp.retrbinary(f'RETR {filename}', tmp_f.write)
        tmp_f.seek(0)
        with tmp_f as f:
            dfs = pd.read_csv(f, **self.csv_params)
            for df in dfs:
                yield df


class Minio2PandasCSVReader(BaseReader):
    def __init__(
            self,
            host: str,
            access_key: str,
            secret_key: str,
            bucket_name: str,
            csv_params: tp.Dict[str, tp.Any],
            **kwargs):
        self.client = Minio(
            host,
            access_key=access_key,
            secret_key=secret_key,
            secure=False
        )
        self.csv_params = csv_params
        self.bucket_name = bucket_name
    
    def read(self, filename):
        filename = f"{self.bucket_name}/{filename}"
        bucket, path = filename.split("/")
        if type(path) != str:
            path = "/".join(path)
        obj = self.client.get_object(bucket, path)
        print(obj)
        for df in pd.read_csv(obj, **self.csv_params):
            yield df
