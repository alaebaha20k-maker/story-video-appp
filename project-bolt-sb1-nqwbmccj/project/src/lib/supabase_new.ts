import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

// Only create Supabase client if credentials are provided
// Gallery feature will be disabled if Supabase is not configured
export const supabase = (supabaseUrl && supabaseAnonKey) 
  ? createClient(supabaseUrl, supabaseAnonKey)
  : null;

export interface SavedVideo {
  id: string;
  topic: string;
  video_path: string;
  story_type: string;
  image_style: string;
  voice_id: string;
  duration: number;
  created_at: string;
}
