#!/usr/bin/env python3
"""
Documentation Update Script for SLAMTEC Aurora Python SDK

This script updates the API reference documentation by regenerating it from
the current source code. It can be run manually or integrated into CI/CD pipelines.

Usage:
    python tools/update_docs.py [--clean] [--format html|markdown|both] [--verbose]

Features:
- Automatic backup of existing documentation
- Clean regeneration or incremental updates
- Support for both HTML and Markdown formats
- Verification of documentation completeness
- Git integration for tracking changes
"""

import os
import sys
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime


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


def generate_docs(project_root, format_type, verbose=False):
    """Generate documentation using the documentation generator."""
    generator_script = project_root / "tools" / "generate_docs.py"
    
    if not generator_script.exists():
        print(f"Error: Documentation generator not found: {generator_script}")
        return False
    
    cmd = f"python3 {generator_script} --format {format_type} --output docs"
    result = run_command(cmd, cwd=project_root, verbose=verbose)
    
    return result is not None


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


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Update Aurora Python SDK API documentation")
    parser.add_argument("--clean", action="store_true",
                       help="Clean existing documentation before regenerating")
    parser.add_argument("--format", choices=["html", "markdown", "both"], default="both",
                       help="Documentation format to generate (default: both)")
    parser.add_argument("--no-backup", action="store_true",
                       help="Skip creating backup of existing documentation")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose output")
    parser.add_argument("--check-only", action="store_true",
                       help="Only check if documentation needs updating")
    
    args = parser.parse_args()
    
    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    docs_dir = project_root / "docs"
    
    print("SLAMTEC Aurora Python SDK Documentation Updater")
    print("=" * 55)
    
    # Get SDK version
    sdk_version = get_sdk_version(project_root)
    print(f"SDK Version: {sdk_version}")
    print(f"Project Root: {project_root}")
    print(f"Documentation Directory: {docs_dir}")
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
        backup_dir = backup_docs(docs_dir, args.verbose)
    
    try:
        # Clean documentation if requested
        if args.clean:
            clean_docs(docs_dir, args.verbose)
        
        # Generate documentation
        formats_to_generate = []
        if args.format == "both":
            formats_to_generate = ["markdown", "html"]
        else:
            formats_to_generate = [args.format]
        
        success = True
        for fmt in formats_to_generate:
            print(f"Generating {fmt.upper()} documentation...")
            if not generate_docs(project_root, fmt, args.verbose):
                print(f"Failed to generate {fmt} documentation")
                success = False
            else:
                # Verify generated documentation
                if not verify_docs(docs_dir, fmt, args.verbose):
                    print(f"Documentation verification failed for {fmt}")
                    success = False
        
        if success:
            print()
            print("✅ Documentation update completed successfully!")
            
            # Show summary
            if docs_dir.exists():
                md_files = len(list(docs_dir.glob("*.md")))
                html_files = len(list(docs_dir.glob("*.html")))
                print(f"   📄 Markdown files: {md_files}")
                print(f"   🌐 HTML files: {html_files}")
            
            # Check for git changes
            if check_git_status(project_root, False):
                print("   📝 Git changes detected in documentation")
                print("   Run 'git add docs/ && git commit' to commit changes")
            
            # Show access information
            if "markdown" in formats_to_generate:
                print(f"   📖 View Markdown: {docs_dir / 'index.md'}")
            if "html" in formats_to_generate:
                print(f"   🌐 View HTML: {docs_dir / 'index.html'}")
            
            return 0
        else:
            print("❌ Documentation update failed")
            
            # Restore backup if available
            if backup_dir and backup_dir.exists():
                print(f"Restoring backup from {backup_dir}")
                if docs_dir.exists():
                    shutil.rmtree(docs_dir)
                shutil.move(backup_dir, docs_dir)
            
            return 1
            
    except Exception as e:
        print(f"❌ Error during documentation update: {e}")
        
        # Restore backup if available
        if backup_dir and backup_dir.exists():
            print(f"Restoring backup from {backup_dir}")
            try:
                if docs_dir.exists():
                    shutil.rmtree(docs_dir)
                shutil.move(backup_dir, docs_dir)
            except Exception as restore_error:
                print(f"Failed to restore backup: {restore_error}")
        
        return 1
    
    finally:
        # Clean up old backups (keep only the most recent 3)
        if not args.no_backup:
            backup_pattern = project_root / "docs_backup_*"
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