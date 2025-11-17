import { useVideoStore } from '../store/useVideoStore';

const API_URL = 'http://localhost:5000';

// ✅ HEALTH CHECK
export const checkHealth = async (): Promise<boolean> => {
  try {
    const response = await fetch(`${API_URL}/health`, {
      method: 'GET',
    });
    return response.ok;
  } catch (error) {
    console.error('Health check failed:', error);
    return false;
  }
};

interface GenerateVideoRequest {
  topic: string;
  story_type: string;  // Fixed: was "storytype"
  duration: number;
  image_style: string;
  image_mode: string;
  voice_id: string;
  voice_engine?: string;
  voice_speed?: number;
  num_scenes: number;
  hook_intensity: string;
  pacing: string;
  characters?: any[];
  stock_keywords?: string[];
  // NEW: Effects and options
  zoom_effect?: boolean;
  zoom_intensity?: number;
  auto_captions?: boolean;
  color_filter?: string;
  template?: any;  // Optional template from script analysis
}

// ✅ GENERATE VIDEO (NEW FLOW: Gemini 1 → Gemini 2 → Colab)
export const generateVideo = async (requestData: GenerateVideoRequest) => {
  try {
    console.log('🚀 Sending to NEW backend (Gemini 1 → 2 → Colab):', requestData);

    const response = await fetch(`${API_URL}/api/generate-video`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP error! status: ${response.status}: ${errorText}`);
    }

    const result = await response.json();
    console.log('✅ Backend response:', result);
    return result;
  } catch (error) {
    console.error('❌ Generation failed:', error);
    throw error;
  }
};

// ✅ GET PROGRESS
export const getProgress = async () => {
  try {
    const response = await fetch(`${API_URL}/api/progress`);
    if (!response.ok) throw new Error('Failed to fetch progress');
    return await response.json();
  } catch (error) {
    console.error('Progress fetch failed:', error);
    throw error;
  }
};

// ✅ GET VIDEO URL
export const getVideoUrl = (filename: string) => {
  return `${API_URL}/api/video/${filename}`;
};

// ✅ GET AVAILABLE VOICES
export const getAvailableVoices = async () => {
  try {
    const response = await fetch(`${API_URL}/api/voices`);
    if (!response.ok) throw new Error('Failed to fetch voices');
    return await response.json();
  } catch (error) {
    console.error('Voices fetch failed:', error);
    throw error;
  }
};

// ✅ GET AVAILABLE EFFECTS
export const getAvailableEffects = async () => {
  try {
    const response = await fetch(`${API_URL}/api/available-effects`);
    if (!response.ok) throw new Error('Failed to fetch effects');
    return await response.json();
  } catch (error) {
    console.error('Effects fetch failed:', error);
    throw error;
  }
};

// ✅ GENERATE VIDEO WITH EFFECTS
export const generateVideoWithEffects = async (
  requestData: GenerateVideoRequest & { effects: string | string[] }
) => {
  try {
    const response = await fetch(`${API_URL}/api/generate-video-with-effects`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Generation with effects failed:', error);
    throw error;
  }
};