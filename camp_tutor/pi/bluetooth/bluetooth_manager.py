"""Bluetooth manager for Camp Tutor robot."""

import logging
import asyncio
import threading
from typing import List, Optional, Dict, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class BluetoothState(Enum):
    """Bluetooth connection state."""
    DISCONNECTED = "disconnected"
    SCANNING = "scanning"
    CONNECTED = "connected"
    CONNECTING = "connecting"
    ERROR = "error"


@dataclass
class BluetoothDevice:
    """Represents a discovered Bluetooth device."""
    name: str
    address: str
    rssi: int = 0
    connected: bool = False


class BluetoothManager:
    """Manages Bluetooth scanning and connection."""

    _instance: Optional["BluetoothManager"] = None
    _lock = threading.Lock()

    def __init__(self):
        self._state = BluetoothState.DISCONNECTED
        self._connected_device: Optional[BluetoothDevice] = None
        self._discovered_devices: Dict[str, BluetoothDevice] = {}
        self._scan_callback: Optional[Callable] = None
        self._connected_callback: Optional[Callable] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._bleak_scanner = None
        self._auto_connect_saved()


    def _auto_connect_saved(self):
        """Auto-connect to saved Bluetooth devices by scanning for name."""
        from pathlib import Path
        from config.wifi_manager import _load_credentials
        
        creds = _load_credentials()
        bt_devices = creds.get("bluetooth_devices", {})
        
        if not bt_devices:
            return
        
        device_name = None
        device_address = None
        
        for address, device_info in bt_devices.items():
            device_name = device_info.get("name", "")
        
        if not device_name:
            return
        
        logger.info(f"Searching for Bluetooth device: {device_name}")
        
        try:
            import subprocess
            
            result = subprocess.run(
                ["sudo", "bluetoothctl", "devices"],
                capture_output=True,
                timeout=10,
            )
            
            if result.returncode == 0:
                devices_output = result.stdout.decode()
                for line in devices_output.split("\n"):
                    if device_name in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            device_address = parts[1]
                            logger.info(f"Found device address: {device_address}")
                            break
            
            if not device_address:
                logger.info(f"Device {device_name} not paired - scanning...")
                result = subprocess.run(
                    ["sudo", "bluetoothctl", "scan", "on"],
                    capture_output=True,
                    timeout=30,
                )
                return
            
            result = subprocess.run(
                ["sudo", "bluetoothctl", "trust", device_address],
                capture_output=True,
                timeout=10,
            )
            result = subprocess.run(
                ["sudo", "bluetoothctl", "pair", device_address],
                capture_output=True,
                timeout=30,
            )
            result = subprocess.run(
                ["sudo", "bluetoothctl", "connect", device_address],
                capture_output=True,
                timeout=15,
            )
            
            if result.returncode == 0:
                logger.info(f"Connected to {device_name}")
                self._connected_device = BluetoothDevice(
                    name=device_name,
                    address=device_address,
                    rssi=-50,
                    connected=True,
                )
                self._state = BluetoothState.CONNECTED
            else:
                logger.warning(f"Could not connect to {device_name}: {result.stderr.decode()}")
                
        except Exception as e:
            logger.warning(f"Bluetooth auto-connect error: {e}")

    @classmethod
    def get_instance(cls) -> "BluetoothManager":
        """Get singleton instance."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    @property
    def state(self) -> BluetoothState:
        """Get current Bluetooth state - live from system."""
        self._check_live_status()
        return self._state

    def _check_live_status(self):
        """Check live Bluetooth status from system."""
        import subprocess
        try:
            result = subprocess.run(
                ["rfkill", "list", "bluetooth"],
                capture_output=True,
                timeout=5,
            )
            if result.returncode == 0:
                output = result.stdout.decode().lower()
                if "soft blocked: yes" in output:
                    self._state = BluetoothState.DISCONNECTED
                elif "hard blocked: yes" in output:
                    self._state = BluetoothState.ERROR
                else:
                    self._state = BluetoothState.DISCONNECTED
            else:
                self._state = BluetoothState.ERROR
        except Exception:
            self._state = BluetoothState.DISCONNECTED

    @property
    def connected_device(self) -> Optional[BluetoothDevice]:
        """Get currently connected device."""
        return self._connected_device

    @property
    def discovered_devices(self) -> List[BluetoothDevice]:
        """Get list of discovered devices."""
        return list(self._discovered_devices.values())

    def _ensure_event_loop(self):
        """Ensure event loop is running in background thread."""
        if self._loop is None:
            self._loop = asyncio.new_event_loop()
            self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
            self._thread.start()
            logger.info("Bluetooth event loop started")

    async def _scan_async(self, duration: int = 10):
        """Scan for BLE devices asynchronously."""
        try:
            from bleak import BleakScanner
            self._bleak_scanner = BleakScanner()
            self._state = BluetoothState.SCANNING
            logger.info(f"Starting BLE scan for {duration} seconds...")

            devices = await self._bleak_scanner.discover(timeout=duration)
            self._discovered_devices.clear()

            for device in devices:
                if device.name:
                    self._discovered_devices[device.address] = BluetoothDevice(
                        name=device.name or "Unknown",
                        address=device.address,
                        rssi=device.rssi or 0,
                    )
                    logger.info(f"Found: {device.name} ({device.address})")

            self._state = BluetoothState.DISCONNECTED
            
            if self._scan_callback:
                self._scan_callback(self.discovered_devices)

        except ImportError:
            logger.warning("bleak library not installed - cannot scan real Bluetooth devices")
            self._state = BluetoothState.ERROR
            self._discovered_devices = {}
            if self._scan_callback:
                self._scan_callback(self.discovered_devices)

        except Exception as e:
            logger.error(f"BLE scan error: {e}")
            self._state = BluetoothState.ERROR

    def scan(self, duration: int = 10) -> List[BluetoothDevice]:
        """Scan for available Bluetooth devices."""
        self._ensure_event_loop()
        
        def run_scan():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self._scan_async(duration))
                loop.close()
            except Exception as e:
                logger.error(f"Scan error: {e}")
        
        thread = threading.Thread(target=run_scan, daemon=True)
        thread.start()
        thread.join(timeout=duration + 5)
        
        return self.discovered_devices

    def list_devices(self) -> List[BluetoothDevice]:
        """List all known Bluetooth devices (paired and scanned)."""
        devices = []
        
        # Try bluetoothctl first
        try:
            import subprocess
            result = subprocess.run(
                ["sudo", "bluetoothctl", "devices"],
                capture_output=True,
                timeout=10,
            )
            
            if result.returncode == 0:
                for line in result.stdout.decode().split("\n"):
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 3:
                            address = parts[1]
                            name = " ".join(parts[2:])
                            devices.append(BluetoothDevice(
                                name=name,
                                address=address,
                                rssi=-60,
                            ))
        except Exception as e:
            logger.warning(f"bluetoothctl failed: {e}")
        
        # Also add discovered devices from scanning
        for addr, device in self._discovered_devices.items():
            if not any(d.address == addr for d in devices):
                devices.append(device)
        
        return devices

    async def _connect_async(self, address: str):
        """Connect to device asynchronously."""
        try:
            from bleak import BleakClient
            self._state = BluetoothState.CONNECTING
            logger.info(f"Connecting to {address}...")

            async with BleakClient(address) as client:
                if client.is_connected:
                    device = self._discovered_devices.get(address)
                    if device:
                        device.connected = True
                        self._connected_device = device
                        self._state = BluetoothState.CONNECTED
                        logger.info(f"Connected to {device.name}")
                        
                        if self._connected_callback:
                            self._connected_callback(device)

        except ImportError:
            logger.warning("bleak library not installed - simulating connection")
            device = self._discovered_devices.get(address)
            if device:
                device.connected = True
                self._connected_device = device
                self._state = BluetoothState.CONNECTED
                logger.info(f"Simulated connection to {device.name}")
                
                if self._connected_callback:
                    self._connected_callback(device)

        except Exception as e:
            logger.error(f"Connection error: {e}")
            self._state = BluetoothState.ERROR

    def connect(self, address: str) -> bool:
        """Connect to a Bluetooth device by address."""
        if address not in self._discovered_devices:
            logger.error(f"Device {address} not in discovered devices")
            return False

        def run_connect():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self._connect_async(address))
                loop.close()
            except Exception as e:
                logger.error(f"Connection error: {e}")

        thread = threading.Thread(target=run_connect, daemon=True)
        thread.start()
        thread.join(timeout=10)
        
        return self._state == BluetoothState.CONNECTED

    def disconnect(self) -> bool:
        """Disconnect from current device."""
        if self._connected_device:
            address = self._connected_device.address
            self._connected_device.connected = False
            self._connected_device = None
            self._state = BluetoothState.DISCONNECTED
            logger.info(f"Disconnected from {address}")
            return True
        return False

    def on_scan_result(self, callback: Callable):
        """Register callback for scan results."""
        self._scan_callback = callback

    def on_connected(self, callback: Callable):
        """Register callback for connection events."""
        self._connected_callback = callback

    def get_status(self) -> Dict:
        """Get Bluetooth status."""
        return {
            "state": self._state.value,
            "connected_device": {
                "name": self._connected_device.name,
                "address": self._connected_device.address,
            } if self._connected_device else None,
            "discovered_count": len(self._discovered_devices),
        }


def get_bluetooth_manager() -> BluetoothManager:
    """Get global Bluetooth manager instance."""
    return BluetoothManager.get_instance()