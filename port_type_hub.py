import os
import glob
from pathlib import Path
from typing import Dict, Any, Callable, Optional, Set, List, Collection
import importlib
import logging
import sys
import inspect
import threading
from functools import partial

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("PortHub")


# ========================== ADAPTABLY APPLICABLE PORT TYPE ==========================
class PortType:
    """
    Adaptably Applicable Typed Port Definition with Registry.
    Supports dynamic metadata and future extensibility.
    """

    _registry: Dict[str, "PortType"] = {}
    _lock = threading.Lock()

    def __init__(self, 
                 id: str, 
                 category: str, 
                 description: str,
                 **metadata: Any):
        self._id = id.lower().strip()
        self._category = category.upper().strip()
        self._description = description
        self._metadata: Dict[str, Any] = metadata or {}

    @property
    def id(self) -> str:
        return self._id

    @property
    def category(self) -> str:
        return self._category

    @property
    def description(self) -> str:
        return self._description

    @property
    def metadata(self) -> Dict[str, Any]:
        return self._metadata.copy()

    def get_meta(self, key: str, default: Any = None) -> Any:
        return self._metadata.get(key, default)

    @classmethod
    def register(cls, id: str, category: str, description: str, **metadata: Any) -> "PortType":
        with cls._lock:
            port_type = cls(id, category, description, **metadata)
            cls._registry[port_type.id] = port_type
            log.info(f"Registered Adaptable PortType: {port_type.id} [{port_type.category}]")
            return port_type

    @classmethod
    def get(cls, id: str) -> Optional["PortType"]:
        with cls._lock:
            return cls._registry.get(id.lower().strip())

    @classmethod
    def get_all(cls) -> Collection["PortType"]:
        with cls._lock:
            return list(cls._registry.values())

    def __repr__(self) -> str:
        return f"PortType({self.id}, {self.category})"

class FilePortWrapper:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.name = os.path.basename(file_path)

    def read(self) -> str:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            log.error(f"Failed to read {self.file_path}: {e}")
            return ""

    def __repr__(self):
        return f"FilePort({self.name})" 
        
class DefaultPortTypes:
    @staticmethod
    def register_all() -> None:
        # === BUILD TOOLS & FRAMEWORKS ===
        PortType.register("vite:config", "BUILD", "Vite Configuration (vite.config.js/ts)")
        PortType.register("vite:devserver", "BUILD", "Vite Development Server", adapter="vite")
        PortType.register("vite:build", "BUILD", "Vite Production Build Output", adapter="vite")
        PortType.register("vite:asset", "BUILD", "Vite Asset (processed by Vite)", adapter="vite")
        PortType.register("vite:module", "BUILD", "Vite Module Federation / Async Chunk", adapter="vite")

        PortType.register("react:component", "FRAMEWORK", "React Component", framework="react")
        PortType.register("vue:component", "FRAMEWORK", "Vue Component", framework="vue")
        PortType.register("svelte:component", "FRAMEWORK", "Svelte Component", framework="svelte")

        # === RENDERING ===
        PortType.register("ssr:render", "RENDER", "Server-Side Rendering Output", rendering="ssr")
        PortType.register("csr:render", "RENDER", "Client-Side Rendering", rendering="csr")
        PortType.register("render:static", "RENDER", "Static Site Generation (SSG)", rendering="static")
        PortType.register("render:stream", "RENDER", "Streaming SSR", rendering="stream")

        # === Render.com Platform ===
        PortType.register("render:service", "RENDER", "Render.com Service", platform="render")
        PortType.register("render:deployment", "RENDER", "Render.com Deployment", platform="render")
        PortType.register("render:env", "RENDER", "Render.com Environment Variables", platform="render")
        PortType.register("render:preview", "RENDER", "Render.com Preview Environment", platform="render")
        PortType.register("render:customdomain", "RENDER", "Render.com Custom Domain", platform="render")

        # === GitHub ===
        PortType.register("github:repo", "GITHUB", "GitHub Repository", platform="github")
        PortType.register("github:pr", "GITHUB", "GitHub Pull Request", platform="github")
        PortType.register("github:workflow", "GITHUB", "GitHub Actions Workflow", platform="github")
        PortType.register("github:artifact", "GITHUB", "GitHub Artifact", platform="github")
        PortType.register("github:release", "GITHUB", "GitHub Release", platform="github")

        # === WEB / DEPLOYMENT ===
        PortType.register("http:response", "WEB", "HTTP Response")
        PortType.register("web:static", "WEB", "Static Assets (HTML, CSS, JS)")
        PortType.register("web:api", "WEB", "Backend API Endpoint")
        PortType.register("code:split", "BUILD", "Code-Split Chunk")
        PortType.register("async:load", "BUILD", "Asynchronously Loaded Module")

        # === DATA & CONFIG ===
        PortType.register("json:config", "DATA", "JSON Configuration")
        PortType.register("env:vars", "CONFIG", "Environment Variables")
        PortType.register("docker:image", "DEPLOY", "Docker Image Reference")


# ========================== UNIVERSAL PORT HUB ==========================
class ModPortHub:
    def __init__(self):
        self.ports: Dict[str, Any] = {}
        self.port_types: Dict[str, PortType] = {}
        self.filters: Dict[str, Callable] = {}
        self.connections: Set[tuple[str, str]] = set()

        DefaultPortTypes.register_all()

    # ====================== CORE PORT MANAGEMENT ======================
    def register_port(self, name: str, instance: Any, port_type_id: Optional[str] = None) -> None:
        name = name.lower().strip()
        if name in self.ports:
            log.warning(f"Port '{name}' already exists. Overwriting.")

        self.ports[name] = instance

        if port_type_id:
            ptype = PortType.get(port_type_id)
            if ptype:
                self.port_types[name] = ptype
                log.info(f"Registered typed port: {name} → {type(instance).__name__} [{ptype.category}]")
            else:
                log.warning(f"PortType '{port_type_id}' not found for port '{name}'")
        else:
            log.info(f"Registered port: {name} → {type(instance).__name__}")

    def get_port(self, name: str) -> Any:
        port = self.ports.get(name.lower().strip())
        if port is None:
            log.error(f"Port '{name}' not found!")
        return port

    def get_port_type(self, name: str) -> Optional[PortType]:
        return self.port_types.get(name.lower().strip())

    def has_port(self, name: str) -> bool:
        return name.lower().strip() in self.ports

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
        source = source.lower().strip()
        target = target.lower().strip()

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

    # ====================== ENHANCED AUTO DISCOVERY ======================
    def auto_discover(self, 
                      package_names: Optional[List[str]] = None,
                      name_patterns: Optional[List[str]] = None,
                      exclude: Optional[List[str]] = None):
        if exclude is None:
            exclude = ["mod_port_hub", "__pycache__", "test", "tests", "old", "legacy"]

        if name_patterns is None:
            name_patterns = [
                "vite", "render", "github", "weaver", "engine", "vector", "tensor",
                "style", "dynamic", "active", "maxp", "operator", "model", "deploy",
                "ssr", "csr", "workflow", "action", "component"
            ]

        discovered = 0
        search_locations = package_names or list(sys.modules.keys())

        type_mapping = {
            "vite": "vite:build",
            "viteconfig": "vite:config",
            "devserver": "vite:devserver",
            "react": "react:component",
            "vue": "vue:component",
            "svelte": "svelte:component",
            "render": "render:service",
            "deployment": "render:deployment",
            "preview": "render:preview",
            "customdomain": "render:customdomain",
            "github": "github:repo",
            "repo": "github:repo",
            "pr": "github:pr",
            "pullrequest": "github:pr",
            "workflow": "github:workflow",
            "action": "github:workflow",
            "artifact": "github:artifact",
            "release": "github:release",
            "ssr": "ssr:render",
            "csr": "csr:render",
            "static": "render:static",
            "stream": "render:stream",
            "docker": "docker:image",
            "env": "env:vars",
            "config": "json:config",
        }

        for module_name in search_locations:
            m_lower = module_name.lower()

            if any(ex in m_lower for ex in exclude):
                continue
            if not any(pat in m_lower for pat in name_patterns):
                continue

            try:
                if module_name not in sys.modules:
                    module = importlib.import_module(module_name)
                else:
                    module = sys.modules[module_name]

                port_name = module_name.replace("_", "-").replace(".", "-").lower()

                # Intelligent Port Type Detection
                assigned_type = None
                for keyword, ptype_id in type_mapping.items():
                    if keyword in m_lower:
                        assigned_type = ptype_id
                        break

                # Special multi-keyword rules
                if "vite" in m_lower and "config" in m_lower:
                    assigned_type = "vite:config"
                elif "github" in m_lower and ("action" in m_lower or "workflow" in m_lower):
                    assigned_type = "github:workflow"
                elif "render" in m_lower and "deploy" in m_lower:
                    assigned_type = "render:deployment"

                # Try to instantiate main class
                main_instance = None
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if inspect.isclass(attr) and not attr_name.startswith("_"):
                        if any(k in attr_name.lower() for k in ["engine", "weaver", "manager", "client", "app", "model"]):
                            try:
                                main_instance = attr()
                                break
                            except Exception:
                                continue

                if main_instance:
                    self.register_port(port_name, main_instance, assigned_type)
                else:
                    self.register_port(port_name, module, assigned_type)

                discovered += 1
                log.info(f"Auto-discovered: {port_name} → {assigned_type or 'untyped'}")

            except Exception as e:
                log.debug(f"Skipped {module_name}: {e}")

        log.info(f"Auto-discovery completed. Found {discovered} new ports.")
        return discovered

    # ====================== UTILITIES ======================
    def list_ports(self) -> List[str]:
        return list(self.ports.keys())

    def list_typed_ports(self) -> Dict[str, PortType]:
        return self.port_types.copy()

    def list_filters(self) -> List[str]:
        return list(self.filters.keys())

    def status(self):
        print("\n=== ModPortHub Status ===")
        print(f"Registered Ports     : {len(self.ports)}")
        print(f"Typed Ports          : {len(self.port_types)}")
        print(f"Available Filters    : {len(self.filters)}")
        print(f"Active Connections   : {len(self.connections)}")
        print(f"Available PortTypes  : {len(PortType.get_all())}")

# ====================== FILE-AWARE AUTO-HUBBING ======================
    def auto_hub_files(self, root_dir: str = ".", extensions: Optional[List[str]] = None):
        """
        Discover and register specific project files as ports.
        Perfect for Vite + React + Render stacks — works without reinstalling packages.
        """
        
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

# ====================== GLOBAL INSTANCE ======================
PortHub = ModPortHub()

# Optional auto-discovery when run directly
if __name__ == "__main__":
    PortHub.auto_discover()
    PortHub.status()
