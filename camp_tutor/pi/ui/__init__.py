"""UI module for Camp Tutor."""

from .ui_controls import (
    VolumeControl,
    AgeGroupSelector,
    TimetableDisplay,
    SimpleConsoleUI,
    SystemMonitor,
    DeviceInfo,
    SystemStatus,
    get_volume_control,
    get_age_selector,
    get_timetable_display,
    get_console_ui,
    get_system_monitor,
)

from .diagnostics import (
    SystemDiagnostics,
    DiagnosticResult,
    DiagnosticLevel,
    get_diagnostics,
)

__all__ = [
    # UI Controls
    "VolumeControl",
    "AgeGroupSelector",
    "TimetableDisplay",
    "SimpleConsoleUI",
    "SystemMonitor",
    "DeviceInfo",
    "SystemStatus",
    "get_volume_control",
    "get_age_selector",
    "get_timetable_display",
    "get_console_ui",
    "get_system_monitor",
    # Diagnostics
    "SystemDiagnostics",
    "DiagnosticResult",
    "DiagnosticLevel",
    "get_diagnostics",
]