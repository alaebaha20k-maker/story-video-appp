import { useEffect, useState } from 'react';
import { useVideoStore } from '../store/useVideoStore';
import { generateVideo, getProgress } from '../utils/api';
import { supabase } from '../lib/supabase';
import { BasicSettings } from '../components/BasicSettings';
import { StoryTypeSelector } from '../components/StoryTypeSelector';
import { AdvancedSettings } from '../components/AdvancedSettings';
import { ImageStyleSelector } from '../components/ImageStyleSelector';
import { ImageModeSelector } from '../components/ImageModeSelector';
import { ImageUpload } from '../components/ImageUpload';
import { StockKeywords } from '../components/StockKeywords';
import { StockMediaSelector } from '../components/StockMediaSelector';
import { VoiceSelector } from '../components/VoiceSelector';
import { CharacterManager } from '../components/CharacterManager';
import { GenerateButton } from '../components/GenerateButton';
import { GenerationProgress } from '../components/GenerationProgress';
import { VideoResult } from '../components/VideoResult';
import { ExampleScriptUpload } from '../components/ExampleScriptUpload';
import { VideoFilters } from '../components/VideoFilters';
import { CaptionEditor } from '../components/CaptionEditor';
import toast, { Toaster } from 'react-hot-toast';

interface ExampleScript {
  id: string;
  name: string;
  content: string;
  type: string;
  hookStyle: string;
  structure: string;
  uploadedAt: string;
}

interface AnalyzedTemplate {
  hookExample: string;
  hookStyle: string;
  setupLength: number;
  riseLength: number;
  climaxLength: number;
  endLength: number;
  tone: string[];
  keyPatterns: string[];
  sentenceVariation: string;
}

export const GeneratorPage = () => {
  const store = useVideoStore();
  const [isPolling, setIsPolling] = useState(false);
  
  const [selectedExample, setSelectedExample] = useState<ExampleScript | null>(null);
  const [template, setTemplate] = useState<AnalyzedTemplate | null>(null);

  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;

    if (isPolling) {
      interval = setInterval(async () => {
        try {
          const progress = await getProgress();
          store.updateProgress(progress);

          if (progress.status === 'complete' && progress.video_path) {
            setIsPolling(false);

            const result = {
              videoPath: progress.video_path,
              topic: store.topic,
              duration: `${store.duration} min`,
              storyType: store.storyType,
              imageStyle: store.imageStyle,
              voice: store.voiceId,
              generatedAt: new Date(),
              sceneCount: store.numScenes,
            };

            store.setResult(result);

            // Save to gallery if Supabase is configured
            if (supabase) {
              try {
                await supabase.from('generated_videos').insert({
                  topic: store.topic,
                  video_path: progress.video_path,
                  story_type: store.storyType,
                  image_style: store.imageStyle,
                  voice_id: store.voiceId,
                  duration: store.duration,
                });
              } catch (err) {
                console.error('Failed to save to gallery:', err);
              }
            }

            toast.success('Video generated successfully!');
          } else if (progress.error) {
            setIsPolling(false);
            store.setError(progress.error);
            toast.error(progress.error);
          }
        } catch (error) {
          setIsPolling(false);
          const message = error instanceof Error ? error.message : 'Failed to check progress';
          store.setError(message);
          toast.error(message);
        }
      }, 1000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isPolling, store]);

  const handleGenerateWithTemplate = async () => {
    if (!store.topic.trim()) {
      toast.error('Please enter a story topic');
      return;
    }

    if (!template) {
      toast.error('Please load a template first');
      return;
    }

    try {
      store.startGeneration();
      toast.loading('Starting generation with template...');

      const response = await fetch('http://localhost:5000/api/generate-with-template', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: store.topic,
          story_type: store.storyType,
          template: template,
          research_data: null,
          duration: store.duration,
          num_scenes: store.numScenes,
          // ✅ ADD ALL SETTINGS (voice, zoom, filters, effects!)
          voice_id: store.voiceId,
          voice_engine: store.voiceEngine,
          zoom_effect: store.zoomEffect,
          color_filter: store.colorFilter,
          visual_effects: false,  // Will add toggle later
          auto_captions: store.autoCaptions,
          srt_subtitles: false,  // Can enable later if needed
          emotion_captions: true,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Generation failed');
      }

      toast.dismiss();
      setIsPolling(true);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to start generation';
      store.setError(message);
      toast.error(message);
    }
  };

  const handleGenerate = async () => {
    if (!store.topic.trim()) {
      toast.error('Please enter a story topic');
      return;
    }

    try {
      store.startGeneration();
      toast.loading('Starting generation...');

      await generateVideo({
        topic: store.topic,
        story_type: store.storyType,
        image_style: store.imageStyle,
        image_mode: store.imageMode,
        voice_id: store.voiceId,
        voice_engine: store.voiceEngine,
        voice_speed: store.voiceSpeed,
        duration: store.duration,
        hook_intensity: store.hookIntensity,
        pacing: store.pacing,
        num_scenes: store.numScenes,
        characters: store.characters.filter(c => c.name && c.description),
        stock_keywords: store.stockKeywords,
        // Filters and Effects
        color_filter: store.colorFilter,
        zoom_effect: store.zoomEffect,
        // Auto Captions (NEW!)
        auto_captions: store.autoCaptions,
        // Manual Captions (single text)
        caption: store.captionEnabled ? {
          text: store.captionText,
          style: store.captionStyle,
          position: store.captionPosition,
          animation: store.captionAnimation,
        } : undefined,
      });

      toast.dismiss();
      setIsPolling(true);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to start generation';
      store.setError(message);
      toast.error(message);
    }
  };

  const handleGenerateAnother = () => {
    store.reset();
    setIsPolling(false);
    setTemplate(null);
    setSelectedExample(null);
  };

  const showUpload = store.imageMode.includes('manual');
  const showStock = store.imageMode.includes('stock');

  if (store.result) {
    return (
      <div className="max-w-5xl mx-auto p-4 space-y-6">
        <Toaster position="top-right" />
        <VideoResult result={store.result} onGenerateAnother={handleGenerateAnother} />
      </div>
    );
  }

  if (store.isGenerating && store.progress) {
    return (
      <div className="max-w-4xl mx-auto p-4">
        <Toaster position="top-right" />
        <GenerationProgress
          progress={store.progress.progress}
          status={store.progress.status}
          substatus={store.progress.substatus}
          details={store.progress.details}
        />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-4 space-y-6">
      <Toaster position="top-right" />

      {/* Example Script Upload */}
      <ExampleScriptUpload 
        onScriptSelected={setSelectedExample}
        onTemplateExtracted={setTemplate}
      />

      <BasicSettings />
      <StoryTypeSelector />
      <AdvancedSettings />
      <ImageStyleSelector />
      <ImageModeSelector />

      {showUpload && <ImageUpload />}
      {showStock && (
        <>
          <StockKeywords />
          <StockMediaSelector />
        </>
      )}

      {/* ✅ VOICE SELECTOR - NOW VISIBLE */}
      <VoiceSelector />
      
      <CharacterManager />
      
      {/* ✨ FILTERS AND EFFECTS */}
      <VideoFilters />
      
      {/* 📝 CAPTIONS */}
      <CaptionEditor />

      {/* Two Generate Buttons */}
      <div className="grid grid-cols-2 gap-4">
        {/* Generate WITH Template */}
        <button
          onClick={handleGenerateWithTemplate}
          disabled={store.isGenerating || !store.topic.trim() || !template}
          className={`p-4 rounded-lg font-bold text-white transition ${
            template && !store.isGenerating
              ? 'bg-gradient-to-r from-green-600 to-green-500 hover:from-green-700 hover:to-green-600'
              : 'bg-gradient-to-r from-gray-600 to-gray-500 cursor-not-allowed opacity-50'
          }`}
        >
          {store.isGenerating ? '⏳ Generating...' : template ? '✨ Generate (Template)' : '📋 No Template'}
        </button>

        {/* Generate WITHOUT Template */}
        <button
          onClick={handleGenerate}
          disabled={store.isGenerating || !store.topic.trim()}
          className={`p-4 rounded-lg font-bold text-white transition ${
            !store.isGenerating && store.topic.trim()
              ? 'bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600'
              : 'bg-gradient-to-r from-gray-600 to-gray-500 cursor-not-allowed opacity-50'
          }`}
        >
          {store.isGenerating ? '⏳ Generating...' : '🚀 Generate (Quick)'}
        </button>
      </div>

      {store.error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-6">
          <h3 className="text-red-800 font-bold mb-2">Error</h3>
          <p className="text-red-700">{store.error}</p>
          <button
            onClick={() => store.setError(null)}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Dismiss
          </button>
        </div>
      )}
    </div>
  );
};