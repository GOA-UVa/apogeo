import time
import os
from datetime import datetime, timezone as tz 
import json

import pandas as pd
import pysftp

from cr300.cr300 import CR300

def read_config() -> dict:
    config = None
    with open('config.json') as fp:
        config = json.load(fp)
    return config


def upload_file_sftp(path: str, config: dict):
    try:
        srv = pysftp.Connection(config['sftphost'], config['sftpuser'], password=config['sftppass'])
        srv.chdir(config['sftpdir'])
        srv.put(path)
        srv.close()
    except Exception as e:
        print(f'Error uploading file via sftp: {e}')


def main():
    port = 'COM4'
    # In Linux it would be:
    #port = '/dev/serial/by-id/usb-Campbell_Scientific__Inc._CR300_00000000050C-if00'
    #port = '/dev/ttyACM0'
    config = read_config()
    wait_minutes = float(config['minutes_wait_loop'])
    cr300 = CR300(port)
    connected = False
    out_dir = 'out'
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    print('Connecting...')
    while not connected:
        connected = cr300.connect()
    print('Connected')
    #df = cr300.get_all_records_data()
    #cr300.close()
    while True:
        try:
            dt = datetime.now(tz=tz.utc)
            outpath = os.path.join(out_dir, dt.strftime('%Y-%m-%d.csv'))
            df = cr300.get_last_records_data()
            if os.path.exists(outpath):
                df0 = pd.read_csv(outpath, index_col=0)
                if df.empty:
                    df = df0
                else:
                    df = pd.concat([df0, df])
            df.to_csv(outpath)
            upload_file_sftp(outpath, config)
        except Exception as e:
            print(f'Error when running the main loop: {e}')
        time.sleep(60 * wait_minutes)


if __name__ == '__main__':
    main()
