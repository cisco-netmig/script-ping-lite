import pythonping
import socket
import logging
import time
from PyQt5 import QtCore

class ContinuousPingWorker(QtCore.QThread):
    """
    Worker thread to continuously ping an IP address and emit updates.
    """
    update_signal = QtCore.pyqtSignal(dict)

    def __init__(self, ip_props):
        """
        Initialize the ping worker.

        Args:
            ip_props (dict): Dictionary containing IP-related metadata.
        """
        super().__init__()
        self.ip_props = ip_props

    def run(self):
        """
        Execute continuous pinging and emit updates periodically.
        """
        logging.info(f"Started ContinuousPingWorker for {self.ip_props['ip']}")
        data = {
            'row': self.ip_props['row'],
            'ip': self.ip_props['ip'],
            'fqdn': socket.getfqdn(self.ip_props['ip']),
            'sent': 0,
            'received': 0,
            'lost': 0,
            'rtt': 0,
            'success': False,
            'thread': ''
        }

        while not self.ip_props.get('stop', False):
            try:
                response = pythonping.ping(self.ip_props['ip'], count=1, timeout=1)
                data['sent'] += response.stats_packets_sent
                data['received'] += response.stats_packets_returned
                data['lost'] += response.stats_packets_lost
                data['rtt'] = response.rtt_avg_ms
                data['success'] = response.success()
                data['thread'] = 'Running'
                self.update_signal.emit(data)
                logging.debug(f"Ping data updated for {data['ip']}: {data}")
                time.sleep(1)
            except Exception as e:
                logging.error(f"Error pinging {self.ip_props['ip']}: {e}")
                break

        logging.info(f"Stopped ContinuousPingWorker for {self.ip_props['ip']}")
