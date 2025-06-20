from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QMessageBox, QStackedWidget, QWidget
from PySide6.QtCore import Signal
from src.utils.api import register_user, login_user
import threading
import requests

class LoginDialog(QDialog):
    login_success = Signal(dict)  # Emits user info/token on success

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login or Register")
        self.setModal(True)
        self.resize(350, 260)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        self.stacked = QStackedWidget()
        # Login form
        login_widget = QWidget()
        login_layout = QVBoxLayout(login_widget)
        login_layout.addWidget(QLabel("Email:"))
        self.login_email = QLineEdit()
        login_layout.addWidget(self.login_email)
        login_layout.addWidget(QLabel("Password:"))
        self.login_password = QLineEdit()
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        login_layout.addWidget(self.login_password)
        self.login_remember = QCheckBox("Remember me")
        login_layout.addWidget(self.login_remember)
        self.login_btn = QPushButton("Login")
        login_layout.addWidget(self.login_btn)
        self.switch_to_register = QPushButton("Need an account? Register")
        login_layout.addWidget(self.switch_to_register)
        self.stacked.addWidget(login_widget)
        # Register form
        register_widget = QWidget()
        register_layout = QVBoxLayout(register_widget)
        register_layout.addWidget(QLabel("Name:"))
        self.register_name = QLineEdit()
        register_layout.addWidget(self.register_name)
        register_layout.addWidget(QLabel("Email:"))
        self.register_email = QLineEdit()
        register_layout.addWidget(self.register_email)
        register_layout.addWidget(QLabel("Password:"))
        self.register_password = QLineEdit()
        self.register_password.setEchoMode(QLineEdit.EchoMode.Password)
        register_layout.addWidget(self.register_password)
        self.register_remember = QCheckBox("Remember me")
        register_layout.addWidget(self.register_remember)
        self.register_btn = QPushButton("Register")
        register_layout.addWidget(self.register_btn)
        self.switch_to_login = QPushButton("Already have an account? Login")
        register_layout.addWidget(self.switch_to_login)
        self.stacked.addWidget(register_widget)
        layout.addWidget(self.stacked)
        self.setLayout(layout)
        # Connections
        self.switch_to_register.clicked.connect(lambda: self.stacked.setCurrentIndex(1))
        self.switch_to_login.clicked.connect(lambda: self.stacked.setCurrentIndex(0))
        self.login_btn.clicked.connect(self._on_login)
        self.register_btn.clicked.connect(self._on_register)
        # (Backend logic will be added later) 

    def _on_login(self):
        email = self.login_email.text().strip()
        password = self.login_password.text()
        if not email or not password:
            QMessageBox.warning(self, "Login", "Please enter email and password.")
            return
        def do_login():
            try:
                result = login_user(email, password)
                self.login_success.emit(result)
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Login Failed", str(e))
        threading.Thread(target=do_login).start()

    def _detect_location(self):
        try:
            resp = requests.get("http://ip-api.com/json", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                city = data.get("city", "")
                country = data.get("country", "")
                if city and country:
                    return f"{city}, {country}"
                elif country:
                    return country
            return "Unknown"
        except Exception:
            return "Unknown"

    def _on_register(self):
        name = self.register_name.text().strip()
        email = self.register_email.text().strip()
        password = self.register_password.text()
        if not name or not email or not password:
            QMessageBox.warning(self, "Register", "Please fill all fields.")
            return
        def do_register():
            location = self._detect_location()
            if location == "Unknown":
                QMessageBox.warning(self, "Location", "Could not auto-detect your location. You can update it later in settings.")
            try:
                result = register_user(email, password, name, location)
                self.login_success.emit(result)
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Registration Failed", str(e))
        threading.Thread(target=do_register).start() 