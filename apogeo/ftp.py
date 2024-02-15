"""___Built-In Modules___"""
import os
from io import StringIO
import traceback
import ftplib
import socket

"""___Apogeo Modules___"""
from . import logger


BUFFER_SIZE = 1024*25
SECONDS_FTP_TIMEOUT = 10*60


class ProcessLogger:
    def __init__(self, filesize, buffersize, ftp_server):
        self.filesize = filesize
        self.buffersize = buffersize
        self.ftp_server = ftp_server
        self.sentsize = 0
        self.log = logger.get_logger()

    def callback_buffer_sent(self, buf):
        self.sentsize += self.buffersize
        if self.sentsize >= self.filesize:
            self.sentsize = self.filesize
            self.ftp_server.sock.settimeout(5)
        self.log.debug(f"Sent {self.sentsize}/{self.filesize}")
    
    def is_completed(self) -> bool:
        return self.sentsize == self.filesize


def upload_file_ftp(path: str, config: dict):
    log = logger.get_logger()
    try:
        ftp_server = ftplib.FTP(config['remotehost'], config['remoteuser'], config['remotepass'], timeout=SECONDS_FTP_TIMEOUT)
        ftp_server.encoding = "utf-8"
        remotedir = config['remotedir']
        filename = os.path.basename(path)
        dest_path = os.path.join(remotedir, filename)
        if filename in [os.path.basename(f) for f in ftp_server.nlst(remotedir)]:
            log.info(f'Removing server file {dest_path}')
            ftp_server.delete(dest_path)
        log.info(f'Sending {path}...')
        filesize = os.path.getsize(path)
        pl = ProcessLogger(filesize, BUFFER_SIZE, ftp_server)
        try:
            with open(path, "rb") as file:
                _ = ftp_server.storbinary(f"STOR {dest_path}", file, BUFFER_SIZE, pl.callback_buffer_sent)
            ftp_server.quit()
        except socket.timeout:
            if not pl.is_completed():
                raise Exception(f'Socket timed-out while sending file. Sent {pl.sentsize}/{pl.filesize}.')
    except Exception as e:
        trace = traceback.format_exc()
        log.error(f'Error uploading file via ftp: {e}. {trace}')
        print(f'Error uploading file via ftp: {e}')
