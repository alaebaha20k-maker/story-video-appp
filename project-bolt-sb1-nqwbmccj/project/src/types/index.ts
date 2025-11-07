export interface StoryType {
  id: string;
  name: string;
  icon: string;
  description: string;
  bestFor: string;
}

export interface ImageStyle {
  id: string;
  name: string;
  icon: string;
  description: string;
  preview: string;
}

export interface ImageMode {
  id: string;
  name: string;
  icon: string;
  description: string;
  features: string[];
  bestFor: string;
}

export interface Voice {
  id: string;
  name: string;
  icon: string;
  description: string;
  accent: string;
  engine: 'kokoro' | 'edge';
  bestFor: string;
  tone: string;
}

export interface Character {
  name: string;
  description: string;
}

export interface GenerationRequest {
  topic: string;
  story_type: string;
  image_style: string;
  image_mode: string;
  voice_id: string;
  voice_engine?: 'kokoro' | 'edge';
  voice_speed?: number;
  duration: number;
  hook_intensity?: string;
  pacing?: string;
  num_scenes?: number;
  characters?: Character[];
  manual_image_paths?: string[];
  stock_keywords?: string[];
  effects?: string | string[];
}
export interface GenerationProgress {
  status: string;
  progress: number;
  substatus?: string;
  details?: string;
  video_path?: string;
  error?: string;
}

export interface VideoResult {
  videoPath: string;
  topic: string;
  duration: string;
  storyType: string;
  imageStyle: string;
  voice: string;
  generatedAt: Date;
  wordCount?: number;
  sceneCount?: number;
  characters?: string[];
}
