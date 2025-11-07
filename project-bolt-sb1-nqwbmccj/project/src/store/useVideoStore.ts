import { create } from 'zustand';
import { GenerationProgress, VideoResult, Character } from '../types';

interface StockMediaItem {
  id: number;
  type: 'image' | 'video';
  thumbnail: string;
  videoUrl?: string;
  photographer: string;
}

interface VideoStore {
  topic: string;
  storyType: string;
  imageStyle: string;
  imageMode: string;
  voiceId: string;
  voiceEngine: 'kokoro' | 'edge';
  voiceSpeed: number;
  duration: number;
  hookIntensity: string;
  pacing: string;
  numScenes: number;
  characters: Character[];
  manualImages: File[];
  stockKeywords: string[];
  selectedStockMedia: StockMediaItem[];

  // Filters and Effects
  colorFilter: string;
  zoomEffect: boolean;
  
  // Captions
  autoCaptions: boolean;  // NEW: Auto captions from script
  captionEnabled: boolean;
  captionText: string;
  captionStyle: string;
  captionPosition: string;
  captionAnimation: string;

  isGenerating: boolean;
  progress: GenerationProgress | null;
  result: VideoResult | null;
  error: string | null;

  setTopic: (topic: string) => void;
  setStoryType: (type: string) => void;
  setImageStyle: (style: string) => void;
  setImageMode: (mode: string) => void;
  setVoiceId: (id: string) => void;
  setVoiceEngine: (engine: 'kokoro' | 'edge') => void;
  setVoiceSpeed: (speed: number) => void;
  setDuration: (duration: number) => void;
  setHookIntensity: (intensity: string) => void;
  setPacing: (pacing: string) => void;
  setNumScenes: (num: number) => void;
  setCharacters: (characters: Character[]) => void;
  setManualImages: (images: File[]) => void;
  setStockKeywords: (keywords: string[]) => void;
  setSelectedStockMedia: (media: StockMediaItem[]) => void;
  
  setColorFilter: (filter: string) => void;
  setZoomEffect: (enabled: boolean) => void;
  setAutoCaptions: (enabled: boolean) => void;  // NEW
  setCaptionEnabled: (enabled: boolean) => void;
  setCaptionText: (text: string) => void;
  setCaptionStyle: (style: string) => void;
  setCaptionPosition: (position: string) => void;
  setCaptionAnimation: (animation: string) => void;

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
  voiceId: 'af_bella',
  voiceEngine: 'kokoro',
  voiceSpeed: 1.0,
  duration: 5,
  hookIntensity: 'medium',
  pacing: 'medium',
  numScenes: 10,
  characters: [],
  manualImages: [],
  stockKeywords: [],
  selectedStockMedia: [],
  
  // Filters and Effects
  colorFilter: 'none',
  zoomEffect: false,
  
  // Captions
  autoCaptions: false,  // NEW: Auto captions from script
  captionEnabled: false,
  captionText: '',
  captionStyle: 'simple',
  captionPosition: 'bottom',
  captionAnimation: 'fade_in',

  isGenerating: false,
  progress: null,
  result: null,
  error: null,

  setTopic: (topic) => set({ topic }),
  setStoryType: (storyType) => set({ storyType }),
  setImageStyle: (imageStyle) => set({ imageStyle }),
  setImageMode: (imageMode) => set({ imageMode }),
  setVoiceId: (voiceId) => set({ voiceId }),
  setVoiceEngine: (voiceEngine) => set({ voiceEngine }),
  setVoiceSpeed: (voiceSpeed) => set({ voiceSpeed: Math.max(0.5, Math.min(2.0, voiceSpeed)) }),
  setDuration: (duration) => set({ duration }),
  setHookIntensity: (hookIntensity) => set({ hookIntensity }),
  setPacing: (pacing) => set({ pacing }),
  setNumScenes: (numScenes) => set({ numScenes }),
  setCharacters: (characters) => set({ characters }),
  setManualImages: (manualImages) => set({ manualImages }),
  setStockKeywords: (stockKeywords) => set({ stockKeywords }),
  setSelectedStockMedia: (selectedStockMedia) => set({ selectedStockMedia }),
  
  setColorFilter: (colorFilter) => set({ colorFilter }),
  setZoomEffect: (zoomEffect) => set({ zoomEffect }),
  setAutoCaptions: (autoCaptions) => set({ autoCaptions }),  // NEW
  setCaptionEnabled: (captionEnabled) => set({ captionEnabled }),
  setCaptionText: (captionText) => set({ captionText }),
  setCaptionStyle: (captionStyle) => set({ captionStyle }),
  setCaptionPosition: (captionPosition) => set({ captionPosition }),
  setCaptionAnimation: (captionAnimation) => set({ captionAnimation }),

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