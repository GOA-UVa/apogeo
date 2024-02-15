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
    try:
        cnopts = CnOptsNoHostKeys()
        if 'host_key_checking' in config and config['host_key_checking']:
            try:
                cnopts = pysftp.CnOpts()
            except pysftp.HostKeysException as e:
                log.warning(f'Warning: {e}')
        with pysftp.Connection(config['remotehost'], config['remoteuser'], password=config['remotepass'], cnopts=cnopts) as srv:
            log.info(f'Sending {path}...')
            dest_path = os.path.join(config['remotedir'], os.path.basename(path))
            srv.put(path, dest_path)
    except Exception as e:
        log.error(f'Error uploading file via sftp: {e}')
