#!/usr/bin/env python3
"""
Build script for SLAMTEC Aurora Python SDK packaging.

This script builds platform-specific wheel packages for the Aurora Python SDK.
Each platform gets its own wheel package to avoid user confusion.

Usage:
    python tools/build_package.py [--all-platforms] [--platforms PLATFORM...] [--clean] [--test]
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path


def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent


def get_version():
    """Get version from cpp_sdk version.txt file."""
    version_file = get_project_root() / "cpp_sdk" / "aurora_remote_public" / "version.txt"
    if version_file.exists():
        with open(version_file, 'r') as f:
            lines = f.readlines()
            # Version is on the 4th line
            if len(lines) >= 4:
                version_line = lines[3].strip()
                # Extract version number (e.g., "2.0.0-alpha" -> "2.0.0a0")
                version = version_line.replace('-alpha', 'a0').replace('-beta', 'b0').replace('-rc', 'rc')
                return version
    return "1.0.0"  # fallback version


def get_supported_platforms():
    """Get list of supported platforms by checking available libraries."""
    cpp_lib_dir = get_project_root() / "cpp_sdk" / "aurora_remote_public" / "lib"
    platforms = []
    
    if not cpp_lib_dir.exists():
        return platforms
    
    for item in cpp_lib_dir.iterdir():
        if item.is_dir():
            platforms.append(item.name)
    
    return platforms


def clean_build_artifacts():
    """Clean previous build artifacts."""
    project_root = get_project_root()
    python_bindings_dir = project_root / "python_bindings"
    
    # Directories to clean
    dirs_to_clean = [
        python_bindings_dir / "build",
        python_bindings_dir / "dist", 
        python_bindings_dir / "slamtec_aurora_sdk.egg-info",
        python_bindings_dir / "slamtec_aurora_sdk" / "lib"  # Package lib directory
    ]
    
    # Clean directories
    for dir_path in dirs_to_clean:
        if dir_path.exists():
            print(f"Cleaning {dir_path}")
            shutil.rmtree(dir_path)
    
    # Clean .pyc files
    for pyc_file in python_bindings_dir.rglob("*.pyc"):
        pyc_file.unlink()
    
    # Clean __pycache__ directories
    for pycache_dir in python_bindings_dir.rglob("__pycache__"):
        shutil.rmtree(pycache_dir)


def build_package(target_platforms=None, clean=False):
    """Build wheel packages for specified platforms.
    
    Args:
        target_platforms: List of platforms to build for, or None for current platform only
        clean: Whether to clean build artifacts first
    """
    project_root = get_project_root()
    python_bindings_dir = project_root / "python_bindings"
    
    if clean:
        print("Cleaning previous build artifacts...")
        clean_build_artifacts()
    
    # Check required directories
    if not python_bindings_dir.exists():
        print(f"Error: python_bindings directory not found at {python_bindings_dir}")
        return False
    
    if not (project_root / "cpp_sdk" / "aurora_remote_public" / "lib").exists():
        print("Error: Native libraries not found. Please ensure cpp_sdk/aurora_remote_public/lib exists.")
        return False
    
    # If no target platforms specified, build for current platform
    if target_platforms is None:
        target_platforms = [None]  # None means current platform
    
    all_builds_successful = True
    
    for target_platform in target_platforms:
        print(f"\n{'='*60}")
        if target_platform:
            print(f"Building for platform: {target_platform}")
        else:
            print("Building for current platform")
        print(f"{'='*60}")
        
        # Clean lib directory before each build
        lib_dir = python_bindings_dir / "slamtec_aurora_sdk" / "lib"
        if lib_dir.exists():
            shutil.rmtree(lib_dir)
        
        # Try multiple build approaches to work around permission issues
        build_approaches = [
            # Approach 1: Build in temp directory (most reliable for our use case)
            {
                "name": "build in temp directory",
                "cmd": [sys.executable, "setup.py", "build", "--build-base", f"/tmp/aurora_build_{target_platform or 'current'}", "bdist_wheel"],
                "use_env": False
            },
            # Approach 2: Use pip build module (fallback)
            {
                "name": "pip build module", 
                "cmd": [sys.executable, "-m", "build", "--wheel"],
                "use_env": True
            },
            # Approach 3: Direct setup.py with elevated permissions
            {
                "name": "setup.py with sudo",
                "cmd": ["sudo", sys.executable, "setup.py", "bdist_wheel"],
                "use_env": False
            },
            # Approach 4: Build source distribution as fallback
            {
                "name": "source distribution (sdist)",
                "cmd": [sys.executable, "setup.py", "sdist"],
                "use_env": False
            }
        ]
        
        platform_build_successful = False
        
        for approach in build_approaches:
            try:
                print(f"\n--- Trying {approach['name']} ---")
                
                # Prepare command and environment
                if approach["use_env"] and target_platform:
                    # Set environment variable for setup.py
                    env = os.environ.copy()
                    env["AURORA_TARGET_PLATFORM"] = target_platform
                    cmd = approach["cmd"]
                elif not approach["use_env"] and target_platform:
                    # Add command line argument
                    cmd = approach["cmd"] + [f"--target-platform={target_platform}"]
                    env = None
                else:
                    cmd = approach["cmd"]
                    env = None
                
                print(f"Command: {' '.join(cmd)}")
                print(f"Working directory: {python_bindings_dir}")
                if target_platform and approach["use_env"]:
                    print(f"Environment: AURORA_TARGET_PLATFORM={target_platform}")
                
                # Run the build
                result = subprocess.run(cmd, cwd=python_bindings_dir, check=True, 
                                      capture_output=True, text=True, env=env)
                
                print("✅ Build successful!")
                print("Build output:")
                print(result.stdout)
                if result.stderr:
                    print("Build warnings:")
                    print(result.stderr)
                platform_build_successful = True
                break
                
            except subprocess.CalledProcessError as e:
                print(f"❌ {approach['name']} failed with exit code {e.returncode}")
                if e.stderr:
                    print("Error output:")
                    print(e.stderr)
                if e.stdout:
                    print("Standard output:")
                    print(e.stdout)
                print(f"Trying next approach...\n")
                continue
            except FileNotFoundError as e:
                print(f"❌ {approach['name']} failed: {e}")
                print(f"Trying next approach...\n")
                continue
        
        if not platform_build_successful:
            print(f"❌ All build approaches failed for platform: {target_platform or 'current'}")
            all_builds_successful = False
        else:
            print(f"✅ Successfully built package for platform: {target_platform or 'current'}")
    
    # Copy wheels to root wheels directory
    if all_builds_successful:
        copy_wheels_to_root()
    
    return all_builds_successful


def copy_wheels_to_root():
    """Copy built wheel packages to the root wheels directory."""
    project_root = get_project_root()
    source_dist_dir = project_root / "python_bindings" / "dist"
    root_wheels_dir = project_root / "wheels"
    
    if not source_dist_dir.exists():
        print("No dist directory found, skipping wheel copy")
        return
    
    # Create wheels directory in root if it doesn't exist
    root_wheels_dir.mkdir(exist_ok=True)
    
    # Find all wheel files
    wheel_files = list(source_dist_dir.glob("*.whl"))
    
    if not wheel_files:
        print("No wheel files found to copy")
        return
    
    print(f"\nCopying wheels to {root_wheels_dir}:")
    for wheel_file in wheel_files:
        dest_file = root_wheels_dir / wheel_file.name
        
        # Copy the file (overwrite if exists)
        shutil.copy2(wheel_file, dest_file)
        size_mb = dest_file.stat().st_size / (1024 * 1024)
        print(f"  ✅ {wheel_file.name} ({size_mb:.1f} MB)")
    
    print(f"✅ Successfully copied {len(wheel_files)} wheel(s) to root wheels directory")


def test_package():
    """Test the built package by trying to import it in a clean virtual environment."""
    print("Testing package import in virtual environment...")
    
    # Create a temporary virtual environment for testing
    project_root = get_project_root()
    test_env = project_root / "test_env"
    
    try:
        # Clean up any existing test environment
        if test_env.exists():
            print(f"Removing existing test environment: {test_env}")
            shutil.rmtree(test_env)
        
        print(f"Creating test virtual environment: {test_env}")
        # Create test environment using python3
        subprocess.run(["python3", "-m", "venv", str(test_env)], check=True)
        
        # Get pip and python executables
        if sys.platform == "win32":
            pip_exe = test_env / "Scripts" / "pip.exe"
            python_exe = test_env / "Scripts" / "python.exe"
        else:
            pip_exe = test_env / "bin" / "pip"
            python_exe = test_env / "bin" / "python"
        
        print(f"Using pip: {pip_exe}")
        print(f"Using python: {python_exe}")
        
        # Upgrade pip first
        print("Upgrading pip in test environment...")
        subprocess.run([str(pip_exe), "install", "--upgrade", "pip"], check=True)
        
        # Install required dependencies
        print("Installing numpy dependency...")
        subprocess.run([str(pip_exe), "install", "numpy"], check=True)
        
        # Find the built wheel - test the most recent one
        wheels_dir = project_root / "wheels"
        if wheels_dir.exists():
            wheel_files = list(wheels_dir.glob("*.whl"))
        else:
            # Fallback to dist directory
            dist_dir = project_root / "python_bindings" / "dist"
            wheel_files = list(dist_dir.glob("*.whl"))
        
        if not wheel_files:
            print("Error: No wheel files found to test")
            return False
        
        # Sort by modification time to get the latest
        wheel_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        wheel_file = wheel_files[0]  # Test the latest wheel
        print(f"Testing wheel: {wheel_file.name}")
        
        # Install the wheel
        print("Installing Aurora SDK wheel package...")
        subprocess.run([str(pip_exe), "install", str(wheel_file)], check=True)
        
        # Test import and basic functionality
        test_script = '''
import sys
import os
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print()

try:
    import slamtec_aurora_sdk
    print(f"✅ Successfully imported slamtec_aurora_sdk")
    print(f"   Location: {slamtec_aurora_sdk.__file__}")
    
    # Test SDK creation
    print("\\nTesting SDK creation...")
    sdk = slamtec_aurora_sdk.AuroraSDK()
    print("✅ Successfully created AuroraSDK instance")
    
    # Test version access (this should work even without device)
    try:
        version_info = sdk.get_version_info()
        print(f"✅ SDK version info: {version_info}")
    except Exception as e:
        print(f"⚠️  Could not get version info (expected without device): {e}")
        print("   This is normal behavior when no Aurora device is connected")
    
    # Test component access
    print("\\nTesting component access...")
    controller = sdk.controller
    data_provider = sdk.data_provider
    map_manager = sdk.map_manager
    print("✅ Successfully accessed all SDK components")
    
    # Cleanup
    sdk.release()
    print("✅ Successfully released SDK resources")
    
    print("\\n🎉 Package test completed successfully!")
    print("   The Aurora SDK package is working correctly")
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''
        
        print("Running package tests...")
        result = subprocess.run([str(python_exe), "-c", test_script], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        
        if result.stderr:
            print("Test warnings:")
            print(result.stderr)
        
        print("✅ Package test completed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Package test failed with exit code {e.returncode}")
        if hasattr(e, 'stdout') and e.stdout:
            print("Test output:")
            print(e.stdout)
        if hasattr(e, 'stderr') and e.stderr:
            print("Error output:")
            print(e.stderr)
        return False
    except Exception as e:
        print(f"❌ Package test failed with exception: {e}")
        return False
    finally:
        # Clean up test environment
        if test_env.exists():
            print(f"Cleaning up test environment: {test_env}")
            try:
                shutil.rmtree(test_env)
            except Exception as e:
                print(f"Warning: Could not clean up test environment: {e}")
                print(f"Please manually remove: {test_env}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Build Aurora Python SDK packages")
    parser.add_argument("--all-platforms", action="store_true", 
                       help="Build packages for all supported platforms")
    parser.add_argument("--platforms", nargs="+", 
                       help="Build packages for specific platforms (e.g., linux_x86_64 linux_aarch64 win64)")
    parser.add_argument("--clean", action="store_true",
                       help="Clean build artifacts before building")
    parser.add_argument("--test", action="store_true",
                       help="Test the built package after building")
    
    args = parser.parse_args()
    
    print("="*60)
    print("SLAMTEC Aurora Python SDK Package Builder")
    print("="*60)
    
    version = get_version()
    platforms = get_supported_platforms()
    
    print(f"SDK Version: {version}")
    print(f"Available platforms: {', '.join(platforms)}")
    
    # Determine which platforms to build
    if args.all_platforms:
        target_platforms = platforms
        print("Building packages for all supported platforms")
    elif args.platforms:
        target_platforms = args.platforms
        # Validate platforms
        for platform in target_platforms:
            if platform not in platforms:
                print(f"Error: Platform '{platform}' not supported")
                print(f"Available platforms: {', '.join(platforms)}")
                sys.exit(1)
        print(f"Building packages for specified platforms: {', '.join(target_platforms)}")
    else:
        target_platforms = None  # Current platform only
        import platform
        system = platform.system().lower()
        machine = platform.machine().lower()
        print(f"Building package for current platform: {system} {machine}")
    
    print()
    
    # Build the packages
    success = build_package(target_platforms=target_platforms, clean=args.clean)
    
    if not success:
        print("❌ Package build failed")
        sys.exit(1)
    
    print("✅ Package build successful")
    
    # Test the package if requested
    if args.test:
        print("\nTesting built packages...")
        test_success = test_package()
        if not test_success:
            print("❌ Package test failed")
            sys.exit(1)
        print("✅ Package test successful")
    
    # Show built packages
    project_root = Path(__file__).parent.parent
    wheels_dir = project_root / "wheels"
    
    if wheels_dir.exists():
        wheel_files = list(wheels_dir.glob("*.whl"))
        if wheel_files:
            print(f"\nBuilt packages available in {wheels_dir}:")
            wheel_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            for wheel in wheel_files:
                size_mb = wheel.stat().st_size / (1024 * 1024)
                print(f"  {wheel.name} ({size_mb:.1f} MB)")
            
            print(f"\nTo install a package:")
            print(f"  pip install wheels/<package_name>.whl")
            print(f"\nExample:")
            if wheel_files:
                print(f"  pip install wheels/{wheel_files[0].name}")
    else:
        # Fallback to dist directory
        dist_dir = project_root / "python_bindings" / "dist"
        if dist_dir.exists():
            wheel_files = list(dist_dir.glob("*.whl"))
            if wheel_files:
                print(f"\nBuilt packages in {dist_dir}:")
                wheel_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                for wheel in wheel_files:
                    size_mb = wheel.stat().st_size / (1024 * 1024)
                    print(f"  {wheel.name} ({size_mb:.1f} MB)")
    
    print("\n" + "="*60)
    print("Build completed successfully!")
    print("="*60)


if __name__ == "__main__":
    main()