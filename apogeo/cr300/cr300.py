from io import StringIO
import time

import serial
import pandas as pd

_MAX_RECORDS_MSG = 20
_REBOOT_WAIT_TIME = 10
_DEFAULT_DELAY = 1
_DEFAULT_DELAY_FAST = 0.01


class CR300():
    def __init__(self, port: str, baudrate: int = 9600, timeout: float = None, fast: bool = False):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.fast = fast
        self.s = serial.Serial(port, baudrate, timeout=timeout)

    def new_serial(self):
        self.s.close()
        self.s = serial.Serial(self.port, self.baudrate, timeout=self.timeout)

    def refresh(self):
        self.s.close()
        self.s.open()

    def _send_command_fast(self, cmd: str, delay=_DEFAULT_DELAY_FAST) -> str:
        cmd_send = f"{cmd}\r\n".encode()
        self.s.write(cmd_send)
        out = b""
        empty_returns = 0
        max_empty_returns = 2/delay
        while not out.endswith(b"\r\nCR300>"):
            ret = self.s.read_all()
            if len(ret) == 0:
                empty_returns += 1
                if empty_returns > max_empty_returns:
                    break # The response is empty
                time.sleep(delay)
            else:
                empty_returns = 0
            out += ret
        if not out.startswith(cmd_send):
            raise Exception("DataLogger didn't answer with the sent CMD at the begining. Something wrong happened.")
        return '\n'.join(out.decode().split('\r\n'))

    def _send_command(self, cmd: str, delay=_DEFAULT_DELAY) -> str:
        cmd_send = f"{cmd}\r\n".encode()
        self.s.write(cmd_send)
        time.sleep(delay)
        out = self.s.read_all()
        if not out.startswith(cmd_send):
            raise Exception("DataLogger didn't answer with the sent CMD at the begining. Something wrong happened.")
        return '\n'.join(out.decode().split('\r\n'))

    def _get_default_delay(self) -> float:
        if self.fast:
            return _DEFAULT_DELAY_FAST
        return _DEFAULT_DELAY

    def send_command(self, cmd: str, delay: float = None, _try=0) -> str:
        if delay == None:
            delay = self._get_default_delay()
        try:
            if self.fast:
                out = self._send_command_fast(cmd, delay)
            else:
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
        if len(out_lines) == 0:
            return pd.DataFrame([])
        out_lines[0] = ' '.join(['date', 'time', 'type', 'id'] + out_lines[0].split()[1:])
        out = '\n'.join(out_lines).replace('   ', ' ').replace('   ', ' ')
        df = pd.read_csv(StringIO(out), sep=' ', header=0, index_col=3)
        df['datetime'] = pd.to_datetime(df['date'] + df['time'], format='%Y/%m/%d%H:%M:%S.%f')
        df.drop(['date', 'time', 'type'], inplace=True, axis=1)
        return df

    def get_last_records_data(self):
        dfs = []
        keep_seeking = True
        while keep_seeking:
            df = self.get_one_records_data()
            if len(df) == 0:
                keep_seeking = False
            else:
                dfs.append(df)
        if dfs:
            df = pd.concat(dfs)
            df.index = df.index.astype(int)
            df = df[~df.index.duplicated(keep='last')]
        return df

    def get_all_records_data(self):
        self.send_command('reboot')
        self.send_command('YES')
        time.sleep(_REBOOT_WAIT_TIME)
        return self.get_last_records_data()
