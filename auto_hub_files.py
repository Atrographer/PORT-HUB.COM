import glob
import os
from pathlib import Path

class ModPortHub:
    # ... existing code ...

    def auto_hub_files(self, root_dir: str = ".", extensions: Optional[List[str]] = None):
        """Discover and hub specific files as ports (React, Vite, Render, .py, .html, .api, etc.)"""
        if extensions is None:
            extensions = [".py", ".jsx", ".tsx", ".vue", ".svelte", 
                         ".js", ".ts", "vite.config.*", ".html", ".json"]

        discovered = 0
        root = Path(root_dir).resolve()

        for ext in extensions:
            for file in glob.glob(str(root / "**" / f"*{ext}"), recursive=True):
                if any(ignore in file for ignore in ["node_modules", "__pycache__", ".git"]):
                    continue

                rel_path = os.path.relpath(file, root)
                port_name = rel_path.replace("/", "-").replace("\\", "-").lower()

                # Auto-assign type based on file
                port_type = self._infer_port_type_from_file(file)

                # Register file wrapper as port (lazy loader)
                file_port = FilePort(file)  # simple wrapper you can extend
                self.register_port(port_name, file_port, port_type)

                discovered += 1

        # Auto-connect known compatible groups
        self._auto_connect_compatible()
        log.info(f"File auto-hub completed. Hubb'ed {discovered} files.")
        return discovered

    def _infer_port_type_from_file(self, filepath: str) -> Optional[str]:
        name = filepath.lower()
        if "vite.config" in name: return "vite:config"
        if any(x in name for x in [".jsx", ".tsx"]): return "react:component"
        if "render" in name or "deployment" in name: return "render:service"
        if name.endswith(".py"): return "web:api" if "api" in name else None
        if name.endswith(".html"): return "web:static"
        return None

    def _auto_connect_compatible(self):
        """Auto bridge common stacks like Vite ↔ React ↔ Render"""
        vite_ports = [n for n in self.ports if n.startswith("vite")]
        react_ports = [n for n in self.ports if "react" in n]
        render_ports = [n for n in self.ports if "render" in n]

        for v in vite_ports:
            for r in react_ports:
                self.connect(v, r, bidirectional=True)
            for ren in render_ports:
                self.connect(v, ren, bidirectional=True)
