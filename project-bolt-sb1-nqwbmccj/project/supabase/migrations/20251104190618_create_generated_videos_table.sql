/*
  # Create Generated Videos Table

  1. New Tables
    - `generated_videos`
      - `id` (uuid, primary key) - Unique identifier for each video
      - `topic` (text) - The story topic provided by user
      - `video_path` (text) - Path/filename of the generated video
      - `story_type` (text) - Type of story (horror, emotional, etc.)
      - `image_style` (text) - Visual style used (cinematic, anime, etc.)
      - `voice_id` (text) - Voice narrator used
      - `duration` (integer) - Video duration in minutes
      - `created_at` (timestamptz) - Timestamp of creation
  
  2. Security
    - Enable RLS on `generated_videos` table
    - Add policy for public read access (since this is a demo app)
    - Add policy for public insert access (for saving generated videos)
    - Add policy for public delete access (for removing videos)
  
  3. Indexes
    - Create index on created_at for efficient sorting
  
  4. Notes
    - This table stores metadata about generated videos
    - Video files themselves are served from the API server
    - Public access enabled for demo purposes
*/

CREATE TABLE IF NOT EXISTS generated_videos (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  topic text NOT NULL,
  video_path text NOT NULL,
  story_type text NOT NULL,
  image_style text NOT NULL,
  voice_id text NOT NULL,
  duration integer NOT NULL DEFAULT 5,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE generated_videos ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access"
  ON generated_videos
  FOR SELECT
  USING (true);

CREATE POLICY "Allow public insert access"
  ON generated_videos
  FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Allow public delete access"
  ON generated_videos
  FOR DELETE
  USING (true);

CREATE INDEX IF NOT EXISTS idx_generated_videos_created_at 
  ON generated_videos(created_at DESC);