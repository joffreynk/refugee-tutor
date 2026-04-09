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

    @classmethod
    def get_instance(cls) -> "BluetoothManager":
        """Get singleton instance."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    @property
    def state(self) -> BluetoothState:
        """Get current Bluetooth state."""
        return self._state

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
            logger.warning("bleak library not installed - using simulated devices")
            self._state = BluetoothState.DISCONNECTED
            self._discovered_devices = {
                "00:11:22:33:44:55": BluetoothDevice("BAS-102A", "00:11:22:33:44:55", -45, False),
                "AA:BB:CC:DD:EE:FF": BluetoothDevice("BT-Speaker-001", "AA:BB:CC:DD:EE:FF", -60, False),
                "11:22:33:44:55:66": BluetoothDevice("Bluetooth-Headset", "11:22:33:44:55:66", -70, False),
            }
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