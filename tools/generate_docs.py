#!/usr/bin/env python3
"""
Documentation Generator for SLAMTEC Aurora Python SDK

This script automatically generates API reference documentation by parsing
Python source files and extracting docstrings, class definitions, and method signatures.

Usage:
    python tools/generate_docs.py [--format html|markdown|both] [--output DIR] [--clean] [--verbose]

Features:
- Extracts docstrings, classes, methods, and function signatures
- Generates both HTML and Markdown formats
- Cross-references between components
- Automatic table of contents
- Code syntax highlighting
- Type hints extraction
- Backup and restore functionality
- Git integration for change tracking
- Documentation verification
"""

import os
import sys
import ast
import inspect
import argparse
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import importlib.util


def run_command(cmd, cwd=None, verbose=False):
    """Run a shell command and return the result."""
    if verbose:
        print(f"Running: {cmd}")
    
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd, 
            capture_output=True, text=True, check=True
        )
        if verbose and result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {cmd}")
        print(f"Error: {e.stderr}")
        return None


def backup_docs(docs_dir, verbose=False):
    """Create a backup of existing documentation."""
    if not docs_dir.exists():
        if verbose:
            print("No existing documentation to backup")
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = docs_dir.parent / f"docs_backup_{timestamp}"
    
    try:
        shutil.copytree(docs_dir, backup_dir)
        if verbose:
            print(f"Created backup: {backup_dir}")
        return backup_dir
    except Exception as e:
        print(f"Failed to create backup: {e}")
        return None


def clean_docs(docs_dir, verbose=False):
    """Clean existing documentation directory."""
    if docs_dir.exists():
        shutil.rmtree(docs_dir)
        if verbose:
            print(f"Cleaned documentation directory: {docs_dir}")


def verify_docs(docs_dir, format_type, verbose=False):
    """Verify that documentation was generated correctly."""
    if not docs_dir.exists():
        print("Error: Documentation directory not found")
        return False
    
    # Check for index file
    if format_type == "markdown":
        index_file = docs_dir / "index.md"
    elif format_type == "html":
        index_file = docs_dir / "index.html"
    else:
        # Check both for 'both' format
        index_md = docs_dir / "index.md"
        index_html = docs_dir / "index.html"
        if not (index_md.exists() and index_html.exists()):
            print("Error: Missing index files")
            return False
        if verbose:
            print("Found both HTML and Markdown index files")
        return True
    
    if not index_file.exists():
        print(f"Error: Index file not found: {index_file}")
        return False
    
    # Count documentation files
    if format_type == "markdown":
        doc_files = list(docs_dir.glob("*.md"))
    elif format_type == "html":
        doc_files = list(docs_dir.glob("*.html"))
    else:
        doc_files = list(docs_dir.glob("*.md")) + list(docs_dir.glob("*.html"))
    
    if len(doc_files) < 5:  # Should have at least index + a few module docs
        print(f"Warning: Only {len(doc_files)} documentation files found")
        return False
    
    if verbose:
        print(f"Verification passed: Found {len(doc_files)} documentation files")
    
    return True


def check_git_status(project_root, verbose=False):
    """Check if there are changes in the documentation."""
    result = run_command("git status --porcelain docs/", cwd=project_root, verbose=False)
    
    if result and result.stdout.strip():
        if verbose:
            print("Documentation changes detected:")
            print(result.stdout)
        return True
    else:
        if verbose:
            print("No documentation changes detected")
        return False


def get_sdk_version(project_root):
    """Get SDK version from the source code."""
    init_file = project_root / "python_bindings" / "slamtec_aurora_sdk" / "__init__.py"
    
    try:
        with open(init_file, 'r') as f:
            content = f.read()
        
        # Extract version from __version__ = "x.x.x"
        for line in content.split('\n'):
            if line.strip().startswith('__version__'):
                version = line.split('=')[1].strip().strip('"\'')
                return version
    except Exception:
        pass
    
    return "unknown"


class DocGenerator:
    """Main documentation generator class."""
    
    def __init__(self, sdk_path, output_dir, format_type="markdown"):
        """
        Initialize documentation generator.
        
        Args:
            sdk_path: Path to the SDK source code
            output_dir: Output directory for generated docs
            format_type: Output format ('html' or 'markdown')
        """
        self.sdk_path = sdk_path
        self.output_dir = output_dir
        self.format_type = format_type
        self.modules = {}
        self.components = {}
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def extract_module_info(self, module_path: Path) -> Dict[str, Any]:
        """Extract information from a Python module."""
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source)
            module_info = {
                'name': module_path.stem,
                'path': module_path,
                'docstring': ast.get_docstring(tree),
                'classes': [],
                'functions': [],
                'imports': [],
                'constants': []
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = self.extract_class_info(node)
                    module_info['classes'].append(class_info)
                elif isinstance(node, ast.FunctionDef) and not self.is_method(node, tree):
                    func_info = self.extract_function_info(node)
                    module_info['functions'].append(func_info)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        module_info['imports'].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        for alias in node.names:
                            module_info['imports'].append(f"{node.module}.{alias.name}")
                elif isinstance(node, ast.Assign):
                    # Extract module-level constants
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            module_info['constants'].append({
                                'name': target.id,
                                'value': self.get_node_value(node.value)
                            })
            
            return module_info
            
        except Exception as e:
            print(f"Error parsing {module_path}: {e}")
            return None
    
    def extract_class_info(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Extract information from a class definition."""
        class_info = {
            'name': node.name,
            'docstring': ast.get_docstring(node),
            'bases': [self.get_node_name(base) for base in node.bases],
            'methods': [],
            'properties': [],
            'class_variables': []
        }
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self.extract_function_info(item, is_method=True)
                if item.name.startswith('__') and item.name.endswith('__'):
                    method_info['type'] = 'magic'
                elif item.name.startswith('_'):
                    method_info['type'] = 'private'
                else:
                    method_info['type'] = 'public'
                
                # Check if it's a property
                if any(isinstance(decorator, ast.Name) and decorator.id == 'property' 
                       for decorator in item.decorator_list):
                    method_info['type'] = 'property'
                    class_info['properties'].append(method_info)
                else:
                    class_info['methods'].append(method_info)
            elif isinstance(item, ast.Assign):
                # Class variables
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        class_info['class_variables'].append({
                            'name': target.id,
                            'value': self.get_node_value(item.value)
                        })
        
        return class_info
    
    def extract_function_info(self, node: ast.FunctionDef, is_method: bool = False) -> Dict[str, Any]:
        """Extract information from a function definition."""
        func_info = {
            'name': node.name,
            'docstring': ast.get_docstring(node),
            'args': [],
            'returns': None,
            'decorators': [self.get_node_name(dec) for dec in node.decorator_list],
            'is_method': is_method,
            'is_async': isinstance(node, ast.AsyncFunctionDef)
        }
        
        # Extract arguments
        for arg in node.args.args:
            arg_info = {'name': arg.arg}
            if arg.annotation:
                arg_info['type'] = self.get_node_name(arg.annotation)
            func_info['args'].append(arg_info)
        
        # Extract return type
        if node.returns:
            func_info['returns'] = self.get_node_name(node.returns)
        
        return func_info
    
    def get_node_name(self, node) -> str:
        """Get string representation of an AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self.get_node_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return f"{self.get_node_name(node.value)}[{self.get_node_name(node.slice)}]"
        elif isinstance(node, ast.Constant):
            return repr(node.value)
        else:
            return str(node)
    
    def get_node_value(self, node) -> str:
        """Get value representation of an AST node."""
        try:
            if isinstance(node, ast.Constant):
                return repr(node.value)
            elif isinstance(node, ast.Name):
                return node.id
            else:
                return "<complex_value>"
        except:
            return "<unknown>"
    
    def is_method(self, node: ast.FunctionDef, tree: ast.AST) -> bool:
        """Check if a function is a method (inside a class)."""
        for parent in ast.walk(tree):
            if isinstance(parent, ast.ClassDef):
                if node in parent.body:
                    return True
        return False
    
    def scan_sdk_modules(self) -> None:
        """Scan all SDK modules and extract information."""
        print(f"Scanning SDK modules in {self.sdk_path}")
        
        for py_file in self.sdk_path.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
                
            print(f"Processing {py_file.name}...")
            module_info = self.extract_module_info(py_file)
            if module_info:
                self.modules[module_info['name']] = module_info
                
        print(f"Found {len(self.modules)} modules")
    
    def generate_markdown_docs(self) -> None:
        """Generate Markdown documentation."""
        print("Generating Markdown documentation...")
        
        # Generate index page
        self.generate_markdown_index()
        
        # Generate individual module pages
        for module_name, module_info in self.modules.items():
            self.generate_markdown_module(module_name, module_info)
        
        print(f"Markdown documentation generated in {self.output_dir}")
    
    def generate_markdown_index(self) -> None:
        """Generate main index page in Markdown."""
        content = [
            "# SLAMTEC Aurora Python SDK API Reference",
            "",
            "This is the automatically generated API reference for the SLAMTEC Aurora Python SDK.",
            "",
            "## Components",
            "",
        ]
        
        # Sort modules by priority, then alphabetically within same priority
        sorted_modules = sorted(self.modules.items(), 
                              key=lambda x: (self.get_module_priority(x[0]), x[0]))
        
        # Add all modules in priority order
        for module_name, module_info in sorted_modules:
            description = self.extract_short_description(module_info['docstring'])
            content.append(f"- **[{module_name}]({module_name}.md)** - {description}")
        
        content.extend([
            "",
            "## Quick Start",
            "",
            "```python",
            "from slamtec_aurora_sdk import AuroraSDK",
            "",
            "# Create SDK instance",
            "sdk = AuroraSDK()",
            "",
            "# Connect to device",
            "sdk.connect(connection_string=\"192.168.1.212\")",
            "",
            "# Get data",
            "pose = sdk.data_provider.get_current_pose()",
            "left_img, right_img = sdk.data_provider.get_camera_preview()",
            "",
            "# Cleanup",
            "sdk.disconnect()",
            "sdk.release()",
            "```",
            "",
            "## Architecture",
            "",
            "The Aurora Python SDK follows a component-based architecture:",
            "",
        ])
        
        # Dynamically build architecture description from actual modules
        architecture_components = []
        for module_name, module_info in sorted_modules:
            # Skip utility/internal modules from architecture overview
            if module_name in ['c_bindings', 'data_types', 'exceptions', 'utils']:
                continue
            
            # Get first line of docstring as component description
            description = self.extract_short_description(module_info['docstring'])
            if description and description != "No description available":
                # Convert module_name to readable format using smart capitalization
                display_name = self.format_module_display_name(module_name)
                architecture_components.append(f"- **{display_name}**: {description}")
        
        content.extend(architecture_components)
        content.extend([
            "",
            f"*Documentation generated automatically from source code*",
        ])
        
        with open(self.output_dir / "index.md", 'w', encoding='utf-8') as f:
            f.write("\n".join(content))
    
    def generate_markdown_module(self, module_name: str, module_info: Dict[str, Any]) -> None:
        """Generate Markdown documentation for a single module."""
        content = [
            f"# {module_name}",
            "",
        ]
        
        # Module docstring
        if module_info['docstring']:
            content.extend([
                module_info['docstring'],
                "",
            ])
        
        # Import statement
        content.extend([
            "## Import",
            "",
            f"```python",
            f"from slamtec_aurora_sdk import {module_name}",
            f"```",
            "",
        ])
        
        # Classes
        if module_info['classes']:
            content.append("## Classes")
            content.append("")
            
            for class_info in module_info['classes']:
                content.extend(self.generate_markdown_class(class_info))
        
        # Functions
        if module_info['functions']:
            content.append("## Functions")
            content.append("")
            
            for func_info in module_info['functions']:
                content.extend(self.generate_markdown_function(func_info))
        
        # Constants
        if module_info['constants']:
            content.append("## Constants")
            content.append("")
            
            for const in module_info['constants']:
                content.append(f"- **{const['name']}** = `{const['value']}`")
            content.append("")
        
        with open(self.output_dir / f"{module_name}.md", 'w', encoding='utf-8') as f:
            f.write("\n".join(content))
    
    def generate_markdown_class(self, class_info: Dict[str, Any]) -> List[str]:
        """Generate Markdown documentation for a class."""
        content = [
            f"### {class_info['name']}",
            "",
        ]
        
        # Inheritance
        if class_info['bases']:
            content.append(f"**Inherits from:** {', '.join(class_info['bases'])}")
            content.append("")
        
        # Class docstring
        if class_info['docstring']:
            content.extend([
                class_info['docstring'],
                "",
            ])
        
        # Properties
        if class_info['properties']:
            content.extend([
                "#### Properties",
                "",
            ])
            
            for prop in class_info['properties']:
                content.extend(self.generate_markdown_method(prop, is_property=True))
        
        # Public methods
        public_methods = [m for m in class_info['methods'] if m['type'] == 'public']
        if public_methods:
            content.extend([
                "#### Methods",
                "",
            ])
            
            for method in public_methods:
                content.extend(self.generate_markdown_method(method))
        
        # Magic methods
        magic_methods = [m for m in class_info['methods'] if m['type'] == 'magic']
        if magic_methods:
            content.extend([
                "#### Special Methods",
                "",
            ])
            
            for method in magic_methods:
                content.extend(self.generate_markdown_method(method))
        
        return content
    
    def generate_markdown_method(self, method_info: Dict[str, Any], is_property: bool = False) -> List[str]:
        """Generate Markdown documentation for a method."""
        content = []
        
        # Method signature
        if is_property:
            signature = f"**{method_info['name']}**"
        else:
            args = []
            for arg in method_info['args']:
                if 'type' in arg:
                    args.append(f"{arg['name']}: {arg['type']}")
                else:
                    args.append(arg['name'])
            
            return_type = ""
            if method_info['returns']:
                return_type = f" -> {method_info['returns']}"
            
            signature = f"**{method_info['name']}**({', '.join(args)}){return_type}"
        
        content.extend([
            signature,
            "",
        ])
        
        # Method docstring
        if method_info['docstring']:
            # Parse docstring for arguments and returns
            docstring = method_info['docstring']
            content.extend([
                docstring,
                "",
            ])
        
        return content
    
    def generate_markdown_function(self, func_info: Dict[str, Any]) -> List[str]:
        """Generate Markdown documentation for a function."""
        return self.generate_markdown_method(func_info)
    
    def extract_short_description(self, docstring: Optional[str]) -> str:
        """Extract first sentence from docstring as short description."""
        if not docstring:
            return "No description available"
        
        lines = docstring.strip().split('\\n')
        first_line = lines[0].strip()
        
        if first_line:
            # Take first sentence
            if '.' in first_line:
                return first_line.split('.')[0] + '.'
            return first_line
        
        return "No description available"
    
    def format_module_display_name(self, module_name: str) -> str:
        """Format module name for display in documentation."""
        # Special cases for known acronyms and formatting
        special_cases = {
            'aurora_sdk': 'AuroraSDK',
            'lidar_2d_map_builder': 'LIDAR2DMapBuilder',
            'imu': 'IMU',
            'api': 'API',
            'sdk': 'SDK',
            'lidar': 'LIDAR',
            'vslam': 'VSLAM',
            'ai': 'AI',
            'cv': 'CV',
            'ml': 'ML'
        }
        
        if module_name in special_cases:
            return special_cases[module_name]
        
        # Split by underscores and capitalize each part
        parts = module_name.split('_')
        formatted_parts = []
        
        for part in parts:
            # Check if part is a known acronym
            if part.lower() in special_cases:
                formatted_parts.append(special_cases[part.lower()])
            else:
                # Regular capitalization
                formatted_parts.append(part.capitalize())
        
        return ''.join(formatted_parts)
    
    def get_module_priority(self, module_name: str) -> int:
        """Determine module priority for sorting (lower number = higher priority)."""
        # Main SDK entry point
        if module_name == 'aurora_sdk':
            return 0
        # Core components
        elif module_name in ['controller', 'data_provider']:
            return 1
        # Feature components (any module ending with common patterns)
        elif any(module_name.endswith(suffix) for suffix in ['_manager', '_builder', '_detector']):
            return 2
        elif module_name in ['enhanced_imaging', 'floor_detector']:
            return 2
        # Data and utility modules
        elif module_name in ['data_types', 'exceptions', 'utils']:
            return 4
        # Low-level modules
        elif module_name in ['c_bindings']:
            return 5
        # Everything else (future components)
        else:
            return 3
    
    def generate_html_docs(self) -> None:
        """Generate HTML documentation."""
        print("Generating HTML documentation...")
        
        # HTML template
        html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Aurora Python SDK</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; margin: 0; padding: 20px; background: #f8f9fa; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; border-bottom: 1px solid #ecf0f1; padding-bottom: 5px; }}
        h3 {{ color: #2980b9; }}
        h4 {{ color: #7f8c8d; }}
        code {{ background: #f8f9fa; padding: 2px 6px; border-radius: 3px; font-family: 'Monaco', 'Consolas', monospace; }}
        pre {{ background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        pre code {{ background: none; padding: 0; }}
        .nav {{ background: #34495e; color: white; padding: 10px 0; margin: -40px -40px 40px -40px; border-radius: 8px 8px 0 0; }}
        .nav ul {{ list-style: none; padding: 0 20px; margin: 0; }}
        .nav li {{ display: inline-block; margin-right: 20px; }}
        .nav a {{ color: #3498db; text-decoration: none; }}
        .nav a:hover {{ text-decoration: underline; }}
        .signature {{ background: #e8f4fd; padding: 10px; border-left: 4px solid #3498db; margin: 10px 0; }}
        .docstring {{ margin: 15px 0; }}
        .back-to-top {{ position: fixed; bottom: 20px; right: 20px; background: #3498db; color: white; padding: 10px; border-radius: 50%; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="container">
        <nav class="nav">
            <ul>
                <li><a href="index.html">Home</a></li>
                {nav_links}
            </ul>
        </nav>
        {content}
        <a href="#" class="back-to-top">↑</a>
    </div>
</body>
</html>'''
        
        # Generate navigation links
        nav_links = []
        for module_name in sorted(self.modules.keys()):
            nav_links.append(f'<li><a href="{module_name}.html">{module_name}</a></li>')
        nav_links_str = "\\n".join(nav_links)
        
        # Generate index page
        index_content = self.generate_html_index()
        with open(self.output_dir / "index.html", 'w', encoding='utf-8') as f:
            f.write(html_template.format(
                title="API Reference",
                nav_links=nav_links_str,
                content=index_content
            ))
        
        # Generate module pages
        for module_name, module_info in self.modules.items():
            module_content = self.generate_html_module(module_name, module_info)
            with open(self.output_dir / f"{module_name}.html", 'w', encoding='utf-8') as f:
                f.write(html_template.format(
                    title=module_name,
                    nav_links=nav_links_str,
                    content=module_content
                ))
        
        print(f"HTML documentation generated in {self.output_dir}")
    
    def generate_html_index(self) -> str:
        """Generate HTML index page content."""
        content = [
            "<h1>SLAMTEC Aurora Python SDK API Reference</h1>",
            "<p>This is the automatically generated API reference for the SLAMTEC Aurora Python SDK.</p>",
            "<h2>Components</h2>",
            "<ul>",
        ]
        
        # Sort modules by priority, then alphabetically within same priority
        sorted_modules = sorted(self.modules.items(), 
                              key=lambda x: (self.get_module_priority(x[0]), x[0]))
        
        for module_name, module_info in sorted_modules:
            description = self.extract_short_description(module_info['docstring'])
            display_name = self.format_module_display_name(module_name)
            content.append(f'<li><strong><a href="{module_name}.html">{display_name}</a></strong> - {description}</li>')
        
        content.extend([
            "</ul>",
            "<h2>Quick Start</h2>",
            "<pre><code>from slamtec_aurora_sdk import AuroraSDK\n\n# Create SDK instance\nsdk = AuroraSDK()\n\n# Connect to device\nsdk.connect(connection_string=\"192.168.1.212\")\n\n# Get data\npose = sdk.data_provider.get_current_pose()\nleft_img, right_img = sdk.data_provider.get_camera_preview()\n\n# Cleanup\nsdk.disconnect()\nsdk.release()</code></pre>",
        ])
        
        return "\n".join(content)
    
    def generate_html_module(self, module_name: str, module_info: Dict[str, Any]) -> str:
        """Generate HTML content for a module."""
        content = [
            f"<h1>{module_name}</h1>",
        ]
        
        if module_info['docstring']:
            content.extend([
                f"<div class='docstring'>{module_info['docstring'].replace(chr(10), '<br>')}</div>",
            ])
        
        # Classes
        if module_info['classes']:
            content.append("<h2>Classes</h2>")
            for class_info in module_info['classes']:
                content.extend(self.generate_html_class(class_info))
        
        # Functions
        if module_info['functions']:
            content.append("<h2>Functions</h2>")
            for func_info in module_info['functions']:
                content.extend(self.generate_html_function(func_info))
        
        return "\n".join(content)
    
    def generate_html_class(self, class_info: Dict[str, Any]) -> List[str]:
        """Generate HTML documentation for a class."""
        content = [
            f"<h3>{class_info['name']}</h3>",
        ]
        
        if class_info['docstring']:
            content.append(f"<div class='docstring'>{class_info['docstring'].replace(chr(10), '<br>')}</div>")
        
        # Methods
        if class_info['methods']:
            content.append("<h4>Methods</h4>")
            for method in class_info['methods']:
                if method['type'] == 'public':
                    content.extend(self.generate_html_method(method))
        
        return content
    
    def generate_html_method(self, method_info: Dict[str, Any]) -> List[str]:
        """Generate HTML documentation for a method."""
        args = [arg['name'] for arg in method_info['args']]
        signature = f"{method_info['name']}({', '.join(args)})"
        
        content = [
            f"<div class='signature'><code>{signature}</code></div>",
        ]
        
        if method_info['docstring']:
            content.append(f"<div class='docstring'>{method_info['docstring'].replace(chr(10), '<br>')}</div>")
        
        return content
    
    def generate_html_function(self, func_info: Dict[str, Any]) -> List[str]:
        """Generate HTML documentation for a function."""
        return self.generate_html_method(func_info)
    
    def generate(self) -> None:
        """Generate documentation in the specified format."""
        self.scan_sdk_modules()
        
        if self.format_type == "markdown":
            self.generate_markdown_docs()
        elif self.format_type == "html":
            self.generate_html_docs()
        else:
            raise ValueError(f"Unsupported format: {self.format_type}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Generate Aurora Python SDK API documentation")
    parser.add_argument("--format", choices=["html", "markdown", "both"], default="markdown",
                       help="Output format (default: markdown)")
    parser.add_argument("--output", type=str, default="docs",
                       help="Output directory (default: docs)")
    parser.add_argument("--sdk-path", type=str,
                       help="Path to SDK source code (default: auto-detect)")
    parser.add_argument("--clean", action="store_true",
                       help="Clean existing documentation before regenerating")
    parser.add_argument("--no-backup", action="store_true",
                       help="Skip creating backup of existing documentation")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose output")
    parser.add_argument("--check-only", action="store_true",
                       help="Only check if documentation needs updating")
    
    args = parser.parse_args()
    
    # Get project root and SDK path
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    if args.sdk_path:
        sdk_path = Path(args.sdk_path)
    else:
        sdk_path = project_root / "python_bindings" / "slamtec_aurora_sdk"
    
    if not sdk_path.exists():
        print(f"Error: SDK path not found: {sdk_path}")
        return 1
    
    output_dir = project_root / args.output
    
    print("SLAMTEC Aurora Python SDK Documentation Generator")
    print("=" * 55)
    
    # Get SDK version
    sdk_version = get_sdk_version(project_root)
    print(f"SDK Version: {sdk_version}")
    print(f"Project Root: {project_root}")
    print(f"SDK Path: {sdk_path}")
    print(f"Output Directory: {output_dir}")
    print(f"Format: {args.format}")
    print()
    
    # Check if documentation needs updating (git-based)
    if args.check_only:
        has_changes = check_git_status(project_root, args.verbose)
        if has_changes:
            print("Documentation may need updating (git changes detected)")
            return 1
        else:
            print("Documentation appears up to date")
            return 0
    
    # Create backup if requested
    backup_dir = None
    if not args.no_backup:
        backup_dir = backup_docs(output_dir, args.verbose)
    
    try:
        # Clean documentation if requested
        if args.clean:
            clean_docs(output_dir, args.verbose)
        
        # Generate documentation
        formats_to_generate = []
        if args.format == "both":
            formats_to_generate = ["markdown", "html"]
        else:
            formats_to_generate = [args.format]
        
        success = True
        for fmt in formats_to_generate:
            print(f"Generating {fmt.upper()} documentation...")
            
            # Generate documentation
            generator = DocGenerator(sdk_path, output_dir, fmt)
            try:
                generator.generate()
                
                # Verify generated documentation
                if not verify_docs(output_dir, fmt, args.verbose):
                    print(f"Documentation verification failed for {fmt}")
                    success = False
            except Exception as e:
                print(f"Failed to generate {fmt} documentation: {e}")
                success = False
        
        if success:
            print()
            print("✅ Documentation generation completed successfully!")
            
            # Show summary
            if output_dir.exists():
                md_files = len(list(output_dir.glob("*.md")))
                html_files = len(list(output_dir.glob("*.html")))
                print(f"   📄 Markdown files: {md_files}")
                print(f"   🌐 HTML files: {html_files}")
            
            # Check for git changes
            if check_git_status(project_root, False):
                print("   📝 Git changes detected in documentation")
                print("   Run 'git add docs/ && git commit' to commit changes")
            
            # Show access information
            if "markdown" in formats_to_generate:
                print(f"   📖 View Markdown: {output_dir / 'index.md'}")
            if "html" in formats_to_generate:
                print(f"   🌐 View HTML: {output_dir / 'index.html'}")
            
            return 0
        else:
            print("❌ Documentation generation failed")
            
            # Restore backup if available
            if backup_dir and backup_dir.exists():
                print(f"Restoring backup from {backup_dir}")
                if output_dir.exists():
                    shutil.rmtree(output_dir)
                shutil.move(backup_dir, output_dir)
            
            return 1
            
    except Exception as e:
        print(f"❌ Error during documentation generation: {e}")
        
        # Restore backup if available
        if backup_dir and backup_dir.exists():
            print(f"Restoring backup from {backup_dir}")
            try:
                if output_dir.exists():
                    shutil.rmtree(output_dir)
                shutil.move(backup_dir, output_dir)
            except Exception as restore_error:
                print(f"Failed to restore backup: {restore_error}")
        
        return 1
    
    finally:
        # Clean up old backups (keep only the most recent 3)
        if not args.no_backup:
            backups = sorted(project_root.glob("docs_backup_*"))
            if len(backups) > 3:
                for old_backup in backups[:-3]:
                    try:
                        shutil.rmtree(old_backup)
                        if args.verbose:
                            print(f"Removed old backup: {old_backup}")
                    except Exception as e:
                        if args.verbose:
                            print(f"Failed to remove old backup {old_backup}: {e}")


if __name__ == "__main__":
    sys.exit(main())