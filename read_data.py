import time

import serial


class CR300():
    def __init__(self, port: str, baudrate: int = 9600):
        self.port = port
        self.baudrate = baudrate
        self.s = serial.Serial(port, baudrate)

    def new_serial(self):
        self.s.close()
        self.s = serial.Serial(self.port, self.baudrate)

    def refresh(self):
        self.s.close()
        self.s.open()

    def send_command(self, cmd: str, delay=1) -> str:
        print(f"{cmd}\r\n".encode())
        self.s.write(f"{cmd}\r\n".encode())
        time.sleep(delay)
        out = self.s.read_all()
        print(out)
        return '\n'.join(out.decode().split('\r\n'))

    def connect(self, delay = 0.1) -> bool:
        self.s.write(f"\r\n".encode())
        time.sleep(delay)
        out = self.s.read_all()
        return out == b"\r\nCR300>"

    def close(self):
        self.s.close()


def main():
    #port = '/dev/serial/by-id/usb-Campbell_Scientific__Inc._CR300_00000000050C-if00'
    port = '/dev/ttyACM0'
    cr300 = CR300(port)
    connected = False
    print('Connecting...')
    while not connected:
        connected = cr300.connect()
    print('Connected')
    resp = cr300.send_command('SHOW RECORDS')
    print(resp)

    resp = cr300.send_command('HELP')
    print(resp)
    cr300.close()
    

if __name__ == '__main__':
    main()
