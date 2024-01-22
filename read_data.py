import time
import os
from io import StringIO

import serial
import pandas as pd


class CR300():
    def __init__(self, port: str, baudrate: int = 9600, timeout: float = None):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.s = serial.Serial(port, baudrate, timeout=timeout)

    def new_serial(self):
        self.s.close()
        self.s = serial.Serial(self.port, self.baudrate, timeout=self.timeout)

    def refresh(self):
        self.s.close()
        self.s.open()

    def _send_command(self, cmd: str, delay=1) -> str:
        cmd_send = f"{cmd}\r\n".encode()
        self.s.write(cmd_send)
        time.sleep(delay)
        out = self.s.read_all()
        if not out.startswith(cmd_send):
            raise Exception("DataLogger didn't answer with the sent CMD at the begining. Something wrong happened.")
        return '\n'.join(out.decode().split('\r\n'))

    def send_command(self, cmd: str, delay=1, _try=0) -> str:
        try:
            out = self._send_command(cmd, delay)
        except Exception:
            if _try > 2:
                raise Exception("Connection lost, and couldn't recover it.")
            elif _try < 2:
                self.refresh()
            else:
                self.new_serial()
            connected = False
            while not connected:
                connected = self.connect()
            out = self.send_command(cmd, delay, _try + 1)
        return out

    def connect(self, delay = 0.1) -> bool:
        self.s.write(f"\r\n".encode())
        time.sleep(delay)
        out = self.s.read_all()
        return out == b"\r\nCR300>"

    def close(self):
        self.s.close()

    def get_one_records_data(self):
        out_lines = self.send_command("SHOW RECORDS").splitlines()[1:-1]
        out_lines[0] = ' '.join(['date', 'time', 'type', 'id'] + out_lines[0].split()[1:])
        out = '\n'.join(out_lines).replace('   ', ' ')
        df = pd.read_csv(StringIO(out), sep=' ', header=0, index_col=3)
        df['datetime'] = pd.to_datetime(df['date'] + df['time'], format='%Y/%m/%d%H:%M:%S.%f')
        df.drop(['date', 'time', 'type'], inplace=True, axis=1)
        return df

    def get_last_records_data(self):
        dfs = []
        keep_seeking = True
        while keep_seeking:
            df = self.get_one_records_data()
            dfs.append(df)
            if len(df) < 20:
                keep_seeking = False
        df = pd.concat(dfs)
        return df

    def get_all_records_data(self):
        self.send_command('reboot')
        self.send_command('YES')
        time.sleep(10)
        return self.get_last_records_data()

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
