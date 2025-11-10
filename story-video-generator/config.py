"""
🔧 CONFIGURATION - Google Colab GPU Server URLs

Update these URLs when you start a new Colab session!
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

# ═══════════════════════════════════════════════════════════════════════════════
# 📝 HOW TO UPDATE:
# ═══════════════════════════════════════════════════════════════════════════════
#
# Option 1: Edit this file directly
#   1. Run your Google Colab notebook
#   2. Copy the ngrok URL (e.g., https://abc-123.ngrok-free.dev)
#   3. Replace COLAB_SERVER_URL value above
#   4. Restart your backend server
#
# Option 2: Use environment variable
#   export COLAB_SERVER_URL="https://your-ngrok-url.ngrok-free.dev"
#   python api_server.py
#
# ═══════════════════════════════════════════════════════════════════════════════

print(f"🌐 Colab Server URL: {COLAB_SERVER_URL}")
print(f"🎤 Kokoro API: {KOKORO_API_URL}")
print(f"🎨 SDXL API: {SDXL_API_URL}")
