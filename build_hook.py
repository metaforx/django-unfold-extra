from hatchling.builders.hooks.plugin.interface import BuildHookInterface
import subprocess
from pathlib import Path

class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        """
        Build the CSS files before packaging.
        """
        project_root = Path.cwd()
        src_dir = project_root / "unfold_extra" / "src"

        # Only proceed if the src directory exists
        if not src_dir.exists():
            self.app.display_warning(f"Warning: {src_dir} does not exist, skipping CSS build")
            return

        # Ensure node_modules exists
        if not (src_dir / "node_modules").exists():
            self.app.display_info("Installing Node.js dependencies...")
            subprocess.run(["npm", "install"], cwd=src_dir)

        # Build the CSS
        self.app.display_info("Building CSS files...")
        result = subprocess.run(
            ["npx", "tailwindcss", "-i", "css/unfold_extra.css", "-o", "../static/unfold_extra/css/styles.css", "--minify"],
            cwd=src_dir
        )

        if result.returncode != 0:
            self.app.display_warning("Failed to build CSS, continuing anyway")
        else:
            self.app.display_info("CSS built successfully")