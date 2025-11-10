"""
Fix all merge conflicts in the project
"""
import os
from pathlib import Path

def clean_merge_conflicts(file_path):
    """Remove merge conflicts from a file, keeping HEAD version"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        cleaned_lines = []
        skip_mode = False
        in_conflict = False
        
        for line in lines:
            if '<<<<<<< HEAD' in line:
                in_conflict = True
                continue
            elif '=======' in line and in_conflict:
                skip_mode = True
                continue
            elif '>>>>>>> ' in line and in_conflict:
                in_conflict = False
                skip_mode = False
                continue
            
            if not skip_mode:
                cleaned_lines.append(line)
        
        if len(cleaned_lines) != len(lines):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(cleaned_lines)
            print(f"✅ Fixed {file_path}: Removed {len(lines) - len(cleaned_lines)} lines")
            return True
        return False
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def fix_all():
    """Fix all Python files in the project"""
    base_dir = Path(".")
    fixed_count = 0
    
    # Files to fix
    files_to_check = [
        "api_server.py",
        "config/settings.py",
        "src/ai/script_generator.py",
        "src/ai/image_generator.py",
        "src/editor/ffmpeg_compiler.py",
    ]
    
    for file_path in files_to_check:
        full_path = base_dir / file_path
        if full_path.exists():
            if clean_merge_conflicts(full_path):
                fixed_count += 1
        else:
            print(f"⚠️ File not found: {file_path}")
    
    print(f"\n🎉 Fixed {fixed_count} files!")

if __name__ == '__main__':
    fix_all()
