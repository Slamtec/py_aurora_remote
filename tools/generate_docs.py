#!/usr/bin/env python3
"""
Documentation Generator for SLAMTEC Aurora Python SDK

This script automatically generates API reference documentation by parsing
Python source files and extracting docstrings, class definitions, and method signatures.

Usage:
    python tools/generate_docs.py [--format html|markdown] [--output DIR]

Features:
- Extracts docstrings, classes, methods, and function signatures
- Generates both HTML and Markdown formats
- Cross-references between components
- Automatic table of contents
- Code syntax highlighting
- Type hints extraction
"""

import os
import sys
import ast
import inspect
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import importlib.util


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
        
        # Sort modules by importance
        important_modules = ['aurora_sdk', 'controller', 'data_provider', 'map_manager', 
                           'lidar_2d_map_builder', 'enhanced_imaging', 'floor_detector', 
                           'data_types', 'exceptions']
        
        # Add important modules first
        for module_name in important_modules:
            if module_name in self.modules:
                module_info = self.modules[module_name]
                description = self.extract_short_description(module_info['docstring'])
                content.append(f"- **[{module_name}]({module_name}.md)** - {description}")
        
        # Add remaining modules
        for module_name, module_info in self.modules.items():
            if module_name not in important_modules:
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
            "- **AuroraSDK**: Main SDK class providing component access",
            "- **Controller**: Device connection and control",
            "- **DataProvider**: Data acquisition (pose, images, sensors)",
            "- **MapManager**: VSLAM (3D visual mapping) operations",
            "- **LIDAR2DMapBuilder**: 2D LIDAR mapping operations",
            "- **EnhancedImaging**: Advanced imaging features",
            "- **FloorDetector**: Multi-floor detection",
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
        
        for module_name, module_info in self.modules.items():
            description = self.extract_short_description(module_info['docstring'])
            content.append(f'<li><strong><a href="{module_name}.html">{module_name}</a></strong> - {description}</li>')
        
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
    parser.add_argument("--format", choices=["html", "markdown"], default="markdown",
                       help="Output format (default: markdown)")
    parser.add_argument("--output", type=str, default="docs",
                       help="Output directory (default: docs)")
    parser.add_argument("--sdk-path", type=str,
                       help="Path to SDK source code (default: auto-detect)")
    
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
    print("=" * 50)
    print(f"SDK Path: {sdk_path}")
    print(f"Output Directory: {output_dir}")
    print(f"Format: {args.format}")
    print()
    
    # Generate documentation
    generator = DocGenerator(sdk_path, output_dir, args.format)
    try:
        generator.generate()
        print()
        print("Documentation generation completed successfully!")
        print(f"Open {output_dir / ('index.' + args.format)} to view the documentation.")
        return 0
    except Exception as e:
        print(f"Error generating documentation: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())