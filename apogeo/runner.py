"""___Built-In Modules___"""
import time
import os
from datetime import datetime, timezone as tz 
import json
import traceback
import signal
import shutil
from threading import Lock, Thread

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
    df.to_csv(outpath)


def upload_files(config: dict, out_dir: str, current_file: str):
    files = os.listdir(out_dir)
    for file in files:
        fullpath = os.path.join(out_dir, file)
        ftp.upload_file_ftp(fullpath, config)
        if file != current_file:
            os.makedirs(_DIR_SENT_OLD, exist_ok=True)
            dst = os.path.join(_DIR_SENT_OLD, file)
            shutil.move(fullpath, dst)


_stopping = False
_loop_lock = Lock()

def gracefully_exit(signum, frame):
    """
    The _stopping global variable is set to True (allowing the exit of the main loop) and
    the global _loop_lock is released, allowing to exit from the loop sleep. 
    """
    global _stopping
    log = logger.get_logger()
    if not _stopping:
        _stopping = True
        msg = 'Gracefully exiting, program will finish when the current iteration of the main loop finishes.'
        print(msg)
        log.info(msg)
        _loop_lock.release()
    else:
        msg = 'Graceful exit already requested. Please wait for the program to finish.'
        print(msg)
        log.info(msg)


def _thread_loop_sleep(seconds: int, lock: Lock):
    lock.acquire()
    time.sleep(seconds)
    if not _stopping:
        lock.release()


def loop_sleep(seconds: int):
    """
    A new thread is created where the _loop_lock is acquired thus not letting this method
    finish until it ends, or _loop_lock is released through a keyboard interrupt.
    """
    t = Thread(target=_thread_loop_sleep, args=(seconds, _loop_lock), daemon=True)
    _loop_lock.release()
    t.start()
    time.sleep(5)
    _loop_lock.acquire()


def run():
    # TODO Improve logging, not regular prints.
    signal.signal(signal.SIGINT, gracefully_exit)
    _loop_lock.acquire()
    config = read_config()
    log = logger.get_logger()
    port = config['serialport']
    wait_minutes = float(config['minutes_wait_loop'])
    try:
        cr300 = CR300(port)
    except Exception as e:
        msg = f'ERROR opening connection with CR300: {e}.\nMake sure no other program is connected to the CR300 (PC400, LoggerNet...)'
        print(msg)
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
    while not _stopping:
        try:
            dt = datetime.now(tz=tz.utc)
            filename = dt.strftime('%Y-%m-%d.csv')
            outpath = os.path.join(out_dir, filename)
            get_from_cr300(cr300, outpath)
            log.debug('Stored CR300 info')
            upload_files(config, out_dir, filename)
            log.debug('Uploaded files through FTP')
        except Exception as e:
            trace = traceback.format_exc()
            log.error(f'Error when running the main loop: {e}.\nTrace: {trace}')
        if not _stopping:
            loop_sleep(60 * wait_minutes)
    cr300.close()
    log.info('Finished running')
    print('Finished running')
