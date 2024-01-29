import time
import os
from datetime import datetime, timezone as tz 

import pandas as pd

from cr300.cr300 import CR300


def main():
    port = 'COM4'
    # In Linux it would be:
    #port = '/dev/serial/by-id/usb-Campbell_Scientific__Inc._CR300_00000000050C-if00'
    #port = '/dev/ttyACM0'
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
        time.sleep(60)


if __name__ == '__main__':
    main()
