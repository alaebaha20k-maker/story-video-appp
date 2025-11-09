import { create } from 'zustand';
import { GenerationProgress, VideoResult, Character } from '../types';

interface VideoStore {
  topic: string;
  storyType: string;
  imageStyle: string;
  imageMode: string;
  voiceId: string;
  voiceSpeed: number;              // ✅ NEW: Voice speed control (0.5-2.0)
  duration: number;
  hookIntensity: string;
  pacing: string;
  numScenes: number;
  characters: Character[];
  manualImages: File[];
  stockKeywords: string[];

  isGenerating: boolean;
  progress: GenerationProgress | null;
  result: VideoResult | null;
  error: string | null;

  setTopic: (topic: string) => void;
  setStoryType: (type: string) => void;
  setImageStyle: (style: string) => void;
  setImageMode: (mode: string) => void;
  setVoiceId: (id: string) => void;
  setVoiceSpeed: (speed: number) => void;               // ✅ NEW
  setDuration: (duration: number) => void;
  setHookIntensity: (intensity: string) => void;
  setPacing: (pacing: string) => void;
  setNumScenes: (num: number) => void;
  setCharacters: (characters: Character[]) => void;
  setManualImages: (images: File[]) => void;
  setStockKeywords: (keywords: string[]) => void;

  startGeneration: () => void;
  updateProgress: (progress: GenerationProgress) => void;
  setResult: (result: VideoResult) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

export const useVideoStore = create<VideoStore>((set) => ({
  topic: '',
  storyType: 'scary_horror',
  imageStyle: 'cinematic',
  imageMode: 'ai_only',
  voiceId: 'male_narrator_deep',  // ✅ Default Edge alias
  voiceSpeed: 1.0,        // ✅ NEW: Normal speed
  duration: 5,
  hookIntensity: 'medium',
  pacing: 'medium',
  numScenes: 10,
  characters: [],
  manualImages: [],
  stockKeywords: [],

  isGenerating: false,
  progress: null,
  result: null,
  error: null,

  setTopic: (topic) => set({ topic }),
  setStoryType: (storyType) => set({ storyType }),
  setImageStyle: (imageStyle) => set({ imageStyle }),
  setImageMode: (imageMode) => set({ imageMode }),
  setVoiceId: (voiceId) => set({ voiceId }),
  setVoiceSpeed: (voiceSpeed) => set({ voiceSpeed: Math.max(0.5, Math.min(2.0, voiceSpeed)) }),  // ✅ NEW: Clamp 0.5-2.0
  setDuration: (duration) => set({ duration }),
  setHookIntensity: (hookIntensity) => set({ hookIntensity }),
  setPacing: (pacing) => set({ pacing }),
  setNumScenes: (numScenes) => set({ numScenes }),
  setCharacters: (characters) => set({ characters }),
  setManualImages: (manualImages) => set({ manualImages }),
  setStockKeywords: (stockKeywords) => set({ stockKeywords }),

  startGeneration: () => set({ isGenerating: true, progress: null, result: null, error: null }),
  updateProgress: (progress) => set({ progress }),
  setResult: (result) => set({ result, isGenerating: false }),
  setError: (error) => set({ error, isGenerating: false }),
  reset: () =>
    set({
      isGenerating: false,
      progress: null,
      result: null,
      error: null,
    }),
}));