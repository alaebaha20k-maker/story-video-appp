"""
🎬 CHUNKED SCRIPT GENERATOR - Replicates HTML Gemini API Logic
Direct Gemini 2.5 Flash API calls with chunking for long scripts
"""

import requests
import time
import re
from typing import Dict, List, Optional
from src.utils.logger import logger


class ChunkedScriptGenerator:
    """Generate scripts using chunked Gemini API calls (HTML logic replica)"""

    def __init__(self):
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        logger.info("🎬 Chunked Script Generator initialized (Gemini 2.5 Flash)")

    def get_chunk_config(self, target_length: int) -> Dict:
        """Calculate chunking configuration based on target length"""
        if target_length <= 10000:
            return {"chunks": 2, "chars_per_chunk": 6000}
        elif target_length <= 30000:
            return {"chunks": 2, "chars_per_chunk": 15000}
        elif target_length <= 60000:
            return {"chunks": 3, "chars_per_chunk": 20000}
        elif target_length <= 70000:
            return {"chunks": 3, "chars_per_chunk": 25000}
        else:  # >= 100000
            return {"chunks": 3, "chars_per_chunk": 35000}

    def extract_last_sentences(self, text: str, num_sentences: int = 8) -> str:
        """Extract last N sentences for seamless continuation"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

        if len(sentences) <= num_sentences:
            return text

        last_sentences = sentences[-num_sentences:]
        return '. '.join(last_sentences) + '.'

    def build_first_chunk_prompt(
        self,
        video_title: str,
        niche: str,
        type_: str,
        style_example: str,
        story_plot: str,
        extra_instructions: str,
        chars_per_chunk: int,
        total_chunks: int
    ) -> str:
        """Build prompt for first chunk (matches HTML exactly)"""

        # Determine if single or multi-chunk
        if total_chunks == 1:
            chunk_focus = "Write COMPLETE story with full beginning, middle, climax, and ending."
        else:
            chunk_focus = f"Chunk 1 of {total_chunks} - Focus: Hook, setup, character introduction, rising action begins"

        prompt = f"""You are a MASTER YouTube scriptwriter creating {type_} content in the {niche} niche.

🎯 TARGET: {chars_per_chunk} characters (Chunk 1 of {total_chunks})

STYLE REFERENCE (MATCH THIS EXACTLY):
{style_example}

STORY DETAILS:
Title: {video_title}
Plot: {story_plot}
{extra_instructions if extra_instructions else ''}

{chunk_focus}

CRITICAL RULES:
❌ NO labels, headers, or section markers
❌ NO character name changes (establish names at start, keep them)
❌ NO personality shifts
✅ Match the style example EXACTLY (tone, pacing, structure)
✅ Start directly with narrative
✅ All 5 senses in descriptions (sight, sound, smell, taste, touch)
✅ Natural dialogue with contractions
✅ Show don't tell emotions (physical reactions)
✅ Build tension constantly
✅ Specific details (names, places, objects)
✅ Varied sentence length for rhythm
✅ Strong vocabulary without repetition

CHARACTER CONSISTENCY:
- Establish clear character names early
- NEVER change names or personalities
- Maintain consistent traits
- Natural character development
- Reference earlier events smoothly

EMOTIONAL DEPTH:
- Physical manifestations of emotions
- Internal thoughts when appropriate
- Sensory reactions to situations
- Authentic dialogue

WRITE EXACTLY {chars_per_chunk} CHARACTERS with rich detail!

Generate NOW (no title):"""

        return prompt

    def build_continuation_prompt(
        self,
        video_title: str,
        niche: str,
        type_: str,
        previous_chunk: str,
        chars_per_chunk: int,
        part_num: int,
        total_chunks: int
    ) -> str:
        """Build prompt for continuation chunks (matches HTML exactly)"""

        # Extract context from previous chunk
        previous_context = self.extract_last_sentences(previous_chunk, 8)

        # Determine chunk focus
        if part_num == total_chunks:
            chunk_focus = "FINAL CHUNK - Complete story with satisfying, emotionally resonant ending!"
        else:
            # Mid-story chunks
            progress = part_num / total_chunks
            if progress < 0.5:
                chunk_focus = "Focus: Rising action, escalating tension"
            elif progress < 0.75:
                chunk_focus = "Focus: Complications, peak tension building"
            else:
                chunk_focus = "Focus: Climactic events leading to resolution"

        prompt = f"""Continue SEAMLESSLY. Chunk {part_num} of {total_chunks}.

TITLE: {video_title}
STYLE: {type_} | NICHE: {niche}

PREVIOUS CHUNK ENDED:
"{previous_context}"

🎯 TARGET: {chars_per_chunk} characters

{chunk_focus}

SEAMLESS CONTINUATION:
✅ Continue EXACTLY where previous ended
✅ Same character names and personalities
✅ Same writing style and tone
✅ Continue mid-scene if needed
✅ Natural story flow
✅ Reference previous events smoothly

MAINTAIN:
- Same sensory immersion
- Consistent character voices
- Established relationships
- Story momentum

WRITE {chars_per_chunk} CHARACTERS with maximum quality!

Continue NOW:"""

        return prompt

    def call_gemini_api(
        self,
        prompt: str,
        api_key: str,
        retry_count: int = 0,
        max_retries: int = 3
    ) -> str:
        """Call Gemini API with retry logic (matches HTML exactly)"""

        url = f"{self.base_url}?key={api_key}"

        headers = {
            "Content-Type": "application/json"
        }

        body = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.95,
                "maxOutputTokens": 65536,
                "topP": 0.95,
                "topK": 64
            }
        }

        try:
            logger.info(f"⚙️ Calling Gemini 2.5 Flash API...")
            response = requests.post(url, json=body, headers=headers, timeout=180)

            # Handle rate limits (429 or 503)
            if response.status_code in [429, 503]:
                if retry_count < max_retries:
                    wait_time = (retry_count + 1) * 3  # 3s, 6s, 9s
                    logger.warning(f"⏳ API rate limit hit... waiting {wait_time}s before retry {retry_count + 1}/{max_retries}")
                    time.sleep(wait_time)
                    return self.call_gemini_api(prompt, api_key, retry_count + 1, max_retries)
                else:
                    raise Exception("API rate limit exceeded after retries")

            if not response.ok:
                raise Exception(f"API Error {response.status_code}: {response.text}")

            data = response.json()

            # Extract text from response
            text = data['candidates'][0]['content']['parts'][0]['text'].strip()
            return text

        except requests.exceptions.Timeout:
            if retry_count < max_retries:
                logger.warning(f"⚠️ Request timeout, retry {retry_count + 1}/{max_retries}...")
                time.sleep(2)
                return self.call_gemini_api(prompt, api_key, retry_count + 1, max_retries)
            raise Exception("API request timeout after retries")

        except requests.exceptions.RequestException as e:
            if retry_count < max_retries:
                logger.warning(f"⚠️ Network error, retry {retry_count + 1}/{max_retries}...")
                time.sleep(2)
                return self.call_gemini_api(prompt, api_key, retry_count + 1, max_retries)
            raise Exception(f"Network error: {str(e)}")

    def generate_script(
        self,
        api_key: str,
        target_length: int,
        video_title: str,
        niche: str,
        type_: str,
        style_example: str,
        story_plot: str,
        extra_instructions: str = ""
    ) -> Dict:
        """
        Generate complete script using chunked generation

        Returns:
            {
                "script": "complete script text",
                "stats": {
                    "totalCharacters": int,
                    "totalWords": int,
                    "generationTime": float,
                    "chunksGenerated": int
                }
            }
        """

        start_time = time.time()

        # Calculate chunking
        config = self.get_chunk_config(target_length)
        total_chunks = config['chunks']
        chars_per_chunk = config['chars_per_chunk']

        logger.info(f"✅ Starting script generation...")
        logger.info(f"📝 Niche: {niche}")
        logger.info(f"🎭 Type: {type_}")
        logger.info(f"📏 Target: {target_length} characters")
        logger.info(f"🔧 Config: {total_chunks} chunks × {chars_per_chunk} chars")

        chunks = []

        # Generate chunks
        for i in range(total_chunks):
            chunk_num = i + 1
            logger.info(f"\n🔥 Generating chunk {chunk_num}/{total_chunks}...")

            # Build prompt
            if i == 0:
                # First chunk
                prompt = self.build_first_chunk_prompt(
                    video_title, niche, type_, style_example, story_plot,
                    extra_instructions, chars_per_chunk, total_chunks
                )
            else:
                # Continuation chunks
                prompt = self.build_continuation_prompt(
                    video_title, niche, type_, chunks[-1],
                    chars_per_chunk, chunk_num, total_chunks
                )

            # Call Gemini API
            chunk_text = self.call_gemini_api(prompt, api_key)
            chunks.append(chunk_text)

            logger.info(f"✅ Chunk {chunk_num}/{total_chunks}: {len(chunk_text):,} characters ✓")

            # Wait between chunks (except after last chunk)
            if i < total_chunks - 1:
                logger.info("⏸️ Waiting 1.5s...")
                time.sleep(1.5)

        # Merge chunks
        final_script = '\n\n'.join(chunks)

        # Calculate stats
        generation_time = time.time() - start_time
        total_characters = len(final_script)
        total_words = len(final_script.split())

        logger.info(f"\n🎉 SUCCESS!")
        logger.info(f"📊 Total: {total_characters:,} characters")
        logger.info(f"📝 Words: {total_words:,}")
        logger.info(f"⏱️ Time: {generation_time:.1f} seconds")
        logger.info(f"📦 Chunks merged: {len(chunks)}")

        return {
            "script": final_script,
            "stats": {
                "totalCharacters": total_characters,
                "totalWords": total_words,
                "generationTime": round(generation_time, 2),
                "chunksGenerated": len(chunks)
            }
        }


# Global instance
chunked_script_generator = ChunkedScriptGenerator()
