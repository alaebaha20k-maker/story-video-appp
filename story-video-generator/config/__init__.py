"""
Configuration package
"""

# ═══════════════════════════════════════════════════════════════
# 🌐 GOOGLE COLAB GPU SERVER CONFIGURATION
# ═══════════════════════════════════════════════════════════════

# ⚠️ IMPORTANT: Update this URL when you start your Colab notebook!
# The Colab notebook will show you the ngrok URL after running all cells.
# Example: https://xxxx-xxxx-xxxx.ngrok-free.app

COLAB_SERVER_URL = 'https://contemplable-suzy-unfussing.ngrok-free.dev'

# Colab endpoints
COLAB_ENDPOINTS = {
    'health': '/health',
    'generate_audio': '/generate_audio',  # Kokoro TTS
    'generate_image': '/generate_image',  # SDXL-Turbo single
    'generate_images_batch': '/generate_images_batch',  # SDXL-Turbo batch
    'compile_video': '/compile_video'  # FFmpeg video compilation with ALL effects
}