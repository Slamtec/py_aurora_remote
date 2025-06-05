#!/usr/bin/env python3
"""
Setup script for SLAMTEC Aurora Remote SDK Python Bindings

This script handles the installation of the Python bindings along with
the native Aurora SDK dynamic libraries for specific platforms.
"""

import os
import sys
import platform
import shutil
from pathlib import Path
from setuptools import setup, find_packages


def get_version():
    """Get version from cpp_sdk version.txt file."""
    version_file = Path(__file__).parent.parent / "cpp_sdk" / "aurora_remote_public" / "version.txt"
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


# Package information
PACKAGE_NAME = "slamtec-aurora-python-sdk"
VERSION = get_version()
DESCRIPTION = "Python bindings for SLAMTEC Aurora Remote SDK"
LONG_DESCRIPTION = """
SLAMTEC Aurora Remote SDK Python Bindings

This package provides Python bindings for the SLAMTEC Aurora Remote SDK,
enabling Python applications to communicate with Aurora devices and
retrieve pose, image, LiDAR, and map data.

Features:
- Device discovery and connection
- Real-time pose data retrieval
- Camera frame preview
- LiDAR scan data access
- Map visualization capabilities
- Pythonic API with context manager support

Requirements:
- Python 3.6+
- NumPy
- OpenCV (optional, for visualization examples)
"""

AUTHOR = "SLAMTEC Co., Ltd."
AUTHOR_EMAIL = "support@slamtec.com"
URL = "https://github.com/SLAMTEC/Aurora-Remote-Python-SDK"


def get_platform_info():
    """Get platform and architecture information."""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == "linux":
        if "aarch64" in machine or "arm64" in machine:
            return "linux", "aarch64"
        else:
            return "linux", "x86_64"
    elif system == "windows":
        return "win64", "x64"
    elif system == "darwin":
        if "arm64" in machine or "aarch64" in machine:
            return "macos", "arm64"
        else:
            return "macos", "x86_64"
    else:
        raise RuntimeError(f"Unsupported platform: {system}")


def get_native_lib_path():
    """Get the path to the native library for the current platform."""
    system, arch = get_platform_info()
    
    if system == "linux":
        if arch == "aarch64":
            return "../cpp_sdk/aurora_remote_public/lib/linux_aarch64/libslamtec_aurora_remote_sdk.so"
        else:
            return "../cpp_sdk/aurora_remote_public/lib/linux_x86_64/libslamtec_aurora_remote_sdk.so"
    elif system == "win64":
        return "../cpp_sdk/aurora_remote_public/lib/win64/slamtec_aurora_remote_sdk.dll"
    elif system == "macos":
        if arch == "arm64":
            return "../cpp_sdk/aurora_remote_public/lib/macos_arm64/libslamtec_aurora_remote_sdk.dylib"
        else:
            return "../cpp_sdk/aurora_remote_public/lib/macos_x86_64/libslamtec_aurora_remote_sdk.dylib"


def check_native_library():
    """Check if the native library exists for the current platform."""
    lib_path = get_native_lib_path()
    full_path = Path(__file__).parent / lib_path
    
    if not full_path.exists():
        print(f"ERROR: Native library not found at: {full_path}")
        print(f"Platform: {get_platform_info()}")
        print("Please ensure the Aurora SDK native library is present.")
        return False
    
    print(f"Found native library: {full_path}")
    return True


def copy_native_libraries(target_platform=None):
    """Copy native libraries to the package directory.
    
    Args:
        target_platform: Specific platform to build for (e.g., 'linux_x86_64', 'linux_aarch64', 'win64')
                        If None, builds for current platform.
    """
    # Determine target directory within the package
    package_dir = Path(__file__).parent / "slamtec_aurora_sdk"
    lib_dir = package_dir / "lib"
    
    # Clean and create lib directory
    if lib_dir.exists():
        shutil.rmtree(lib_dir)
    lib_dir.mkdir(exist_ok=True)
    
    # Create __init__.py to make this a proper Python package (silences setuptools warnings)
    init_file = lib_dir / "__init__.py"
    init_file.write_text('"""\nNative library package for Aurora SDK.\nThis package contains platform-specific native libraries.\n"""\n')
    
    # Source directory for native libraries
    cpp_lib_dir = Path(__file__).parent.parent / "cpp_sdk" / "aurora_remote_public" / "lib"
    
    # Platform to library mapping
    platform_lib_mapping = {
        "linux_aarch64": "libslamtec_aurora_remote_sdk.so",
        "linux_x86_64": "libslamtec_aurora_remote_sdk.so", 
        "win64": "slamtec_aurora_remote_sdk.dll",
        "macos_arm64": "libslamtec_aurora_remote_sdk.dylib",
        "macos_x86_64": "libslamtec_aurora_remote_sdk.dylib"
    }
    
    if target_platform:
        # Build for specific target platform
        if target_platform not in platform_lib_mapping:
            raise ValueError(f"Unsupported target platform: {target_platform}")
        
        lib_name = platform_lib_mapping[target_platform]
        src_dir = cpp_lib_dir / target_platform
        src_file = src_dir / lib_name
        dst_file = lib_dir / lib_name
        
        if src_file.exists():
            shutil.copy2(src_file, dst_file)
            print(f"Copied {src_file} -> {dst_file}")
        else:
            raise FileNotFoundError(f"Native library not found for {target_platform} at {src_file}")
    else:
        # Build for current platform
        system, arch = get_platform_info()
        
        if system == "linux":
            current_platform = f"linux_{arch}"
        elif system == "win64":
            current_platform = "win64"
        elif system == "macos":
            current_platform = f"macos_{arch}"
        else:
            raise RuntimeError(f"Unsupported current platform: {system}")
        
        lib_name = platform_lib_mapping[current_platform]
        src_dir = cpp_lib_dir / current_platform
        src_file = src_dir / lib_name
        dst_file = lib_dir / lib_name
        
        if src_file.exists():
            shutil.copy2(src_file, dst_file)
            print(f"Copied {src_file} -> {dst_file}")
        else:
            raise FileNotFoundError(f"Native library not found for current platform {current_platform} at {src_file}")


def get_supported_platforms():
    """Get list of supported platforms by checking available libraries."""
    cpp_lib_dir = Path(__file__).parent.parent / "cpp_sdk" / "aurora_remote_public" / "lib"
    platforms = []
    
    if not cpp_lib_dir.exists():
        return platforms
    
    for item in cpp_lib_dir.iterdir():
        if item.is_dir():
            platforms.append(item.name)
    
    return platforms


def read_requirements():
    """Read requirements from requirements.txt file."""
    requirements_file = Path(__file__).parent / "requirements.txt"
    if requirements_file.exists():
        with open(requirements_file, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    else:
        # Default requirements
        return [
            "numpy>=1.19.0",
        ]


def read_optional_requirements():
    """Read optional requirements for examples and visualization."""
    return [
        "opencv-python>=4.5.0",  # For visualization examples
        "matplotlib>=3.3.0",     # Alternative visualization
    ]


if __name__ == "__main__":
    # Check command line arguments for target platform
    target_platform = None
    for arg in sys.argv[1:]:
        if arg.startswith("--target-platform="):
            target_platform = arg.split("=", 1)[1]
            sys.argv.remove(arg)
            break
    
    # Also check environment variable (for build scripts)
    if not target_platform:
        target_platform = os.environ.get("AURORA_TARGET_PLATFORM", None)
    
    # Determine package name and platform info
    if target_platform:
        # Building for specific target platform
        package_name = f"{PACKAGE_NAME}-{target_platform.replace('_', '-')}"
        print(f"Building platform-specific package for target: {target_platform}")
        
        # Validate target platform exists
        cpp_lib_dir = Path(__file__).parent.parent / "cpp_sdk" / "aurora_remote_public" / "lib"
        if not (cpp_lib_dir / target_platform).exists():
            print(f"Error: Target platform {target_platform} not found in {cpp_lib_dir}")
            print(f"Available platforms: {get_supported_platforms()}")
            sys.exit(1)
    else:
        # Building for current platform
        system, arch = get_platform_info()
        package_name = f"{PACKAGE_NAME}-{system}-{arch}"
        print(f"Building platform-specific package for current platform: {system} {arch}")
        
        # Check for native library before proceeding
        if not check_native_library():
            print("\nTo fix this issue:")
            print("1. Ensure you have downloaded the complete Aurora SDK")
            print("2. Verify the cpp_sdk directory contains the native libraries")
            print("3. Check that your platform is supported")
            sys.exit(1)
    
    # Copy native libraries to package
    copy_native_libraries(target_platform=target_platform)
    
    # Read package requirements
    install_requires = read_requirements()
    extras_require = {
        "examples": read_optional_requirements(),
        "visualization": ["opencv-python>=4.5.0", "matplotlib>=3.3.0"],
    }
    
    setup(
        name=package_name,
        version=VERSION,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/plain",
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        url=URL,
        
        # Package discovery - include all packages (lib is now a proper package)
        packages=find_packages(where="."),
        package_dir={},
        
        # Include package data (native libraries)
        package_data={
            "slamtec_aurora_sdk": [
                "lib/*.so",        # Include .so files directly in lib/
                "lib/*.dll",       # Include .dll files directly in lib/
                "lib/*.dylib",     # Include .dylib files directly in lib/
            ],
        },
        # Exclude files we don't want in the package
        exclude_package_data={
            "slamtec_aurora_sdk": [
                "lib/.gitkeep",    # Exclude marker files
            ],
        },
        include_package_data=True,
        
        # Requirements
        python_requires=">=3.6",
        install_requires=install_requires,
        extras_require=extras_require,
        
        # Classifiers
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: MIT License",
            "Operating System :: POSIX :: Linux",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: MacOS",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Topic :: Scientific/Engineering",
            "Topic :: Software Development :: Libraries :: Python Modules",
        ],
        
        # Keywords
        keywords="aurora slam lidar robotics navigation mapping",
        
        # Project URLs
        project_urls={
            "Documentation": "https://www.slamtec.com/cn/Support#aurora",
            "Source": "https://github.com/SLAMTEC/Aurora-Remote-Python-SDK",
            "Tracker": "https://github.com/SLAMTEC/Aurora-Remote-Python-SDK/issues",
        },
        
        # Zip safety
        zip_safe=False,
    )
    
    print("\n" + "="*60)
    print("SLAMTEC Aurora Python SDK Build Complete!")
    print("="*60)
    print(f"Package: {package_name} v{VERSION}")
    if target_platform:
        print(f"Target Platform: {target_platform}")
    else:
        print(f"Platform: {system} {arch}")
    print()
    print("To install the built package:")
    print(f"  pip install dist/{package_name}-{VERSION}-py3-none-any.whl")
    print()
    print("Available examples in python_bindings/examples/:")
    print("  python simple_pose.py [device_ip]")
    print("  python camera_preview.py [device_ip]")
    print("  python semantic_segmentation.py --device [device_ip]")
    print()
    print("For visualization examples, install optional dependencies:")
    print(f"  pip install {package_name}[visualization]")
    print("="*60)