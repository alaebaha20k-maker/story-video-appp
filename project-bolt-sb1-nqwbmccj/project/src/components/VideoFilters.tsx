import { Palette, Zap, Sparkles } from 'lucide-react';
import { useVideoStore } from '../store/useVideoStore';

// GPU-accelerated color filters (applied on Google Colab server)
const FILTERS = [
  { id: 'none', name: 'None', description: 'Original colors' },
  { id: 'warm', name: 'Warm', description: 'Cozy warm tones with golden hues' },
  { id: 'cool', name: 'Cool', description: 'Blue professional cinematic look' },
  { id: 'vintage', name: 'Vintage', description: 'Nostalgic retro vignette feel' },
  { id: 'cinematic', name: 'Cinematic', description: 'Professional Hollywood-grade color' },
];

export const VideoFilters = () => {
  const { colorFilter, setColorFilter, zoomEffect, setZoomEffect, grainEffect, setGrainEffect } = useVideoStore();

  return (
    <div className="bg-white rounded-xl shadow-md p-6 space-y-4">
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-2 flex items-center space-x-2">
          <Palette className="w-6 h-6 text-indigo-600" />
          <span>Video Filters & Effects</span>
        </h2>
        <p className="text-gray-600">GPU-accelerated effects on Google Colab (FFmpeg hardware acceleration)</p>
      </div>

      {/* Zoom Effect Toggle */}
      <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg p-4">
        <label className="flex items-center space-x-3 cursor-pointer">
          <input
            type="checkbox"
            checked={zoomEffect}
            onChange={(e) => setZoomEffect(e.target.checked)}
            className="w-5 h-5 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500"
          />
          <div className="flex-1">
            <div className="flex items-center space-x-2">
              <Zap className="w-5 h-5 text-indigo-600" />
              <span className="font-semibold text-gray-900">Ken Burns Zoom Effect</span>
            </div>
            <p className="text-sm text-gray-600 mt-1">
              Smooth zoom on all images/videos (5% zoom in) - Creates dynamic motion
            </p>
          </div>
        </label>
      </div>

      {/* Grain Effect Toggle */}
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-4">
        <label className="flex items-center space-x-3 cursor-pointer">
          <input
            type="checkbox"
            checked={grainEffect}
            onChange={(e) => setGrainEffect(e.target.checked)}
            className="w-5 h-5 text-purple-600 rounded focus:ring-2 focus:ring-purple-500"
          />
          <div className="flex-1">
            <div className="flex items-center space-x-2">
              <Sparkles className="w-5 h-5 text-purple-600" />
              <span className="font-semibold text-gray-900">Film Grain Effect</span>
            </div>
            <p className="text-sm text-gray-600 mt-1">
              Add cinematic film grain/noise overlay for professional aesthetic
            </p>
          </div>
        </label>
      </div>

      {/* Color Filter Selection */}
      <div>
        <h3 className="font-semibold text-gray-900 mb-3">Color Grading Filter</h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          {FILTERS.map((filter) => (
            <button
              key={filter.id}
              onClick={() => setColorFilter(filter.id)}
              className={`p-3 rounded-lg border-2 transition-all text-left ${
                colorFilter === filter.id
                  ? 'border-indigo-600 bg-indigo-50 ring-2 ring-indigo-200'
                  : 'border-gray-200 hover:border-indigo-400 hover:bg-gray-50'
              }`}
            >
              <div className="font-semibold text-gray-900 text-sm">{filter.name}</div>
              <div className="text-xs text-gray-600 mt-1">{filter.description}</div>
            </button>
          ))}
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-800">
        <strong>⚡ GPU-Accelerated:</strong> All effects processed on Google Colab GPU server with FFmpeg hardware acceleration!
      </div>
    </div>
  );
};
