import subprocess
import json
from pathlib import Path
from typing import Tuple, Dict, Any
from .base import BaseVerifier

class SwiftVerifier(BaseVerifier):
    def run_tests(self, test_spec: str) -> Tuple[bool, str]:
        """Run Swift tests"""
        try:
            cmd = ["swift", "test", "--filter", test_spec] if " " in test_spec else ["swift", "test"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
    
    def verify_vision_pro_setup(self) -> Dict[str, bool]:
        """Verify Vision Pro specific setup"""
        checks = {}
        
        # Check for RealityKit imports
        swift_files = list(Path(".").rglob("*.swift"))
        has_realitykit = any(
            "import RealityKit" in f.read_text() 
            for f in swift_files
            if f.exists()
        )
        checks['realitykit_imported'] = has_realitykit
        
        # Check Package.swift for visionOS platform
        package_swift = Path("Package.swift")
        if package_swift.exists():
            content = package_swift.read_text()
            checks['visionos_platform'] = "visionOS" in content
        
        return checks
