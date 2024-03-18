"""___Built-In Modules___"""
import os

"""___Third-Party Modules___"""
import pysftp
# This module requires pysftp>=0.2.9

"""___Apogeo Modules___"""
from . import logger 

class CnOptsNoHostKeys(pysftp.CnOpts):
    def __init__(self):
        self.log = False
        self.compression = False
        self.ciphers = None
        self.hostkeys = None


def upload_file_sftp(path: str, config: dict):
    log = logger.get_logger()
    cnopts = CnOptsNoHostKeys()
    if 'host_key_checking' in config and config['host_key_checking']:
        try:
            cnopts = pysftp.CnOpts()
        except pysftp.HostKeysException as e:
            log.warning(f'Warning: {e}')
    with pysftp.Connection(config['remotehost'], config['remoteuser'], password=config['remotepass'], cnopts=cnopts) as srv:
        remotedir = config['remotedir']
        filename = os.path.basename(path)
        dest_path = os.path.join(remotedir, filename)
        if filename in [os.path.basename(f) for f in srv.listdir(remotedir)]:
            log.debug(f'Removing server file {dest_path}')
            srv.remove(dest_path)
        log.info(f'Sending {path}...')
        srv.put(path, dest_path)
