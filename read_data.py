import time
import os

import pandas as pd

from cr300.cr300 import CR300


def main():
    port = '/dev/serial/by-id/usb-Campbell_Scientific__Inc._CR300_00000000050C-if00'
    #port = '/dev/ttyACM0'
    outpath = 'out/data.csv'
    cr300 = CR300(port)
    connected = False
    print('Connecting...')
    while not connected:
        connected = cr300.connect()
    print('Connected')
    #df = cr300.get_all_records_data()
    #cr300.close()
    while True:
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
