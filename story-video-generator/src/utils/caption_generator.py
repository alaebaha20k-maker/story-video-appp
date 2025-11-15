"""
🎬 AUTO CAPTION GENERATOR
Generates TikTok-style auto-captions from script text with perfect timing
"""

import re
from typing import List, Dict


def split_script_into_sentences(script: str) -> List[str]:
    """
    Split script into sentences for caption generation

    Args:
        script: Full script text

    Returns:
        List of sentence strings
    """
    # Remove extra whitespace
    script = ' '.join(script.split())

    # Split on sentence boundaries (., !, ?)
    sentences = re.split(r'(?<=[.!?])\s+', script)

    # Filter out empty sentences
    sentences = [s.strip() for s in sentences if s.strip()]

    return sentences


def generate_auto_captions(
    script: str,
    audio_duration: float,
    style: str = 'simple',
    position: str = 'bottom'
) -> List[Dict]:
    """
    Generate auto-captions from script with timing based on audio duration

    Args:
        script: Full script text
        audio_duration: Total audio duration in seconds
        style: Caption style (simple, bold, minimal, etc.)
        position: Caption position (top, bottom, center)

    Returns:
        List of caption dictionaries with timing
    """
    # Split script into sentences
    sentences = split_script_into_sentences(script)

    if not sentences:
        return []

    # Calculate total characters to estimate timing
    total_chars = sum(len(s) for s in sentences)

    captions = []
    current_time = 0.0

    for sentence in sentences:
        # Calculate duration based on character count (proportional distribution)
        char_ratio = len(sentence) / total_chars
        duration = audio_duration * char_ratio

        # Minimum duration: 1 second, maximum: 8 seconds
        duration = max(1.0, min(duration, 8.0))

        caption = {
            'text': sentence,
            'start_time': current_time,
            'duration': duration,
            'style': style,
            'position': position
        }

        captions.append(caption)
        current_time += duration

    # Adjust timings to match exact audio duration
    if captions:
        total_caption_time = sum(c['duration'] for c in captions)
        scale_factor = audio_duration / total_caption_time

        current_time = 0.0
        for caption in captions:
            caption['start_time'] = current_time
            caption['duration'] *= scale_factor
            current_time += caption['duration']

    return captions


def generate_word_by_word_captions(
    script: str,
    audio_duration: float,
    words_per_caption: int = 3,
    style: str = 'bold',
    position: str = 'bottom'
) -> List[Dict]:
    """
    Generate TikTok-style word-by-word captions (viral style)

    Args:
        script: Full script text
        audio_duration: Total audio duration in seconds
        words_per_caption: Number of words per caption (2-4 recommended)
        style: Caption style
        position: Caption position

    Returns:
        List of caption dictionaries with timing
    """
    # Remove extra whitespace and split into words
    words = script.split()

    if not words:
        return []

    # Group words into chunks
    caption_chunks = []
    for i in range(0, len(words), words_per_caption):
        chunk = ' '.join(words[i:i + words_per_caption])
        caption_chunks.append(chunk)

    # Calculate duration per caption
    duration_per_caption = audio_duration / len(caption_chunks)

    # Minimum 0.3s per caption, maximum 2s
    duration_per_caption = max(0.3, min(duration_per_caption, 2.0))

    captions = []
    current_time = 0.0

    for chunk in caption_chunks:
        caption = {
            'text': chunk,
            'start_time': current_time,
            'duration': duration_per_caption,
            'style': style,
            'position': position
        }

        captions.append(caption)
        current_time += duration_per_caption

    return captions


def generate_manual_caption(
    text: str,
    audio_duration: float,
    style: str = 'simple',
    position: str = 'bottom',
    animation: str = 'none'
) -> List[Dict]:
    """
    Generate single manual caption for entire video

    Args:
        text: Caption text
        audio_duration: Total audio duration
        style: Caption style
        position: Caption position
        animation: Animation type (not used in FFmpeg, kept for compatibility)

    Returns:
        Single caption that spans entire video
    """
    return [{
        'text': text,
        'start_time': 0.0,
        'duration': audio_duration,
        'style': style,
        'position': position
    }]


# Example usage
if __name__ == '__main__':
    test_script = "This is a scary story. It begins in a dark forest. Strange sounds echo through the trees. What will happen next?"
    test_duration = 15.0

    print("Sentence-based captions:")
    captions = generate_auto_captions(test_script, test_duration)
    for i, cap in enumerate(captions, 1):
        print(f"{i}. [{cap['start_time']:.1f}s - {cap['start_time'] + cap['duration']:.1f}s] {cap['text']}")

    print("\nWord-by-word captions:")
    word_captions = generate_word_by_word_captions(test_script, test_duration, words_per_caption=3)
    for i, cap in enumerate(word_captions[:5], 1):
        print(f"{i}. [{cap['start_time']:.1f}s - {cap['start_time'] + cap['duration']:.1f}s] {cap['text']}")
