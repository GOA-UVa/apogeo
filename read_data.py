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
import pysftp

"""___Apogeo Modules___"""
from cr300.cr300 import CR300

_OUT_DIR = 'out'
_DIR_SENT_OLD = 'sent'


def read_config() -> dict:
    config = None
    with open('config.json') as fp:
        config = json.load(fp)
    return config


def upload_file_sftp(path: str, config: dict):
    try:
        cnopts = pysftp.CnOpts() # knownhosts='known_hosts'
        if not config['host_key_checking']:
            cnopts.hostkeys = None
        with pysftp.Connection(config['sftphost'], config['sftpuser'], password=config['sftppass'], cnopts=cnopts) as srv:
            print(f'Sending {path}...')
            dest_path = os.path.join(config['sftpdir'], os.path.basename(path))
            srv.put(path, dest_path)
    except Exception as e:
        print(f'Error uploading file via sftp: {e}')


def get_from_cr300(cr300: CR300, config: dict, outpath: str):
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
        upload_file_sftp(fullpath, config)
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
    if not _stopping:
        _stopping = True
        print('Gracefully exiting, program will finish when the current iteration of the main loop finishes.')
        _loop_lock.release()
    else:
        print('Graceful exit already requested. Please wait for the program to finish.')


def _thread_loop_sleep(seconds: int, lock: Lock):
    lock.acquire()
    print('loopsleep')
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
    print('waiting for acquire')
    _loop_lock.acquire()
    print('releasing...')


def main():
    # TODO Improve logging, not regular prints.
    # TODO Test that graceful exit is working.
    signal.signal(signal.SIGINT, gracefully_exit)
    _loop_lock.acquire()
    config = read_config()
    port = config['serialport']
    wait_minutes = float(config['minutes_wait_loop'])
    try:
        cr300 = CR300(port)
    except Exception as e:
        print(f'ERROR opening connection with CR300: {e}.')
        print('Make sure no other program is connected to the CR300 (PC400, LoggerNet...)')
        exit(1)
    connected = False
    out_dir = _OUT_DIR
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    print('Connecting to CR300...')
    while not connected:
        connected = cr300.connect()
    print('Connected')
    #df = cr300.get_all_records_data()
    while not _stopping:
        try:
            dt = datetime.now(tz=tz.utc)
            filename = dt.strftime('%Y-%m-%d.csv')
            outpath = os.path.join(out_dir, filename)
            get_from_cr300(cr300, config, outpath)
            print('Stored')
            upload_files(config, out_dir, filename)
            print('Uploaded through SFTP')
        except Exception as e:
            trace = traceback.format_exc()
            print(f'Error when running the main loop: {e}.\nTrace: {trace}')
        if not _stopping:
            loop_sleep(60 * wait_minutes)
    cr300.close()
    print('Finished running')


if __name__ == '__main__':
    main()
