#!/usr/bin/env python
"""
Script to identify and remove unused code.
This helps reduce complexity and prevents old code from interfering with new implementations.
"""

import os
import shutil
from pathlib import Path


# Files and directories that can be safely removed
UNUSED_ITEMS = [
    # Old consolidated system (replaced by enterprise implementation)
    'apps/generators/consolidated/',
    
    # Old exceptions (replaced by exceptions_unified.py)
    'apps/generators/exceptions.py',
    
    # Old views (replaced by views_refactored.py)
    'apps/generators/views_refactored.py',  # Keep for now as reference
    
    # Duplicate LLM clients (replaced by shared/llm_client.py)
    'apps/generators/learning_objectives/llm_client.py',
    'apps/generators/lesson_starter/llm_client.py',
    'apps/generators/discussion_questions/llm_client.py',
    
    # Documentation files that are no longer needed
    'CONSOLIDATED_SYSTEM_QA_CHECKLIST.md',
    'CODE_QUALITY_10_10_IMPLEMENTATION.md',
    'CODE_QUALITY_TRANSFORMATION_SUMMARY.md',
    'DEDUPLICATION_REFACTORING_COMPLETE.md',
    'DUPLICATION_ANALYSIS.md',
    'ENTERPRISE_IMPLEMENTATION_COMPLETE.md',
    'SENIOR_DEVELOPER_CODE_REVIEW.md',
    'migrate_deduplication.py',
]

# Items to keep but note for future cleanup
KEEP_BUT_NOTE = [
    'apps/generators/views.py',  # Still used by URLs
    'apps/generators/tests.py',  # Original tests
    'apps/generators/base.py',  # Base generator (might be useful)
    'apps/generators/prompt_templates.py',  # Still used
    'apps/generators/document_formatter.py',  # Still used
]

def backup_item(item_path):
    """Create a backup before deletion."""
    backup_path = f"{item_path}.backup"
    if os.path.exists(item_path):
        if os.path.isdir(item_path):
            shutil.copytree(item_path, backup_path)
        else:
            shutil.copy2(item_path, backup_path)
        print(f"Backed up: {item_path} -> {backup_path}")
        return True
    return False

def remove_item(item_path):
    """Remove a file or directory."""
    if os.path.exists(item_path):
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
        else:
            os.remove(item_path)
        print(f"Removed: {item_path}")
        return True
    print(f"Not found: {item_path}")
    return False

def analyze_dependencies():
    """Analyze which files are actually used."""
    print("\n=== Dependency Analysis ===")
    
    # Check which modules are imported
    base_dir = Path(__file__).parent
    
    # Find all Python files
    python_files = list(base_dir.rglob("*.py"))
    
    # Track imports
    imports = set()
    
    for file in python_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Simple import detection
                lines = content.split('\n')
                for line in lines:
                    if line.strip().startswith('from ') or line.strip().startswith('import '):
                        imports.add(line.strip())
        except:
            pass
    
    # Print frequently imported modules
    print("\nFrequently imported modules:")
    from collections import Counter
    import_count = Counter()
    
    for imp in imports:
        # Extract module name
        parts = imp.split()
        if len(parts) >= 2:
            module = parts[1].split('.')[0]
            import_count[module] += 1
    
    for module, count in import_count.most_common(10):
        print(f"  {module}: {count} imports")

def find_duplicate_functions():
    """Find potentially duplicate functions."""
    print("\n=== Duplicate Function Analysis ===")
    
    base_dir = Path(__file__).parent / "apps/generators"
    function_definitions = {}
    
    for file in base_dir.rglob("*.py"):
        if 'backup' in str(file) or '__pycache__' in str(file):
            continue
            
        try:
            with open(file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for i, line in enumerate(lines):
                if line.strip().startswith('def '):
                    func_name = line.strip().split('(')[0].replace('def ', '')
                    if func_name not in function_definitions:
                        function_definitions[func_name] = []
                    function_definitions[func_name].append({
                        'file': str(file),
                        'line': i + 1
                    })
        except:
            pass
    
    # Find duplicates
    duplicates = {k: v for k, v in function_definitions.items() if len(v) > 1}
    
    if duplicates:
        print("\nPotentially duplicate functions:")
        for func, locations in duplicates.items():
            print(f"\n  {func}:")
            for loc in locations:
                print(f"    - {loc['file']}:{loc['line']}")
    else:
        print("\nNo duplicate functions found!")

def cleanup_unused():
    """Main cleanup function."""
    print("Starting code cleanup...")
    print("=" * 50)
    
    base_dir = Path(__file__).parent
    
    # Analyze before cleanup
    analyze_dependencies()
    find_duplicate_functions()
    
    print("\n" + "=" * 50)
    print("\nCleanup Plan:")
    print("\nItems to REMOVE:")
    for item in UNUSED_ITEMS:
        print(f"  - {item}")
    
    print("\nItems to KEEP (still in use):")
    for item in KEEP_BUT_NOTE:
        print(f"  - {item}")
    
    # Ask for confirmation
    print("\n" + "=" * 50)
    response = input("\nDo you want to proceed with cleanup? (y/N): ")
    
    if response.lower() != 'y':
        print("Cleanup cancelled.")
        return
    
    # Perform cleanup
    print("\nPerforming cleanup...")
    
    removed_count = 0
    for item in UNUSED_ITEMS:
        full_path = base_dir / item
        if backup_item(str(full_path)):
            if remove_item(str(full_path)):
                removed_count += 1
    
    print(f"\nCleanup complete! Removed {removed_count} items.")
    print("\nTo restore any deleted items, use the .backup files.")

if __name__ == '__main__':
    cleanup_unused()
