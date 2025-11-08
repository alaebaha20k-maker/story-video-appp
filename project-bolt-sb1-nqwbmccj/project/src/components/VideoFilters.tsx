import { Palette, Zap } from 'lucide-react';
import { useVideoStore } from '../store/useVideoStore';

const FILTERS = [
  { id: 'none', name: 'None', description: 'Original colors' },
  { id: 'cinematic', name: 'Cinematic', description: 'Professional cinema look' },
  { id: 'warm', name: 'Warm', description: 'Cozy warm tones' },
  { id: 'cool', name: 'Cool', description: 'Blue professional look' },
  { id: 'vibrant', name: 'Vibrant', description: 'Pop and energy' },
  { id: 'vintage', name: 'Vintage', description: 'Nostalgic retro feel' },
  { id: 'noir', name: 'Noir', description: 'Black and white drama' },
  { id: 'dramatic', name: 'Dramatic', description: 'High contrast mood' },
  { id: 'horror', name: 'Horror', description: 'Dark and eerie' },
  { id: 'anime', name: 'Anime', description: 'Vibrant anime style' },
];

export const VideoFilters = () => {
  const { colorFilter, setColorFilter, zoomEffect, setZoomEffect } = useVideoStore();

  return (
    <div className="bg-white rounded-xl shadow-md p-6 space-y-4">
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-2 flex items-center space-x-2">
          <Palette className="w-6 h-6 text-indigo-600" />
          <span>Video Filters & Effects</span>
        </h2>
        <p className="text-gray-600">Add professional color grading and visual effects (no slowdown)</p>
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
              <span className="text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded-full font-medium">
                Recommended
              </span>
            </div>
            <p className="text-sm text-gray-600 mt-1">
              Smooth zoom on all images (30% dramatic zoom) - Creates professional motion and engagement
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
        <strong>⚡ Fast Processing:</strong> Filters use FFmpeg hardware acceleration - no performance impact!
      </div>
    </div>
  );
};
