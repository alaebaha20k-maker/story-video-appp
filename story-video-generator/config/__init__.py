"""
Configuration package
"""

import os

# ═══════════════════════════════════════════════════════════════════════════════
# 🌐 GOOGLE COLAB SERVER URLS (Update when you start new Colab session!)
# ═══════════════════════════════════════════════════════════════════════════════

# Get from environment variable or use default
COLAB_SERVER_URL = os.getenv(
    'COLAB_SERVER_URL',
    'https://contemplable-suzy-unfussing.ngrok-free.dev'  # ✅ UPDATED!
)

# API Endpoints
KOKORO_API_URL = f"{COLAB_SERVER_URL}/generate_audio"
SDXL_API_URL = f"{COLAB_SERVER_URL}/generate_image"
SDXL_BATCH_API_URL = f"{COLAB_SERVER_URL}/generate_images_batch"

print(f"🌐 Colab Server URL: {COLAB_SERVER_URL}")
print(f"🎤 Kokoro API: {KOKORO_API_URL}")
print(f"🎨 SDXL API: {SDXL_API_URL}")
