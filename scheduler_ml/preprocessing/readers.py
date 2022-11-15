import ftplib
import tempfile
import typing as tp

import pandas as pd


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
        return tmp_f
