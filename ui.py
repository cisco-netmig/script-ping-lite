import logging
import os
import re
import copy
import ipaddress
from PyQt5 import QtWidgets, QtGui, QtCore
from .workers import ContinuousPingWorker

class Ui_Form:
    """
    A PyQt5 UI form class for configuring and executing network diagnostics.

    """

    def setup_ui(self, form):
        """
        Set up the layout and UI elements of the diagnostics form.

        Args:
            form (QWidget): The parent widget to apply the layout and components to.
        """
        self.form = form
        self.layout = QtWidgets.QVBoxLayout(form)

        # Initialize and configure action buttons
        self.actions_layout = QtWidgets.QHBoxLayout()
        self.actions_layout.setSpacing(10)
        self.layout.addLayout(self.actions_layout)

        self.add_network_button = self._create_action_button('add', 'Add Host/IP/Subnets')
        self.start_button = self._create_action_button('start', 'Start All', disabled=True)
        self.stop_button = self._create_action_button('stop', 'Stop All', disabled=True)
        self.clear_button = self._create_action_button('clear', 'Clear Table', disabled=True)

        self.actions_layout.addItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        # Initialize and configure the ping table
        self.ping_table = QtWidgets.QTableWidget(self.form)
        self.ping_table.setColumnCount(8)
        self.ping_table.setHorizontalHeaderLabels([
            '', 'IP Address', 'Hostname', 'Sent', 'Received', 'Lost', 'RTT', 'Thread'
        ])
        self.ping_table.horizontalHeader().setHighlightSections(False)
        self.ping_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.ping_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.ping_table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.ping_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ping_table.customContextMenuRequested.connect(self._table_menu_event)
        self.ping_table.setSortingEnabled(True)
        self._configure_table_columns()

        self.layout.addWidget(self.ping_table)

        # Load status icons
        self.red_icon = self._get_icon('red')
        self.green_icon = self._get_icon('green')
        self.yellow_icon = self._get_icon('yellow')

        # Configure the context menu for the table
        self._create_context_menu()

    def _create_action_button(self, icon_name, tooltip, disabled=False):
        """
        Helper method to create a standardized QPushButton with an icon and tooltip.
        """
        button = QtWidgets.QPushButton(self.form)
        button.setIcon(self._get_icon(icon_name))
        button.setIconSize(QtCore.QSize(20, 20))
        button.setToolTip(tooltip)
        button.setDisabled(disabled)
        self.actions_layout.addWidget(button)
        return button

    def _configure_table_columns(self):
        """
        Applies predefined widths and stretch behaviors to the ping table columns.
        """
        self.ping_table.setColumnWidth(0, 0)
        self.ping_table.setColumnWidth(1, 160)
        self.ping_table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.ping_table.setColumnWidth(3, 100)
        self.ping_table.setColumnWidth(4, 100)
        self.ping_table.setColumnWidth(5, 100)
        self.ping_table.setColumnWidth(6, 140)
        self.ping_table.setColumnWidth(7, 150)
        self.ping_table.verticalHeader().setVisible(False)

    def _create_context_menu(self):
        """
        Initializes the context menu with relevant actions.
        """
        self.table_menu = QtWidgets.QMenu(self.form)

        self.start_selected_action = QtWidgets.QAction(self.form)
        self.start_selected_action.setIcon(self._get_icon('start'))
        self.start_selected_action.setText('Start Selected')
        self.table_menu.addAction(self.start_selected_action)

        self.stop_selected_action = QtWidgets.QAction(self.form)
        self.stop_selected_action.setIcon(self._get_icon('stop'))
        self.stop_selected_action.setText('Stop Selected')
        self.table_menu.addAction(self.stop_selected_action)

        self.table_menu.addSeparator()

        self.add_network_action = QtWidgets.QAction(self.form)
        self.add_network_action.setIcon(self._get_icon('add'))
        self.add_network_action.setText('Add Host/IP/Subnets')
        self.table_menu.addAction(self.add_network_action)

        self.start_all_action = QtWidgets.QAction(self.form)
        self.start_all_action.setIcon(self._get_icon('start'))
        self.start_all_action.setText('Start All')
        self.start_all_action.setDisabled(True)
        self.table_menu.addAction(self.start_all_action)

        self.stop_all_action = QtWidgets.QAction(self.form)
        self.stop_all_action.setIcon(self._get_icon('stop'))
        self.stop_all_action.setText('Stop All')
        self.stop_all_action.setDisabled(True)
        self.table_menu.addAction(self.stop_all_action)

        self.clear_action = QtWidgets.QAction(self.form)
        self.clear_action.setIcon(self._get_icon('clear'))
        self.clear_action.setText('Clear Table')
        self.clear_action.setDisabled(True)
        self.table_menu.addAction(self.clear_action)

    def _table_menu_event(self, pos):
        """
        Handles the context menu event on the ping table.

        Parameters:
            pos (QPoint): The position where the context menu is requested.
        """
        selected_ips = self.get_selected_items()
        self.start_selected_action.setDisabled(not selected_ips)
        self.stop_selected_action.setDisabled(not selected_ips)
        self.table_menu.exec_(self.ping_table.mapToGlobal(pos))

    def get_selected_items(self):
        """
        Returns a list of IP addresses from the selected rows in the table.

        Returns:
            List[str]: A list of selected IP addresses.
        """
        return [
            item.text() for item in self.ping_table.selectedItems()
            if item.column() == 1
        ]

    def _get_icon(self, filename: str) -> QtGui.QIcon:
        """
        Load an icon from the assets directory.

        Args:
            filename (str): Name of the icon file (without extension).

        Returns:
            QtGui.QIcon: The QIcon object.
        """
        icon_path = os.path.join(os.path.dirname(__file__), "assets", f"{filename}.ico")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        return icon


class Form(QtWidgets.QWidget, Ui_Form):
    """
    UI Form class.

    """

    def __init__(self, parent=None, **kwargs):
        """
        Initialize the UI form.

        Args:
            parent (QWidget): Parent widget.
            **kwargs: Additional arguments for customization or metadata.
        """
        super().__init__(parent)
        self.kwargs = kwargs
        self.setup_ui(self)
        self.ip_data = {}

        self.add_network_button.clicked.connect(self.setup_add_network_dialog)
        self.add_network_action.triggered.connect(self.setup_add_network_dialog)
        self.start_button.clicked.connect(self.start_all_ping_event)
        self.start_all_action.triggered.connect(self.start_all_ping_event)
        self.start_selected_action.triggered.connect(self.start_selected)
        self.stop_button.clicked.connect(self.stop_all_ping_event)
        self.stop_all_action.triggered.connect(self.stop_all_ping_event)
        self.stop_selected_action.triggered.connect(self.stop_selected)
        self.clear_button.clicked.connect(self.clear_all_table_event)
        self.clear_action.triggered.connect(self.clear_all_table_event)

    def setup_add_network_dialog(self):
        """Create and display the Add Network dialog."""
        logging.debug("Opening Add Network dialog.")
        self.add_dialog = QtWidgets.QDialog(self)
        self.add_dialog.setWindowTitle('Add Host/IP/Subnets')
        self.add_dialog.setWindowFlags(self.add_dialog.windowFlags() ^ QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        self.add_dialog.setWindowIcon(self._get_icon('add'))

        self.layout = QtWidgets.QVBoxLayout(self.add_dialog)
        self.network_text_edit = QtWidgets.QTextEdit(self.add_dialog)
        self.network_text_edit.setMinimumSize(QtCore.QSize(250, 500))
        self.layout.addWidget(self.network_text_edit)

        self.add_button = QtWidgets.QPushButton(self)
        self.add_button.setText('Add')
        self.add_button.clicked.connect(self.create_entries_event)
        self.add_button.setIconSize(QtCore.QSize(25, 25))
        self.layout.addWidget(self.add_button)

        self.add_dialog.show()

    def create_entries_event(self):
        """Process user input and add IPs to the table."""
        logging.debug("Creating entries from Add Network dialog.")
        string_list = list(filter(None, self.form.network_text_edit.toPlainText().splitlines()))
        for string in string_list:
            ip_list = self.get_ip(string)
            for ip in ip_list:
                if not self.ip_data.get(ip):
                    self.ip_data[ip] = {}
                    row = self.ping_table.rowCount()
                    self.ping_table.insertRow(row)

                    status_button = QtWidgets.QPushButton()
                    status_button.setStyleSheet('QPushButton {background:transparent; border: none}')
                    status_button.setIcon(self.yellow_icon)
                    status_button.setIconSize(QtCore.QSize(20, 20))
                    self.ping_table.setCellWidget(row, 0, status_button)
                    self.ping_table.setItem(row, 1, QtWidgets.QTableWidgetItem(ip))
                    for col in range(2, 8):
                        self.ping_table.setItem(row, col, QtWidgets.QTableWidgetItem('' if col != 7 else 'Init'))

                    self.ip_data[ip] = {
                        'row': row,
                        'status_button': status_button,
                        'thread': 'Init',
                        'fqdn': '',
                        'ip': ip
                    }

        self.add_dialog.close()
        self.start_button.setDisabled(not self.ip_data)
        self.start_all_action.setDisabled(not self.ip_data)
        self.clear_button.setDisabled(not self.ip_data)
        self.clear_action.setDisabled(not self.ip_data)

    def get_ip(self, string):
        """
        Resolve a string to one or more IP addresses.

        Args:
            string (str): A hostname or CIDR/IP string.

        Returns:
            list: List of IP addresses.
        """
        logging.debug(f"Resolving input to IPs: {string}")
        if re.search(r'^\d+\.\d+\.\d+\.\d+', string):
            if '/' in string:
                return [str(ip) for ip in ipaddress.ip_network(string).hosts()]
            return [string]
        try:
            return [socket.gethostbyname(string)]
        except Exception as e:
            logging.warning(f"Failed to resolve hostname {string}: {e}")
            return []

    def start_all_ping_event(self):
        """Start pinging all listed IPs."""
        logging.info("Starting all ping tasks.")
        self.stop_button.setDisabled(False)
        self.stop_all_action.setDisabled(False)

        for ip, props in copy.copy(self.ip_data).items():
            self.ip_data[ip]['stop'] = False
            if props.get('worker'):
                props['worker'].start()
            else:
                worker = ContinuousPingWorker(props)
                worker.start()
                worker.update_signal.connect(self.update_table)
                self.ip_data[ip]['worker'] = worker

    def stop_all_ping_event(self):
        """Stop all ongoing ping tasks."""
        logging.info("Stopping all ping tasks.")
        for ip, props in copy.copy(self.ip_data).items():
            if props.get('worker'):
                self.ip_data[ip]['stop'] = True
                self.form.ping_table.item(props['row'], 7).setText('Stopped')
                props['status_button'].setIcon(self.yellow_icon)

    def clear_all_table_event(self):
        """Clear all entries in the ping table."""
        logging.info("Clearing all table entries.")
        self.stop_all_ping_event()
        self.ip_data = {}
        self.ping_table.setRowCount(0)
        for button in [self.start_button, self.start_all_action, self.stop_button, self.stop_all_action,
                       self.clear_button, self.clear_action]:
            button.setDisabled(True)

    def start_selected(self):
        """Start pinging only the selected IPs."""
        logging.info("Starting selected ping tasks.")
        self.stop_button.setDisabled(False)
        self.stop_all_action.setDisabled(False)
        ip_list = self.get_selected_items()

        for ip in ip_list:
            self.ip_data[ip]['stop'] = False
            if self.ip_data[ip].get('worker'):
                self.ip_data[ip]['worker'].start()
            else:
                worker = WorkerContinuousPing(self.ip_data[ip])
                worker.start()
                worker.updateSignal.connect(self.update_table)
                self.ip_data[ip]['worker'] = worker

    def stop_selected(self):
        """Stop only the selected ping tasks."""
        logging.info("Stopping selected ping tasks.")
        ip_list = self.get_selected_items()

        for ip in ip_list:
            if self.ip_data[ip].get('worker'):
                self.ip_data[ip]['stop'] = True
                self.form.ping_table.item(self.ip_data[ip]['row'], 7).setText('Stopped')
                self.ip_data[ip]['status_button'].setIcon(self.yellow_icon)

    def update_table(self, data):
        """
        Update the ping table with new data from a worker.

        Args:
            data (dict): Contains ping results and status info.
        """
        logging.debug(f"Updating table with data: {data}")
        icon = self.green_icon if data['success'] else self.red_icon
        self.ip_data[data['ip']]['status_button'].setIcon(icon)

        for idx, key in enumerate(['fqdn', 'sent', 'received', 'lost', 'rtt', 'thread'], start=2):
            self.ping_table.item(data['row'], idx).setText(str(data[key]))
