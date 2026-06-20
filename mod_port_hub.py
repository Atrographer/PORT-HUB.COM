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

# ====================== FILE-AWARE AUTO-HUBBING ======================
    def auto_hub_files(self, root_dir: str = ".", extensions: Optional[List[str]] = None):
        """
        Discover and register specific project files as ports.
        Perfect for Vite + React + Render stacks — works without reinstalling packages.
        """
        import glob
        from pathlib import Path

        if extensions is None:
            extensions = [
                ".py", ".jsx", ".tsx", ".vue", ".svelte",
                ".js", ".ts", ".html", ".json",
                "vite.config.*"
            ]

        discovered = 0
        root = Path(root_dir).resolve()

        for ext in extensions:
            pattern = str(root / "**" / f"*{ext}" if not ext.startswith(".") else f"**/*{ext}")
            for file_path in glob.glob(pattern, recursive=True):
                if any(ignore in file_path for ignore in ["node_modules", "__pycache__", ".git", "dist", "build"]):
                    continue

                rel_path = os.path.relpath(file_path, root)
                # Create clean port name
                port_name = rel_path.replace("/", "-").replace("\\", "-").replace(".", "-").lower()

                # Infer port type
                port_type_id = self._infer_port_type_from_file(file_path)

                # Create a simple file wrapper port
                file_port = FilePortWrapper(file_path)  # defined below

                self.register_port(port_name, file_port, port_type_id)
                discovered += 1

        # Auto-connect common compatible groups
        self._auto_connect_compatible()

        log.info(f" File auto-hub completed. Hubb'ed {discovered} files from {root_dir}")
        return discovered

    def _infer_port_type_from_file(self, filepath: str) -> Optional[str]:
        """Intelligent type inference based on filename and extension"""
        name = filepath.lower()
        if "vite.config" in name:
            return "vite:config"
        elif any(x in name for x in [".jsx", ".tsx"]):
            return "react:component"
        elif "render" in name or "deployment" in name:
            return "render:service"
        elif name.endswith(".py") and ("api" in name or "app" in name):
            return "web:api"
        elif name.endswith(".html"):
            return "web:static"
        elif name.endswith((".js", ".ts")):
            return "vite:module"
        return None

    def _auto_connect_compatible(self):
        """Automatically bridge common stacks (Vite ↔ React ↔ Render)"""
        vite_ports = [n for n in self.ports if n.startswith("vite")]
        react_ports = [n for n in self.ports if "react" in n]
        render_ports = [n for n in self.ports if "render" in n]

        for v in vite_ports:
            for r in react_ports:
                self.connect(v, r, bidirectional=True)
            for ren in render_ports:
                self.connect(v, ren, bidirectional=True)

        log.info(f"Auto-connected compatible groups: {len(vite_ports)} vite, {len(react_ports)} react, {len(render_ports)} render ports")


# Simple File Wrapper (add this class near the top, after imports)
class FilePortWrapper:
    """Lightweight wrapper for file-based ports"""
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.name = os.path.basename(file_path)

    def read(self) -> str:
        """Read file content"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            log.error(f"Failed to read {self.file_path}: {e}")
            return ""

    def __repr__(self):
        return f"FilePort({self.name})"

    # You can extend this with more methods (write, process, etc.) 

# ====================== GLOBAL HUB ======================
PortHub = ModPortHub()

# Auto run discovery when imported (light version)
if __name__ == "__main__":
    PortHub.auto_discover()
    PortHub.status()
