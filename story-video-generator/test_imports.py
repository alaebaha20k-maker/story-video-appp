"""
🧪 Test all imports to ensure backend can start
"""

def test_imports():
    """Test all critical imports"""
    print("\n" + "="*60)
    print("🧪 Testing Backend Imports")
    print("="*60 + "\n")
    
    errors = []
    
    # Test 1: Script Generator
    try:
        from src.ai.script_generator import script_generator
        print("✅ script_generator imported successfully")
    except Exception as e:
        errors.append(f"❌ script_generator: {e}")
        print(f"❌ script_generator: {e}")
    
    # Test 2: Image Generator
    try:
        from src.ai.image_generator import image_generator
        print("✅ image_generator imported successfully")
    except Exception as e:
        errors.append(f"❌ image_generator: {e}")
        print(f"❌ image_generator: {e}")
    
    # Test 3: TTS Engine
    try:
        from src.voice.tts_engine import tts_engine
        print("✅ tts_engine imported successfully")
    except Exception as e:
        errors.append(f"❌ tts_engine: {e}")
        print(f"❌ tts_engine: {e}")
    
    # Test 4: Video Compiler
    try:
        from src.editor.video_compiler import video_compiler
        print("✅ video_compiler imported successfully")
    except Exception as e:
        errors.append(f"❌ video_compiler: {e}")
        print(f"❌ video_compiler: {e}")
    
    # Test 5: Image Manager
    try:
        from src.media.image_manager import image_manager
        print("✅ image_manager imported successfully")
    except Exception as e:
        errors.append(f"❌ image_manager: {e}")
        print(f"❌ image_manager: {e}")
    
    # Test 6: API Server
    try:
        import api_server
        print("✅ api_server imported successfully")
    except Exception as e:
        errors.append(f"❌ api_server: {e}")
        print(f"❌ api_server: {e}")
    
    # Test 7: Main
    try:
        import main
        print("✅ main.py imported successfully")
    except Exception as e:
        errors.append(f"❌ main: {e}")
        print(f"❌ main: {e}")
    
    print("\n" + "="*60)
    
    if errors:
        print("❌ FAILED - Some imports have errors:")
        for error in errors:
            print(f"   {error}")
        print("\n💡 Fix these import errors before running the backend")
    else:
        print("✅ SUCCESS - All imports working!")
        print("\n🚀 You can now run:")
        print("   python api_server.py")
        print("   OR")
        print("   python main.py")
    
    print("="*60 + "\n")
    
    return len(errors) == 0


if __name__ == "__main__":
    success = test_imports()
    exit(0 if success else 1)
