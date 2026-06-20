"""
PORT-HUB.COM
Thee Port Hub — Dynamic Port/Adapter/Hub System for Python Projects

Treat modules, classes, objects, and project files (especially Vite + React + Render.com)
as first-class, typed, and interconnectable ports.

**Structure:**
- core_port_hub.py : Minimal core version (lightweight, no PortType system)
- port_type_hub.py : Advanced typed version (recommended)
"""

import logging
from typing import Any, Optional

# Primarily expose the advanced typed version
from .port_type_hub import (
    PortType,
    FilePortWrapper,
    DefaultPortTypes,
    ModPortHub,
    PortHub,
)

# Convenience re-exports from advanced hub
__all__ = [
    "PortHub",
    "PortType",
    "FilePortWrapper",
    "DefaultPortTypes",
    "ModPortHub",
    "register_port",
    "get_port",
    "auto_discover",
    "auto_hub_files",
    "connect",
    "status",
    # Legacy core access
    "core_port_hub",
]

# ====================== PUBLIC API (delegates to advanced) ======================

def register_port(name: str, instance: Any, port_type_id: Optional[str] = None) -> None:
    """Register any object as a port in the global hub."""
    PortHub.register_port(name, instance, port_type_id)

def get_port(name: str) -> Any:
    """Retrieve a registered port by name."""
    return PortHub.get_port(name)

def auto_discover(**kwargs) -> int:
    """Auto-discover modules and register them as ports."""
    return PortHub.auto_discover(**kwargs)

def auto_hub_files(root_dir: str = ".", **kwargs) -> int:
    """Auto-hub project files (Vite, React, HTML, etc.) as lazy ports."""
    return PortHub.auto_hub_files(root_dir, **kwargs)

def connect(source: str, target: str, bidirectional: bool = True, **kwargs) -> bool:
    """Connect two ports with dynamic method bridging."""
    return PortHub.connect(source, target, bidirectional=bidirectional, **kwargs)

def status() -> None:
    """Print current status of the PortHub."""
    PortHub.status()

def list_ports() -> list:
    """List all registered port names."""
    return PortHub.list_ports()

# Optional: Import core for legacy/minimal use
try:
    from .core_port_hub import ModPortHub as CoreModPortHub
    core_port_hub = CoreModPortHub()  # minimal instance
except ImportError:
    core_port_hub = None

# Auto-register default port types
DefaultPortTypes.register_all()

log = logging.getLogger("PortHub")
log.info("PORT-HUB.COM initialized. Advanced PortHub ready. Core available as core_port_hub.")
 
