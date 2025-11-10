"""
🤖 PUTER AI INTEGRATION - Access to 500+ AI Models (FREE!)
Claude Sonnet 4, GPT-4, Gemini, and more!
"""

import requests
from typing import Optional, Dict, Any
import time

class PuterAI:
    """Puter AI - Free access to Claude, GPT, Gemini, and 500+ models!"""
    
    def __init__(self):
        """Initialize Puter AI - No API key needed!"""
        self.chat_url = 'https://api.puter.com/drivers/call'
        
        print(f"🤖 Puter AI initialized")
        print(f"   ✅ FREE access to 500+ AI models!")
        print(f"   ✅ No API key required!")
        print(f"   🏆 Claude Sonnet 4, GPT-4, Gemini available!")
    
    def chat(
        self,
        prompt: str,
        model: str = 'claude-sonnet-4',
        temperature: float = 0.75,
        max_tokens: int = 16384
    ) -> str:
        """Chat with AI models via Puter
        
        Args:
            prompt: Your prompt/question
            model: Model to use (default: claude-sonnet-4 - BEST for stories!)
            temperature: 0-1, creativity level
            max_tokens: Maximum response length
        
        Returns:
            AI-generated text response
        """
        
        print(f"\n🤖 Generating with {model.upper()}...")
        print(f"   Prompt length: {len(prompt)} characters")
        print(f"   Temperature: {temperature}")
        print(f"   Max tokens: {max_tokens}")
        
        start_time = time.time()
        
        try:
            # Prepare Puter API request
            headers = {
                'Content-Type': 'application/json'
            }
            
            payload = {
                'interface': 'puter-chat-completion',
                'driver': 'anthropic',  # For Claude
                'method': 'complete',
                'args': {
                    'messages': [
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ],
                    'model': model,
                    'temperature': temperature,
                    'max_tokens': max_tokens
                }
            }
            
            # Make API call to Puter
            print(f"   📡 Calling Puter AI API...")
            response = requests.post(
                self.chat_url,
                json=payload,
                headers=headers,
                timeout=180  # 3 minutes for long scripts
            )
            
            if not response.ok:
                error_msg = response.text[:500]
                print(f"   ❌ API Error: {response.status_code}")
                print(f"   Details: {error_msg}")
                raise Exception(f"❌ Puter AI error {response.status_code}: {error_msg}")
            
            # Get response
            result = response.json()
            
            # Extract text from response
            if 'message' in result and 'content' in result['message']:
                text = result['message']['content']
            elif 'content' in result:
                text = result['content']
            elif 'text' in result:
                text = result['text']
            else:
                raise Exception(f"Unexpected response format: {list(result.keys())}")
            
            duration = time.time() - start_time
            
            print(f"✅ {model.upper()} generation SUCCESS!")
            print(f"   Generated: {len(text)} characters")
            print(f"   Words: {len(text.split())} words")
            print(f"   Generation time: {duration:.1f} seconds")
            print(f"   🏆 Using BEST model for storytelling!")
            
            return text
        
        except requests.exceptions.Timeout:
            raise Exception(f"❌ Puter AI timeout after 180s")
        except requests.exceptions.ConnectionError as e:
            raise Exception(f"❌ Puter AI connection error: {e}")
        except Exception as e:
            print(f"\n{'='*60}")
            print(f"❌ PUTER AI GENERATION FAILED!")
            print(f"{'='*60}")
            print(f"Error: {e}")
            print(f"Model: {model}")
            print(f"\n💡 Troubleshooting:")
            print(f"   1. Check internet connection")
            print(f"   2. Verify api.puter.com is accessible")
            print(f"   3. Try different model (claude, gpt-4, gemini)")
            print(f"   4. Check prompt length")
            print(f"{'='*60}\n")
            raise


def create_puter_ai() -> PuterAI:
    """Create Puter AI instance - No API key needed!"""
    return PuterAI()


# Test if module is run directly
if __name__ == "__main__":
    print("🔍 Testing Puter AI...")
    
    # Create instance
    ai = create_puter_ai()
    
    # Test with Claude Sonnet 4
    print("\n🧪 Testing Claude Sonnet 4...")
    try:
        response = ai.chat(
            "Write a 2-sentence horror story hook.",
            model='claude-sonnet-4',
            temperature=0.75,
            max_tokens=200
        )
        print(f"\n✅ Claude Response:\n{response}\n")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test with GPT
    print("\n🧪 Testing GPT-4...")
    try:
        response = ai.chat(
            "Write a 2-sentence romance story hook.",
            model='gpt-4',
            temperature=0.75,
            max_tokens=200
        )
        print(f"\n✅ GPT-4 Response:\n{response}\n")
    except Exception as e:
        print(f"❌ Error: {e}")
