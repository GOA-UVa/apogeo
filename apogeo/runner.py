"""___Built-In Modules___"""
import os
from datetime import datetime, timezone as tz 
import json
import traceback
import shutil

"""___Third-Party Modules___"""
import pandas as pd

"""___Apogeo Modules___"""
from .cr300.cr300 import CR300
from . import ftp, logger

_OUT_DIR = 'out'
_DIR_SENT_OLD = 'sent'


def read_config() -> dict:
    config = None
    with open('config.json') as fp:
        config = json.load(fp)
    return config


def get_from_cr300(cr300: CR300, outpath: str):
    df = cr300.get_last_records_data()
    if os.path.exists(outpath):
        df0 = pd.read_csv(outpath, index_col=0)
        if df.empty:
            df = df0
        else:
            df = pd.concat([df0, df])
            df.index = df.index.astype(int)
            df[~df.index.duplicated(keep='first')]
    if not df.empty:
        df.to_csv(outpath)


def upload_files(config: dict, out_dir: str, current_file: str):
    log = logger.get_logger()
    files = os.listdir(out_dir)
    for file in files:
        fullpath = os.path.join(out_dir, file)
        try:
            ftp.upload_file_ftp(fullpath, config)
            if file != current_file:
                os.makedirs(_DIR_SENT_OLD, exist_ok=True)
                dst = os.path.join(_DIR_SENT_OLD, file)
                shutil.move(fullpath, dst)
        except Exception as e:
            trace = traceback.format_exc()
            log.error(f'Error uploading file via ftp: {e}. {trace}')
            print(f'Error uploading file via ftp: {e}')


def run():
    log = logger.get_logger()
    try:
        config = read_config()
        port = config['serialport']
        try:
            cr300 = CR300(port, fast=True)
        except Exception as e:
            msg = f'ERROR opening connection with CR300: {e}.\nMake sure no other program is connected to the CR300 (PC400, LoggerNet...)'
            log.critical(msg)
            exit(1)
        connected = False
        out_dir = _OUT_DIR
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        log.info('Connecting to CR300...')
        while not connected:
            connected = cr300.connect()
        log.info('Connected')
        try:
            dt = datetime.now(tz=tz.utc)
            filename = dt.strftime('%Y-%m-%d.csv')
            outpath = os.path.join(out_dir, filename)
            get_from_cr300(cr300, outpath)
            log.info('Stored CR300 info')
            upload_files(config, out_dir, filename)
            log.info('Uploaded files through FTP')
        except Exception as e:
            trace = traceback.format_exc()
            log.critical(f'Error when running the main loop: {e}.\nTrace: {trace}')
        cr300.close()
    except Exception as e:
        log.critical(f'Something happened: {e}')
    log.info('Finished running')
