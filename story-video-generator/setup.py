"""
📦 SETUP - Installation script
"""

from setuptools import setup, find_packages

setup(
    name="ai-video-generator",
    version="1.0.0",
    description="AI-powered video generation system",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "google-generativeai>=0.3.0",
        "requests>=2.31.0",
        "pillow>=10.0.0",
        "together>=1.0.0",
        "edge-tts>=6.1.0",
        "pydub>=0.25.1",
        "moviepy>=1.0.3",
        "numpy>=1.24.0",
        "pexels-api>=1.0.0",
        "python-dotenv>=1.0.0",
        "tqdm>=4.66.0",
        "colorama>=0.4.6",
        "rich>=13.0.0"
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "videogen=main:interactive_mode",
        ],
    },
)