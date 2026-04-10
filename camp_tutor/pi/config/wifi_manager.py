"""WiFi management module for offline/online connectivity."""

import json
import logging
import subprocess
from pathlib import Path
from typing import Optional

from config import settings

logger = logging.getLogger(__name__)


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

    def _load_config(self) -> None:
        """Load WiFi configuration from file."""
        if self._config_path.exists():
            try:
                with open(self._config_path) as f:
                    config = json.load(f)
                    self._ssid = config.get("ssid")
                    self._password = config.get("password")
                    self._offline_mode = config.get("offline_mode", True)
            except Exception as e:
                logger.warning(f"Failed to load WiFi config: {e}")

    def _save_config(self) -> None:
        """Save WiFi configuration to file."""
        try:
            settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
            with open(self._config_path, "w") as f:
                json.dump({
                    "ssid": self._ssid,
                    "password": self._password,
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
        target_ssid = ssid or self._ssid
        target_password = password or self._password

        if not target_ssid or not target_password:
            logger.warning("No WiFi credentials provided")
            return False

        try:
            result = subprocess.run(
                ["nmcli", "device", "wifi", "connect", target_ssid, "password", target_password],
                capture_output=True,
                timeout=30,
            )

            if result.returncode == 0:
                self._connected = True
                self._current_ssid = target_ssid
                self._offline_mode = False
                self._save_config()
                logger.info(f"Connected to WiFi: {target_ssid}")
                return True
            else:
                logger.warning(f"WiFi connection failed: {result.stderr.decode()}")
                return False

        except FileNotFoundError:
            logger.warning("nmcli not available - using NetworkManager")
            return self._connect_alternative(target_ssid, target_password)
        except Exception as e:
            logger.error(f"WiFi connection error: {e}")
            return False

    def _connect_alternative(self, ssid: str, password: str) -> bool:
        """Alternative WiFi connection using ifconfig/wpa_supplicant."""
        try:
            subprocess.run(["ip", "link", "set", "wlan0", "up"], check=True)
            result = subprocess.run(
                ["wpa_passphrase", ssid, password],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if result.returncode == 0:
                logger.info("WiFi setup attempted (manual configuration needed)")
            return False
        except Exception as e:
            logger.error(f"Alternative WiFi connection failed: {e}")
            return False

    def disconnect(self) -> None:
        """Disconnect from WiFi."""
        try:
            subprocess.run(["nmcli", "device", "disconnect", "wlan0"], capture_output=True)
            self._connected = False
            self._current_ssid = None
            logger.info("Disconnected from WiFi")
        except Exception as e:
            logger.error(f"WiFi disconnect error: {e}")

    def get_status(self) -> dict:
        """Get WiFi status."""
        return {
            "connected": self._connected,
            "ssid": self._current_ssid,
            "has_saved": self.has_saved_network(),
            "offline_mode": self._offline_mode,
        }

    def scan_networks(self) -> list:
        """Scan for available WiFi networks."""
        try:
            result = subprocess.run(
                ["nmcli", "-t", "-f", "SSID", "device", "wifi", "list"],
                capture_output=True,
                timeout=15,
            )
            if result.returncode == 0:
                networks = result.stdout.decode().strip().split("\n")
                return [n for n in networks if n]
        except Exception as e:
            logger.error(f"WiFi scan failed: {e}")
        return []

    def check_connection(self) -> bool:
        """Check if currently connected to WiFi."""
        try:
            result = subprocess.run(
                ["nmcli", "-t", "-f", "STATE", "device", "show", "wlan0"],
                capture_output=True,
                timeout=10,
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
            result = subprocess.run(
                ["nmcli", "-t", "-f", "IP4.ADDRESS", "device", "show", "wlan0"],
                capture_output=True,
                timeout=10,
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