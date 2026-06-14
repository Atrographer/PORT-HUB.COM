"""
mod_port_hub.py
Universal Porting Hub — Generalized & Adaptive
"""

from typing import Dict, Any, Callable, Optional, Set, List
import importlib
import logging
import pkgutil
import sys
from functools import partial

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("PortHub")


class ModPortHub:
    def __init__(self):
        self.ports: Dict[str, Any] = {}
        self.filters: Dict[str, Callable] = {}
        self.connections: Set[tuple[str, str]] = set()

    # ====================== CORE PORT MANAGEMENT ======================
    def register_port(self, name: str, instance: Any) -> None:
        """Register any object as a port"""
        if name in self.ports:
            log.warning(f"Port '{name}' already exists. Overwriting.")
        
        self.ports[name] = instance
        log.info(f"Registered port: {name} → {type(instance).__name__}")

    def get_port(self, name: str) -> Any:
        port = self.ports.get(name)
        if port is None:
            log.error(f"Port '{name}' not found!")
        return port

    def has_port(self, name: str) -> bool:
        return name in self.ports

    # ====================== MODFILTER SYSTEM ======================
    def add_filter(self, name: str, func: Callable) -> None:
        self.filters[name] = func
        log.info(f"Added modfilter: {name}")

    def apply_filter(self, filter_name: str, data: Any, **kwargs) -> Any:
        if filter_name not in self.filters:
            log.warning(f"Filter '{filter_name}' not found.")
            return data
        return self.filters[filter_name](data, **kwargs)

    # ====================== CONNECTIONS ======================
    def connect(self, source: str, target: str, 
                method_map: Optional[Dict[str, str]] = None,
                bidirectional: bool = True):
        """Create bridge between ports"""
        if not self.has_port(source) or not self.has_port(target):
            log.error(f"Cannot connect {source} <-> {target} (missing port)")
            return False

        self.connections.add((source, target))
        if bidirectional:
            self.connections.add((target, source))

        src_obj = self.get_port(source)
        tgt_obj = self.get_port(target)

        common_methods = ["generate", "compute", "process", "next", "weave", 
                         "refine", "transform", "forward", "__call__", "run", "step"]

        for method in common_methods:
            if hasattr(tgt_obj, method):
                setattr(src_obj, f"to_{target}_{method}", 
                        partial(getattr(tgt_obj, method)))
            
            if bidirectional and hasattr(src_obj, method):
                setattr(tgt_obj, f"to_{source}_{method}", 
                        partial(getattr(src_obj, method)))

        log.info(f"Connected {source} <{'<->' if bidirectional else '->'} {target}")
        return True

    # ====================== GENERALIZED AUTO DISCOVERY ======================
    def auto_discover(self, 
                      package_names: Optional[List[str]] = None,
                      name_patterns: Optional[List[str]] = None,
                      exclude: Optional[List[str]] = None):
        """
        Generalized adaptive discovery.
        Scans installed modules and attempts to register them intelligently.
        """
        if exclude is None:
            exclude = ["mod_port_hub", "__pycache__", "test", "tests", "old"]

        if name_patterns is None:
            name_patterns = ["weaver", "engine", "vector", "tensor", "style", 
                           "dynamic", "active", "maxp", "operator", "model"]

        discovered = 0

        # 1. Scan specified packages or sys.modules
        search_locations = package_names or list(sys.modules.keys())

        for module_name in search_locations:
            if any(ex in module_name for ex in exclude):
                continue

            # Check if module name matches any pattern
            if not any(pat.lower() in module_name.lower() for pat in name_patterns):
                continue

            try:
                # Import if not already loaded
                if module_name not in sys.modules:
                    module = importlib.import_module(module_name)
                else:
                    module = sys.modules[module_name]

                # Try to find main class or use module itself
                port_name = module_name.replace("_", "-").replace(".", "-")

                # Priority: Look for classes with common naming patterns
                main_instance = None
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if inspect.isclass(attr) and not attr_name.startswith("_"):
                        # Heuristic: likely main class
                        if any(k in attr_name.lower() for k in ["engine", "weaver", "vector", "tensor", "operator", "model"]):
                            try:
                                main_instance = attr()
                                break
                            except Exception:
                                continue

                if main_instance:
                    self.register_port(port_name, main_instance)
                else:
                    # Fallback: register the module itself
                    self.register_port(port_name, module)
                
                discovered += 1

            except Exception as e:
                log.debug(f"Skipped {module_name}: {e}")

        log.info(f"Auto-discovery completed. Found {discovered} new ports.")
        return discovered

    # ====================== UTILITIES ======================
    def list_ports(self) -> List[str]:
        return list(self.ports.keys())

    def list_filters(self) -> List[str]:
        return list(self.filters.keys())

    def status(self):
        print("\n=== ModPortHub Status ===")
        print(f"Registered Ports : {len(self.ports)} → {list(self.ports.keys())}")
        print(f"Available Filters: {len(self.filters)} → {list(self.filters.keys())}")
        print(f"Active Connections: {len(self.connections)}")


# ====================== GLOBAL HUB ======================
PortHub = ModPortHub()

# Auto run discovery when imported (light version)
if __name__ == "__main__":
    PortHub.auto_discover()
    PortHub.status()
