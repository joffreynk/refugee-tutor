"""WiFi management module for offline/online connectivity."""

import base64
import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Optional

from config import settings

logger = logging.getLogger(__name__)

_SUDO_CONFIG_PATH = settings.DATA_DIR / "sudo_config.json"
_CREDENTIALS_PATH = settings.DATA_DIR / "credentials.json"


def _load_credentials() -> dict:
    """Load all credentials from file."""
    creds = {
        "sudo": None,
        "wifi_ssid": None,
        "wifi_password": None,
        "bluetooth_devices": {},
    }
    
    if _CREDENTIALS_PATH.exists():
        try:
            with open(_CREDENTIALS_PATH) as f:
                data = json.load(f)
                creds.update(data)
        except Exception as e:
            logger.warning(f"Could not load credentials: {e}")
    
    return creds


def _load_sudo_password() -> Optional[str]:
    """Load sudo password from environment or config file."""
    creds = _load_credentials()
    if creds.get("sudo"):
        return creds["sudo"]
    
    env_password = os.environ.get("SUDO_PASSWORD")
    if env_password:
        return env_password
    
    if _SUDO_CONFIG_PATH.exists():
        try:
            with open(_SUDO_CONFIG_PATH) as f:
                config = json.load(f)
                return config.get("sudo_password")
        except Exception:
            pass
    
    pi_dir = Path(__file__).parent
    passwords_file = pi_dir / "passwords.txt"
    if passwords_file.exists():
        try:
            config_content = passwords_file.read_text().strip()
            lines = config_content.split("\n")
            for line in lines:
                if line.startswith("sudo="):
                    return line.split("=", 1)[1].strip()
        except Exception as e:
            logger.warning(f"Error reading passwords.txt: {e}")
    
    return None


def _save_sudo_password(password: str) -> None:
    """Save sudo password to config file."""
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(_SUDO_CONFIG_PATH, "w") as f:
            json.dump({"sudo_password": password}, f)
    except Exception as e:
        logger.error(f"Failed to save sudo password: {e}")


def _run_sudo_command(cmd: list) -> subprocess.CompletedProcess:
    """Run command with sudo using stored password."""
    sudo_password = _load_sudo_password()
    logger.info(f"Running sudo command: {' '.join(cmd)} (password loaded: {bool(sudo_password)})")
    if sudo_password:
        full_cmd = ["sudo", "-S"] + cmd
        result = subprocess.run(
            full_cmd,
            input=(sudo_password + "\n").encode(),
            capture_output=True,
            timeout=30,
        )
        logger.info(f"Result: returncode={result.returncode}")
        return result
    else:
        logger.warning("No sudo password loaded - trying sudo without password")
        return subprocess.run(["sudo"] + cmd, capture_output=True, timeout=30)


def _encrypt(text: str) -> str:
    """Simple XOR encryption for stored passwords."""
    key = os.environ.get("WIFI_KEY", settings.WIFI_ENC_KEY)
    key_bytes = key.encode() * ((len(text) // len(key)) + 1)
    encrypted = bytes(a ^ b for a, b in zip(text.encode(), key_bytes[:len(text)]))
    return base64.b64encode(encrypted).decode()


def _decrypt(encrypted: str) -> str:
    """Decrypt XOR-encrypted password."""
    key = os.environ.get("WIFI_KEY", settings.WIFI_ENC_KEY)
    encrypted_bytes = base64.b64decode(encrypted.encode())
    key_bytes = key.encode() * ((len(encrypted_bytes) // len(key)) + 1)
    return bytes(a ^ b for a, b in zip(encrypted_bytes, key_bytes[:len(encrypted_bytes)])).decode()


class WiFiManager:
    """Manages WiFi connectivity for offline/online modes."""

    def __init__(self):
        self._config_path = settings.DATA_DIR / "wifi_config.json"
        self._ssid: Optional[str] = None
        self._password: Optional[str] = None
        self._connected: bool = False
        self._current_ssid: Optional[str] = None
        self._offline_mode: bool = True
        self._load_config()
        self._check_connection_status_on_init()
        self._auto_connect()


    def _auto_connect(self):
        """Auto-connect to saved WiFi network on startup."""
        creds = _load_credentials()
        ssid = creds.get("wifi_ssid")
        password = creds.get("wifi_password")
        auto_connect = creds.get("wifi_auto_connect", False)
        
        if ssid and password and auto_connect and not self._connected:
            networks = self.scan_networks()
            logger.info(f"Available networks: {networks}")
            
            if ssid in networks:
                logger.info(f"Auto-connecting to WiFi: {ssid}")
                self.connect(ssid, password)
            else:
                logger.warning(f"WiFi network '{ssid}' not found - scan results: {networks}")


    def _check_connection_status_on_init(self):
        """Check WiFi connection status on startup."""
        try:
            import subprocess
            sudo_pwd = _load_sudo_password()
            if sudo_pwd:
                result = subprocess.run(
                    ["sudo", "-S", "nmcli", "-t", "-f", "SSID", "device", "wifi", "list", "--connected"],
                    input=sudo_pwd + "\n",
                    capture_output=True,
                    timeout=15,
                )
            else:
                result = subprocess.run(
                    ["sudo", "nmcli", "-t", "-f", "SSID", "device", "wifi", "list", "--connected"],
                    capture_output=True,
                    timeout=15,
                )
            
            if result.returncode == 0:
                output = result.stdout.decode().strip()
                if output and output != "--":
                    self._connected = True
                    self._current_ssid = output
                    self._offline_mode = False
                    logger.info(f"Already connected to WiFi: {self._current_ssid}")
        except Exception as e:
            logger.debug(f"Could not check WiFi status: {e}")

    def _load_config(self) -> None:
        """Load WiFi configuration from file."""
        if self._config_path.exists():
            try:
                with open(self._config_path) as f:
                    config = json.load(f)
                    self._ssid = config.get("ssid")
                    encrypted = config.get("password")
                    if encrypted:
                        self._password = _decrypt(encrypted)
                    else:
                        self._password = None
                    self._offline_mode = config.get("offline_mode", True)
            except Exception as e:
                logger.warning(f"Failed to load WiFi config: {e}")

    def _save_config(self) -> None:
        """Save WiFi configuration to file."""
        try:
            settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
            encrypted_password = _encrypt(self._password) if self._password else None
            with open(self._config_path, "w") as f:
                json.dump({
                    "ssid": self._ssid,
                    "password": encrypted_password,
                    "offline_mode": self._offline_mode,
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save WiFi config: {e}")

    def save_credentials(self, ssid: str, password: str) -> None:
        """Save WiFi credentials."""
        self._ssid = ssid
        self._password = password
        self._save_config()
        logger.info(f"WiFi credentials saved for: {ssid}")

    def has_saved_network(self) -> bool:
        """Check if WiFi credentials are saved."""
        return bool(self._ssid and self._password)

    def set_offline_mode(self, offline: bool) -> None:
        """Set offline mode."""
        self._offline_mode = offline
        self._save_config()
        logger.info(f"Offline mode: {offline}")

    def is_offline_mode(self) -> bool:
        """Check if in offline mode."""
        return self._offline_mode

    def connect(self, ssid: Optional[str] = None, password: Optional[str] = None) -> bool:
        """Connect to WiFi network."""
        import subprocess
        
        target_ssid = ssid or self._ssid
        target_password = password or self._password

        if not target_ssid or not target_password:
            logger.warning("No WiFi credentials provided")
            return False

        logger.info(f"Attempting to connect to WiFi: {target_ssid}")
        
        sudo_pwd = _load_sudo_password()
        logger.info(f"Sudo password loaded: {bool(sudo_pwd)}")
        
        import shlex
        
        if sudo_pwd:
            cmd = f'sudo -S nmcli device wifi connect "{target_ssid}" password "{target_password}"'
            result = subprocess.run(
                cmd,
                shell=True,
                input=(sudo_pwd + "\n").encode(),
                capture_output=True,
                timeout=30,
            )
        else:
            cmd = f'sudo nmcli device wifi connect "{target_ssid}" password "{target_password}"'
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                timeout=30,
            )

        logger.info(f"nmcli result: returncode={result.returncode}")
        if result.returncode != 0:
            logger.info(f"stderr: {result.stderr.decode()}")
            logger.info(f"stdout: {result.stdout.decode()}")

        if result.returncode == 0:
            self._connected = True
            self._current_ssid = target_ssid
            self._offline_mode = False
            self._save_config()
            logger.info(f"Connected to WiFi: {target_ssid}")
            return True
        else:
            error_msg = result.stderr.decode() if result.stderr else result.stdout.decode()
            logger.warning(f"WiFi connection failed: {error_msg}")
            return False

    def disconnect(self) -> None:
        """Disconnect from WiFi."""
        try:
            _run_sudo_command(["nmcli", "device", "disconnect", "wlan0"])
            self._connected = False
            self._current_ssid = None
            logger.info("Disconnected from WiFi")
        except Exception as e:
            logger.error(f"WiFi disconnect error: {e}")

    def get_status(self) -> dict:
        """Get WiFi status - live from system."""
        self._check_live_connection()
        return {
            "connected": self._connected,
            "ssid": self._current_ssid,
            "has_saved": self.has_saved_network(),
            "offline_mode": self._offline_mode,
        }

    def _check_live_connection(self):
        """Check live WiFi connection from system."""
        import subprocess
        try:
            sudo_pwd = _load_sudo_password()
            if sudo_pwd:
                result = subprocess.run(
                    ["sudo", "-S", "nmcli", "-t", "-f", "GENERAL.STATE", "device", "show", "wlan0"],
                    input=sudo_pwd + "\n",
                    capture_output=True,
                    timeout=10,
                )
            else:
                result = subprocess.run(
                    ["sudo", "nmcli", "-t", "-f", "GENERAL.STATE", "device", "show", "wlan0"],
                    capture_output=True,
                    timeout=10,
                )
            
            if result.returncode == 0:
                state = result.stdout.decode().strip()
                if "connected" in state.lower():
                    self._connected = True
                    ssid_result = subprocess.run(
                        ["sudo", "nmcli", "-t", "-f", "IP4.SSID", "device", "show", "wlan0"],
                        capture_output=True,
                        timeout=10,
                    )
                    if ssid_result.returncode == 0:
                        self._current_ssid = ssid_result.stdout.decode().strip() or self._ssid
                    self._offline_mode = False
                else:
                    self._connected = False
        except Exception as e:
            logger.debug(f"Could not check live WiFi: {e}")

    def scan_networks(self) -> list:
        """Scan for available WiFi networks."""
        try:
            result = _run_sudo_command(
                ["nmcli", "-t", "-f", "SSID", "device", "wifi", "list"]
            )
            if result.returncode == 0:
                networks = result.stdout.decode().strip().split("\n")
                unique_networks = sorted(set(n for n in networks if n))
                return unique_networks
        except Exception as e:
            logger.error(f"WiFi scan failed: {e}")
        return []

    def check_connection(self) -> bool:
        """Check if currently connected to WiFi."""
        try:
            result = _run_sudo_command(
                ["nmcli", "-t", "-f", "STATE", "device", "show", "wlan0"]
            )
            if result.returncode == 0:
                state = result.stdout.decode().strip()
                if "connected" in state.lower():
                    self._connected = True
                    return True
        except Exception:
            pass
        self._connected = False
        return False

    def get_ip_address(self) -> Optional[str]:
        """Get IP address of WiFi interface."""
        try:
            result = _run_sudo_command(
                ["nmcli", "-t", "-f", "IP4.ADDRESS", "device", "show", "wlan0"]
            )
            if result.returncode == 0:
                output = result.stdout.decode().strip()
                if output:
                    ip = output.split("/")[0] if "/" in output else output
                    return ip
        except Exception:
            pass
        return None


_wifi_manager_instance: Optional[WiFiManager] = None


def get_wifi_manager() -> WiFiManager:
    """Get global WiFi manager instance."""
    global _wifi_manager_instance
    if _wifi_manager_instance is None:
        _wifi_manager_instance = WiFiManager()
    return _wifi_manager_instance