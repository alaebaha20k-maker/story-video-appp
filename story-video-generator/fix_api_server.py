"""
Script to automatically fix api_server.py - Remove merge conflicts and keep only Edge TTS
"""

def clean_api_server():
    backup_file = "api_server.py.backup"
    output_file = "api_server.py"
    
    print("Reading backup file...")
    with open(backup_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Total lines: {len(lines)}")
    
    # Remove merge conflict markers and keep only HEAD version (which has Edge TTS)
    cleaned_lines = []
    skip_mode = False
    in_conflict = False
    
    for i, line in enumerate(lines):
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
    
    print(f"Cleaned lines: {len(cleaned_lines)}")
    
    # Write cleaned version
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)
    
    print(f"✅ Cleaned api_server.py written! Removed {len(lines) - len(cleaned_lines)} lines.")
    print("\n📋 Summary:")
    print(f"   Original: {len(lines)} lines")
    print(f"   Cleaned: {len(cleaned_lines)} lines")
    print(f"   Removed: {len(lines) - len(cleaned_lines)} lines")

if __name__ == '__main__':
    clean_api_server()
