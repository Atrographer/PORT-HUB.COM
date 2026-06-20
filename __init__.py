"""
PORT-HUB.COM
Thee Port Hub — Dynamic Port/Adapter/Hub System for Python Projects

Treat modules, classes, objects, and project files (especially Vite + React + Render.com)
as first-class, typed, and interconnectable ports.
"""

import logging
from typing import Any, Optional

# Import core components from the main implementation
from .port_type_hub import (
    PortType,
    FilePortWrapper,
    DefaultPortTypes,
    ModPortHub,
)

# Create and expose the global singleton hub (recommended entry point)
PortHub = ModPortHub()

# Convenience re-exports
__all__ = [
    "PortHub",
    "PortType",
    "FilePortWrapper",
    "DefaultPortTypes",
    "ModPortHub",
    # Main public functions
    "register_port",
    "get_port",
    "auto_discover",
    "auto_hub_files",
    "connect",
    "status",
]

# ====================== PUBLIC API ======================

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


# Auto-register default port types on import
DefaultPortTypes.register_all()

# Optional: Light auto-discovery when the package is imported
# (disabled by default to avoid side effects)
# if __name__ == "__main__":
#     auto_discover()
#     auto_hub_files(".")
#     status()

log = logging.getLogger("PortHub")
log.info("PORT-HUB.COM initialized successfully. Use PortHub or
