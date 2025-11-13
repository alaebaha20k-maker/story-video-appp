"""
Optimal Chunk Configuration System for Script Generation

This module provides smart chunking strategies that use FEWER, BIGGER chunks
to reduce API calls while maintaining high quality output.

Strategy: Inspired by successful Gemini 2.5 Flash implementations
- 100K script = Only 3 chunks (not 10-15!)
- Larger chunks = Better narrative flow
- Fewer API calls = Better rate limit management
"""

import logging

logger = logging.getLogger(__name__)


def get_optimal_chunk_config(target_length: int) -> dict:
    """
    Calculate optimal chunk configuration for target script length.

    Optimized for Gemini 2.0 Flash with 8K token limit (~6,000 chars per request).

    Args:
        target_length: Target script length in characters

    Returns:
        dict with keys:
            - chunks: Number of chunks to generate
            - chars_per_chunk: Target characters per chunk
            - buffer: Expected over-generation buffer
            - total_expected: Total expected output (target + buffer)

    Examples:
        >>> config = get_optimal_chunk_config(60000)
        >>> config['chunks']
        10
        >>> config['chars_per_chunk']
        6000
    """
    # With 8K token limit, keep chunks around 6K chars (safe for free tier)
    if target_length <= 10000:
        config = {
            'chunks': 2,
            'chars_per_chunk': 5000,
            'buffer': 2000
        }
    elif target_length <= 30000:
        config = {
            'chunks': 5,
            'chars_per_chunk': 6000,
            'buffer': 5000
        }
    elif target_length <= 60000:
        config = {
            'chunks': 10,
            'chars_per_chunk': 6000,
            'buffer': 10000
        }
    elif target_length <= 70000:
        config = {
            'chunks': 12,
            'chars_per_chunk': 6000,
            'buffer': 12000
        }
    else:  # 100K+
        config = {
            'chunks': 17,
            'chars_per_chunk': 6000,
            'buffer': 15000
        }

    config['total_expected'] = target_length + config['buffer']

    logger.info(f"📊 Chunk config for {target_length:,} chars: "
                f"{config['chunks']} chunks × {config['chars_per_chunk']:,} chars/chunk "
                f"(expected output: {config['total_expected']:,} chars)")

    return config


def estimate_target_length(duration_minutes: int, num_scenes: int = 10) -> int:
    """
    Estimate target script length based on video duration and scene count.

    Args:
        duration_minutes: Video duration in minutes
        num_scenes: Number of scenes (default: 10)

    Returns:
        Estimated target length in characters

    Formula:
        - Base: 10,000 chars per minute of video
        - Scene adjustment: +500 chars per scene for detailed descriptions
    """
    base_length = duration_minutes * 10000
    scene_bonus = num_scenes * 500
    target = base_length + scene_bonus

    logger.info(f"📏 Estimated target: {target:,} chars "
                f"({duration_minutes} min video, {num_scenes} scenes)")

    return target


def get_chunk_section_goal(chunk_num: int, total_chunks: int) -> str:
    """
    Get the narrative goal for a specific chunk.

    Args:
        chunk_num: Current chunk number (1-indexed)
        total_chunks: Total number of chunks

    Returns:
        Description of what this chunk should accomplish
    """
    progress = chunk_num / total_chunks

    if total_chunks == 1:
        return "COMPLETE STORY: Full beginning, middle, climax, and ending"

    if chunk_num == 1:
        return "OPENING: Hook, setup, character introduction, rising action begins"
    elif chunk_num == total_chunks:
        return "CLIMAX & RESOLUTION: Peak conflict, resolution, character arc completion, satisfying ending"
    else:
        return "ESCALATION: Rising action, conflict intensifies, character development, tension building"


def should_add_ending_requirements(chunk_num: int, total_chunks: int) -> bool:
    """
    Determine if this chunk needs explicit ending requirements.

    Args:
        chunk_num: Current chunk number (1-indexed)
        total_chunks: Total number of chunks

    Returns:
        True if this is the final chunk that needs ending instructions
    """
    return chunk_num == total_chunks
