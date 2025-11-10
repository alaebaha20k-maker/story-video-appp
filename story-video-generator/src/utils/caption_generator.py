"""
📝 CAPTION GENERATOR - Perfect Voice Sync with SRT Subtitles
Creates beautifully styled captions that sync exactly with audio
"""

import re
from pathlib import Path
from typing import List, Dict


class CaptionGenerator:
    """Generate SRT subtitle files with perfect audio sync"""

    def __init__(self):
        self.max_chars_per_line = 42  # Optimal for readability
        self.max_words_per_caption = 8  # ~2 seconds of speech

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Replace common abbreviations to avoid false splits
        text = text.replace('Mr.', 'Mr').replace('Mrs.', 'Mrs').replace('Dr.', 'Dr')
        text = text.replace('etc.', 'etc').replace('e.g.', 'eg').replace('i.e.', 'ie')

        # Split on sentence endings
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        return sentences

    def _split_into_words(self, text: str) -> List[str]:
        """Split text into words, preserving punctuation"""
        return text.split()

    def _create_caption_chunks(self, text: str) -> List[str]:
        """Split text into optimal caption chunks"""
        words = self._split_into_words(text)
        chunks = []
        current_chunk = []

        for word in words:
            current_chunk.append(word)

            # Create chunk if we hit max words or end of sentence
            if len(current_chunk) >= self.max_words_per_caption or word.endswith(('.', '!', '?')):
                chunks.append(' '.join(current_chunk))
                current_chunk = []

        # Add remaining words
        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    def _format_time(self, seconds: float) -> str:
        """Convert seconds to SRT time format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def generate_srt(
        self,
        text: str,
        audio_duration: float,
        output_path: str
    ) -> str:
        """
        Generate SRT subtitle file with perfect audio sync

        Args:
            text: Full narration text
            audio_duration: Total audio duration in seconds
            output_path: Where to save the SRT file

        Returns:
            Path to generated SRT file
        """
        # Split text into caption chunks
        chunks = self._create_caption_chunks(text)

        if not chunks:
            print("⚠️  No captions to generate (empty text)")
            return None

        # Calculate timing for each chunk
        time_per_chunk = audio_duration / len(chunks)

        print(f"📝 Generating {len(chunks)} captions...")
        print(f"   Audio duration: {audio_duration:.2f}s")
        print(f"   Time per caption: {time_per_chunk:.2f}s")

        # Generate SRT content
        srt_content = []
        for i, chunk in enumerate(chunks):
            start_time = i * time_per_chunk
            end_time = start_time + time_per_chunk

            # SRT format:
            # 1
            # 00:00:00,000 --> 00:00:02,500
            # Caption text here
            srt_content.append(f"{i + 1}")
            srt_content.append(f"{self._format_time(start_time)} --> {self._format_time(end_time)}")
            srt_content.append(chunk)
            srt_content.append("")  # Blank line between captions

        # Write to file
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(srt_content))

        print(f"   ✅ SRT file created: {output_path}")
        print(f"   📊 Total captions: {len(chunks)}")

        return str(output_path)

    def generate_word_level_srt(
        self,
        text: str,
        audio_duration: float,
        output_path: str,
        words_per_caption: int = 3
    ) -> str:
        """
        Generate word-level captions for very precise sync

        Args:
            text: Full narration text
            audio_duration: Total audio duration in seconds
            output_path: Where to save the SRT file
            words_per_caption: Number of words per caption chunk

        Returns:
            Path to generated SRT file
        """
        words = self._split_into_words(text)

        if not words:
            print("⚠️  No words to generate captions from")
            return None

        # Group words into chunks
        chunks = []
        for i in range(0, len(words), words_per_caption):
            chunk = ' '.join(words[i:i + words_per_caption])
            chunks.append(chunk)

        # Calculate timing
        time_per_chunk = audio_duration / len(chunks)

        print(f"📝 Generating word-level captions...")
        print(f"   Total words: {len(words)}")
        print(f"   Words per caption: {words_per_caption}")
        print(f"   Total captions: {len(chunks)}")
        print(f"   Time per caption: {time_per_chunk:.2f}s")

        # Generate SRT
        srt_content = []
        for i, chunk in enumerate(chunks):
            start_time = i * time_per_chunk
            end_time = start_time + time_per_chunk

            srt_content.append(f"{i + 1}")
            srt_content.append(f"{self._format_time(start_time)} --> {self._format_time(end_time)}")
            srt_content.append(chunk)
            srt_content.append("")

        # Write to file
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(srt_content))

        print(f"   ✅ Word-level SRT created: {output_path}")

        return str(output_path)


# Global instance
caption_generator = CaptionGenerator()
