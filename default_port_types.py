from typing import Dict, Optional, Collection
import threading


class PortType:
    """Immutable port type with a global registry (thread-safe)."""

    _registry: Dict[str, "PortType"] = {}
    _lock = threading.Lock()

    def __init__(self, id: str, category: str, description: str):
        self._id = id.lower().strip()
        self._category = category.upper().strip()
        self._description = description

    @property
    def id(self) -> str:
        return self._id

    @property
    def category(self) -> str:
        return self._category

    @property
    def description(self) -> str:
        return self._description

    @classmethod
    def register(cls, id: str, category: str, description: str) -> "PortType":
        """Register a new PortType (thread-safe)."""
        with cls._lock:
            port_type = cls(id, category, description)
            cls._registry[port_type.id] = port_type
            return port_type

    @classmethod
    def get(cls, id: str) -> Optional["PortType"]:
        """Get a PortType by id (case-insensitive)."""
        with cls._lock:
            return cls._registry.get(id.lower().strip())

    @classmethod
    def get_all(cls) -> Collection["PortType"]:
        """Return all registered PortTypes."""
        with cls._lock:
            return list(cls._registry.values())

    def __repr__(self) -> str:
        return f"PortType(id='{self.id}', category='{self.category}')"


class DefaultPortTypes:
    """Register all default port types."""

    @staticmethod
    def register_all() -> None:
        # === BUILD TOOLS & FRAMEWORKS ===
        PortType.register("vite:config", "BUILD", "Vite Configuration (vite.config.js/ts)")
        PortType.register("vite:devserver", "BUILD", "Vite Development Server")
        PortType.register("vite:build", "BUILD", "Vite Production Build Output")
        PortType.register("vite:asset", "BUILD", "Vite Asset (processed by Vite)")
        PortType.register("vite:module", "BUILD", "Vite Module Federation / Async Chunk")

        PortType.register("react:component", "FRAMEWORK", "React Component")
        PortType.register("vue:component", "FRAMEWORK", "Vue Component")
        PortType.register("svelte:component", "FRAMEWORK", "Svelte Component")

        # === RENDERING ===
        PortType.register("ssr:render", "RENDER", "Server-Side Rendering Output")
        PortType.register("csr:render", "RENDER", "Client-Side Rendering")
        PortType.register("render:static", "RENDER", "Static Site Generation (SSG)")
        PortType.register("render:stream", "RENDER", "Streaming SSR")

        # === Render.com Platform ===
        PortType.register("render:service", "RENDER", "Render.com Service")
        PortType.register("render:deployment", "RENDER", "Render.com Deployment")
        PortType.register("render:env", "RENDER", "Render.com Environment Variables")
        PortType.register("render:preview", "RENDER", "Render.com Preview Environment")
        PortType.register("render:customdomain", "RENDER", "Render.com Custom Domain")

        # === GitHub ===
        PortType.register("github:repo", "GITHUB", "GitHub Repository")
        PortType.register("github:pr", "GITHUB", "GitHub Pull Request")
        PortType.register("github:workflow", "GITHUB", "GitHub Actions Workflow")
        PortType.register("github:artifact", "GITHUB", "GitHub Artifact")
        PortType.register("github:release", "GITHUB", "GitHub Release")

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


# Optional: auto-register on import
# DefaultPortTypes.register_all()
