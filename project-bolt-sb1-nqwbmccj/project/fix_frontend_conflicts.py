"""
Fix all merge conflicts in frontend files
"""
import os
from pathlib import Path

def clean_merge_conflicts(file_path):
    """Remove merge conflicts from a file, keeping 'ours' version"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        cleaned_lines = []
        skip_mode = False
        in_conflict = False
        
        for line in lines:
            if '<<<<<<< ours' in line or '<<<<<<< HEAD' in line:
                in_conflict = True
                continue
            elif '=======' in line and in_conflict:
                skip_mode = True
                continue
            elif '>>>>>>> theirs' in line or '>>>>>>> ' in line:
                in_conflict = False
                skip_mode = False
                continue
            
            if not skip_mode:
                cleaned_lines.append(line)
        
        if len(cleaned_lines) != len(lines):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(cleaned_lines)
            print(f"✅ Fixed {file_path.name}: Removed {len(lines) - len(cleaned_lines)} lines")
            return True
        else:
            print(f"ℹ️  No conflicts in {file_path.name}")
        return False
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def find_and_fix_all():
    """Find and fix all files with merge conflicts in src directory"""
    base_dir = Path("src")
    fixed_count = 0
    checked_count = 0
    
    if not base_dir.exists():
        print("❌ src directory not found!")
        return
    
    # Find all .ts, .tsx, .js, .jsx files
    for ext in ['*.ts', '*.tsx', '*.js', '*.jsx']:
        for file_path in base_dir.rglob(ext):
            checked_count += 1
            if clean_merge_conflicts(file_path):
                fixed_count += 1
    
    print(f"\n🎉 Summary:")
    print(f"   Files checked: {checked_count}")
    print(f"   Files fixed: {fixed_count}")
    print(f"   No conflicts: {checked_count - fixed_count}")

if __name__ == '__main__':
    find_and_fix_all()
