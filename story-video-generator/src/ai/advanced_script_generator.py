"""
🚀 ADVANCED SCRIPT GENERATOR - Smart Chunking + Separate API Keys
Solves quota limits with intelligent chunking and dedicated API keys
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import google.generativeai as genai
from typing import Dict, List, Optional
import re
import time
import math

from config.settings import GEMINI_SETTINGS, GEMINI_API_KEYS
from config.story_types import STORY_TYPES
from src.utils.logger import logger


class AdvancedScriptGenerator:
    """🎯 ULTIMATE Script Generator - Solves quota limits with smart chunking"""
    
    def __init__(self):
        # ✅ Separate API keys for different tasks
        self.script_api_key = GEMINI_API_KEYS["script_generation"]
        self.image_api_key = GEMINI_API_KEYS["image_prompts"]
        
        # ✅ Smart chunking settings
        self.max_chars_per_chunk = GEMINI_SETTINGS["max_chars_per_chunk"]  # 12,000 chars
        self.chunk_overlap = GEMINI_SETTINGS["chunk_overlap"]  # 200 chars
        
        print(f"🚀 Advanced Script Generator initialized")
        print(f"   Script API Key: ...{self.script_api_key[-8:]}")
        print(f"   Image API Key: ...{self.image_api_key[-8:]}")
        print(f"   Smart Chunking: {self.max_chars_per_chunk:,} chars per chunk")
        print(f"   Chunk Overlap: {self.chunk_overlap} chars")
    
    def generate_perfect_script(
        self,
        topic: str,
        story_type: str,
        duration_minutes: int = 24,
        num_scenes: int = 10,
        template: Optional[Dict] = None,
        research_data: Optional[str] = None
    ) -> Dict:
        """
        🎯 Generate PERFECT script with smart chunking to avoid quota limits
        
        Strategy:
        1. Calculate target length
        2. Determine optimal chunk count
        3. Generate script in chunks with overlap
        4. Merge chunks seamlessly
        5. Generate image prompts separately (different API key)
        """
        
        if story_type not in STORY_TYPES:
            story_type = "scary_horror"
        
        style = STORY_TYPES[story_type]
        
        # Calculate target script length
        target_chars = duration_minutes * 150 * 5  # 150 words/min × 5 chars/word
        
        logger.info(f"🎬 Generating {duration_minutes}-minute script")
        logger.info(f"   Target: {target_chars:,} characters")
        logger.info(f"   Topic: {topic}")
        logger.info(f"   Style: {style['name']}")
        
        # ✅ SMART CHUNKING - Calculate optimal chunks
        num_chunks = self._calculate_optimal_chunks(target_chars)
        chars_per_chunk = target_chars // num_chunks
        
        logger.info(f"   Strategy: {num_chunks} chunks × {chars_per_chunk:,} chars each")
        
        if num_chunks == 1:
            # Single chunk - generate normally
            return self._generate_single_chunk(
                topic, style, target_chars, num_scenes, template, research_data
            )
        else:
            # Multi-chunk - advanced generation
            return self._generate_multi_chunk(
                topic, style, target_chars, num_chunks, num_scenes, template, research_data
            )
    
    def _calculate_optimal_chunks(self, target_chars: int) -> int:
        """Calculate optimal number of chunks to avoid quota limits"""
        
        if target_chars <= 8000:  # 8-10 min videos
            return 1
        elif target_chars <= 15000:  # 15-20 min videos
            return 2
        elif target_chars <= 25000:  # 25-30 min videos
            return 3
        elif target_chars <= 40000:  # 40-50 min videos
            return 4
        else:  # 60+ min videos
            return max(4, math.ceil(target_chars / 12000))  # Max 12k per chunk
    
    def _generate_single_chunk(
        self,
        topic: str,
        style: Dict,
        target_chars: int,
        num_scenes: int,
        template: Optional[Dict],
        research_data: Optional[str]
    ) -> Dict:
        """Generate script in single API call (for shorter videos)"""
        
        logger.info("📝 Single-chunk generation (fast mode)")
        
        # Configure Gemini for script generation
        genai.configure(api_key=self.script_api_key)
        model = genai.GenerativeModel(
            model_name=GEMINI_SETTINGS['model'],
            generation_config={
                "temperature": 0.75,
                "top_p": 0.92,
                "top_k": 50,
                "max_output_tokens": 8192,
            }
        )
        
        # Build prompt
        prompt = self._build_script_prompt(
            topic=topic,
            style=style,
            target_chars=target_chars,
            num_scenes=num_scenes,
            template=template,
            research_data=research_data,
            chunk_info=None
        )
        
        # Generate script
        response = model.generate_content(prompt)
        script_text = self._clean_script(response.text)
        
        # Generate image prompts separately
        image_prompts = self._generate_image_prompts_separately(
            script_text, topic, style, num_scenes
        )
        
        # Extract metadata
        characters = self._extract_characters(script_text)
        scenes = self._parse_scenes_from_script(script_text, num_scenes)
        
        logger.success(f"✅ Generated {len(script_text):,} characters")
        
        return {
            "script": script_text,
            "characters": characters,
            "scenes": scenes,
            "image_prompts": image_prompts,
            "story_type": story_type,
            "word_count": len(script_text.split()),
            "character_count": len(script_text),
            "chunks_used": 1,
            "generation_method": "single_chunk"
        }
    
    def _generate_multi_chunk(
        self,
        topic: str,
        style: Dict,
        target_chars: int,
        num_chunks: int,
        num_scenes: int,
        template: Optional[Dict],
        research_data: Optional[str]
    ) -> Dict:
        """Generate script in multiple chunks with seamless merging"""
        
        logger.info(f"📝 Multi-chunk generation ({num_chunks} chunks)")
        
        # Configure Gemini for script generation
        genai.configure(api_key=self.script_api_key)
        model = genai.GenerativeModel(
            model_name=GEMINI_SETTINGS['model'],
            generation_config={
                "temperature": 0.75,
                "top_p": 0.92,
                "top_k": 50,
                "max_output_tokens": 6000,  # Smaller chunks
            }
        )
        
        chars_per_chunk = target_chars // num_chunks
        script_chunks = []
        
        # Generate each chunk
        for chunk_num in range(num_chunks):
            logger.info(f"   Generating chunk {chunk_num + 1}/{num_chunks}...")
            
            chunk_info = {
                "chunk_number": chunk_num + 1,
                "total_chunks": num_chunks,
                "target_chars": chars_per_chunk,
                "is_first": chunk_num == 0,
                "is_last": chunk_num == num_chunks - 1,
                "previous_ending": script_chunks[-1][-200:] if script_chunks else None
            }
            
            # Build chunk-specific prompt
            prompt = self._build_script_prompt(
                topic=topic,
                style=style,
                target_chars=chars_per_chunk,
                num_scenes=num_scenes // num_chunks,
                template=template,
                research_data=research_data,
                chunk_info=chunk_info
            )
            
            # Generate chunk with retry
            for attempt in range(3):
                try:
                    response = model.generate_content(prompt)
                    chunk_text = self._clean_script(response.text)
                    
                    if len(chunk_text) > 500:  # Valid chunk
                        script_chunks.append(chunk_text)
                        logger.info(f"     ✅ Chunk {chunk_num + 1}: {len(chunk_text):,} chars")
                        break
                    else:
                        logger.warning(f"     ⚠️ Chunk {chunk_num + 1} too short, retrying...")
                        
                except Exception as e:
                    logger.error(f"     ❌ Chunk {chunk_num + 1} failed: {e}")
                    if attempt == 2:
                        raise
                    time.sleep(2)
            
            # Rate limiting between chunks
            if chunk_num < num_chunks - 1:
                logger.info(f"     ⏱️ Waiting 8s before next chunk...")
                time.sleep(8)
        
        # Merge chunks seamlessly
        full_script = self._merge_chunks_seamlessly(script_chunks)
        
        # Generate image prompts separately
        image_prompts = self._generate_image_prompts_separately(
            full_script, topic, style, num_scenes
        )
        
        # Extract metadata
        characters = self._extract_characters(full_script)
        scenes = self._parse_scenes_from_script(full_script, num_scenes)
        
        logger.success(f"✅ Generated {len(full_script):,} characters from {num_chunks} chunks")
        
        return {
            "script": full_script,
            "characters": characters,
            "scenes": scenes,
            "image_prompts": image_prompts,
            "story_type": story_type,
            "word_count": len(full_script.split()),
            "character_count": len(full_script),
            "chunks_used": num_chunks,
            "generation_method": "multi_chunk"
        }
    
    def _generate_image_prompts_separately(
        self,
        script_text: str,
        topic: str,
        style: Dict,
        num_scenes: int
    ) -> List[Dict]:
        """Generate image prompts using separate API key"""
        
        logger.info(f"🎨 Generating {num_scenes} image prompts (separate API key)")
        
        # Configure Gemini for image prompts
        genai.configure(api_key=self.image_api_key)
        model = genai.GenerativeModel(
            model_name=GEMINI_SETTINGS['model'],
            generation_config={
                "temperature": 0.8,  # More creative for images
                "top_p": 0.95,
                "top_k": 60,
                "max_output_tokens": 4000,
            }
        )
        
        # Build image prompt generation prompt
        prompt = f"""
Generate {num_scenes} detailed image prompts for SDXL image generation based on this script.

SCRIPT:
{script_text[:3000]}...

TOPIC: {topic}
STYLE: {style['name']}

Create {num_scenes} image prompts that:
1. Match key moments in the script
2. Are optimized for SDXL generation
3. Include cinematic details
4. Vary in composition and mood

Format as JSON array:
[
  {{
    "scene_number": 1,
    "image_prompt": "detailed SDXL prompt here",
    "mood": "description",
    "composition": "shot type"
  }},
  ...
]

Generate exactly {num_scenes} prompts:
"""
        
        try:
            response = model.generate_content(prompt)
            prompts_text = response.text
            
            # Parse JSON or extract prompts
            image_prompts = self._parse_image_prompts(prompts_text, num_scenes)
            
            logger.success(f"✅ Generated {len(image_prompts)} image prompts")
            return image_prompts
            
        except Exception as e:
            logger.error(f"❌ Image prompt generation failed: {e}")
            # Fallback: Generate simple prompts
            return self._generate_fallback_image_prompts(topic, style, num_scenes)
    
    def _build_script_prompt(
        self,
        topic: str,
        style: Dict,
        target_chars: int,
        num_scenes: int,
        template: Optional[Dict],
        research_data: Optional[str],
        chunk_info: Optional[Dict]
    ) -> str:
        """Build optimized prompt for script generation"""
        
        if chunk_info:
            # Multi-chunk prompt
            chunk_context = f"""
CHUNK INFORMATION:
- This is chunk {chunk_info['chunk_number']} of {chunk_info['total_chunks']}
- Target length: {chunk_info['target_chars']:,} characters
- {"OPENING chunk - start the story" if chunk_info['is_first'] else ""}
- {"CLOSING chunk - end the story" if chunk_info['is_last'] else ""}
- {"MIDDLE chunk - continue the narrative" if not chunk_info['is_first'] and not chunk_info['is_last'] else ""}

{f"PREVIOUS CHUNK ENDING: ...{chunk_info['previous_ending']}" if chunk_info['previous_ending'] else ""}

Continue the narrative seamlessly from the previous chunk.
"""
        else:
            chunk_context = ""
        
        template_context = ""
        if template:
            template_context = f"""
TEMPLATE STRUCTURE:
{template}

Follow this template structure for consistency.
"""
        
        research_context = ""
        if research_data:
            research_context = f"""
RESEARCH DATA:
{research_data[:1000]}...

Incorporate these facts naturally into the narrative.
"""
        
        return f"""
Create a {style['name']} script about: {topic}

TARGET LENGTH: {target_chars:,} characters
SCENES: {num_scenes} scenes
STYLE: {style['description']}
TONE: {style['tone']}

{chunk_context}
{template_context}
{research_context}

REQUIREMENTS:
1. Write ONLY the narrative script (no image prompts)
2. Make it exactly {target_chars:,} characters long
3. Use engaging storytelling techniques
4. Include dialogue and descriptions
5. Create natural scene transitions
6. Focus on emotional impact

Write the script now:
"""
    
    def _clean_script(self, script_text: str) -> str:
        """Clean and format script text"""
        # Remove common AI artifacts
        script_text = re.sub(r'^(Script:|SCRIPT:|Here\'s|Here is)', '', script_text, flags=re.IGNORECASE)
        script_text = re.sub(r'```.*?```', '', script_text, flags=re.DOTALL)
        script_text = re.sub(r'\*\*.*?\*\*', '', script_text)
        script_text = re.sub(r'IMAGE:.*?\n', '', script_text, flags=re.IGNORECASE)
        
        # Clean whitespace
        script_text = re.sub(r'\n\s*\n\s*\n', '\n\n', script_text)
        script_text = script_text.strip()
        
        return script_text
    
    def _merge_chunks_seamlessly(self, chunks: List[str]) -> str:
        """Merge script chunks with seamless transitions"""
        if len(chunks) == 1:
            return chunks[0]
        
        merged = chunks[0]
        
        for i in range(1, len(chunks)):
            # Find overlap and merge smoothly
            chunk = chunks[i]
            
            # Remove potential duplicate sentences at chunk boundaries
            merged_sentences = merged.split('.')
            chunk_sentences = chunk.split('.')
            
            # Check for overlap in last few sentences
            overlap_found = False
            for j in range(min(3, len(merged_sentences), len(chunk_sentences))):
                if merged_sentences[-(j+1)].strip() == chunk_sentences[j].strip():
                    # Remove overlap
                    chunk = '.'.join(chunk_sentences[j+1:])
                    overlap_found = True
                    break
            
            # Add transition if needed
            if not merged.endswith('.') and not merged.endswith('!') and not merged.endswith('?'):
                merged += '.'
            
            merged += ' ' + chunk
        
        return merged.strip()
    
    def _extract_characters(self, script_text: str) -> List[str]:
        """Extract character names from script"""
        # Look for dialogue patterns
        characters = set()
        
        # Pattern: "Name:" or "NAME:"
        dialogue_pattern = r'^([A-Z][a-zA-Z\s]+):'
        matches = re.findall(dialogue_pattern, script_text, re.MULTILINE)
        characters.update(matches)
        
        # Pattern: quoted speech attribution
        attribution_pattern = r'said ([A-Z][a-zA-Z\s]+)'
        matches = re.findall(attribution_pattern, script_text)
        characters.update(matches)
        
        return list(characters)[:5]  # Max 5 characters
    
    def _parse_scenes_from_script(self, script_text: str, num_scenes: int) -> List[Dict]:
        """Parse scenes from script text"""
        # Split script into roughly equal scenes
        sentences = script_text.split('.')
        sentences_per_scene = len(sentences) // num_scenes
        
        scenes = []
        for i in range(num_scenes):
            start_idx = i * sentences_per_scene
            end_idx = (i + 1) * sentences_per_scene if i < num_scenes - 1 else len(sentences)
            
            scene_text = '.'.join(sentences[start_idx:end_idx]).strip()
            if scene_text:
                scenes.append({
                    'scene_number': i + 1,
                    'content': scene_text,
                    'image_description': f"Scene {i + 1} from the story"
                })
        
        return scenes
    
    def _parse_image_prompts(self, prompts_text: str, num_scenes: int) -> List[Dict]:
        """Parse image prompts from AI response"""
        try:
            # Try to extract JSON
            import json
            json_match = re.search(r'\[.*\]', prompts_text, re.DOTALL)
            if json_match:
                prompts_data = json.loads(json_match.group())
                return prompts_data[:num_scenes]
        except:
            pass
        
        # Fallback: Extract prompts manually
        prompts = []
        lines = prompts_text.split('\n')
        
        for i, line in enumerate(lines):
            if 'image_prompt' in line.lower() or f'{i+1}.' in line:
                prompt_text = re.sub(r'^\d+\.|\*|-', '', line).strip()
                if len(prompt_text) > 20:
                    prompts.append({
                        'scene_number': len(prompts) + 1,
                        'image_prompt': prompt_text,
                        'mood': 'cinematic',
                        'composition': 'wide shot'
                    })
                    
                    if len(prompts) >= num_scenes:
                        break
        
        return prompts[:num_scenes]
    
    def _generate_fallback_image_prompts(self, topic: str, style: Dict, num_scenes: int) -> List[Dict]:
        """Generate simple fallback image prompts"""
        base_prompt = f"{topic}, {style['description']}, cinematic style"
        
        prompts = []
        for i in range(num_scenes):
            prompts.append({
                'scene_number': i + 1,
                'image_prompt': f"{base_prompt}, scene {i + 1}",
                'mood': style.get('tone', 'dramatic'),
                'composition': 'cinematic shot'
            })
        
        return prompts


# Global instance
advanced_script_generator = AdvancedScriptGenerator()
