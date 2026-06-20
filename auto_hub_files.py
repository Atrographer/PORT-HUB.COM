"""
PORT-HUB.COM - File-Aware Auto-Hubbing Extension
This file acts as a separate, optional extension/port.
"""

import glob
import os
from pathlib import Path
from typing import Optional, List

from port_type_hub import ModPortHub, FilePortWrapper, PortHub, log


class FileHubExtension:
    """Extension that adds file-aware auto-hubbing capability to the PortHub."""

    def __init__(self):
        self.name = "file-hub-extension"
        self.port_type_id = "hub:extension:file"

    def register(self):
        """Register this extension as a port and add methods to the main hub."""
        PortHub.register_port(self.name, self, self.port_type_id)

        # Dynamically attach the auto_hub_files method to the main hub
        if not hasattr(PortHub, 'auto_hub_files'):
            PortHub.auto_hub_files = self.auto_hub_files
            PortHub._infer_port_type_from_file = self._infer_port_type_from_file
            PortHub._auto_connect_compatible = self._auto_connect_compatible

        log.info("FileHubExtension registered as port and methods attached.")

    def auto_hub_files(self, root_dir: str = ".", extensions: Optional[List[str]] = None):
        """
        Discover and register specific project files as ports.
        Ideal for Vite + React + Render stacks.
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
            pattern = str(root / "**" / f"*{ext}" if "*" not in ext else f"**/{ext}")
            for file_path in glob.glob(pattern, recursive=True):
                if any(ignore in file_path for ignore in ["node_modules", "__pycache__", ".git", "dist", "build"]):
                    continue

                rel_path = os.path.relpath(file_path, root)
                port_name = rel_path.replace(os.sep, "-").replace(".", "-").lower()

                port_type_id = self._infer_port_type_from_file(file_path)

                file_port = FilePortWrapper(file_path)
                PortHub.register_port(port_name, file_port, port_type_id)
                discovered += 1

        self._auto_connect_compatible()
        log.info(f"File auto-hub completed. Hubb'ed {discovered} files from {root_dir}")
        return discovered

    def _infer_port_type_from_file(self, filepath: str) -> Optional[str]:
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
        vite_ports = [n for n in PortHub.ports if n.startswith("vite")]
        react_ports = [n for n in PortHub.ports if "react" in n]
        render_ports = [n for n in PortHub.ports if "render" in n]

        for v in vite_ports:
            for r in react_ports:
                PortHub.connect(v, r, bidirectional=True)
            for ren in render_ports:
                PortHub.connect(v, ren, bidirectional=True)

        log.info(f"Auto-connected: {len(vite_ports)} vite, {len(react_ports)} react, {len(render_ports)} render ports")


# Auto-register the extension when this module is imported
if __name__ != "__main__":
    extension = FileHubExtension()
    extension.register() 
