import { Type, Eye } from 'lucide-react';
import { useVideoStore } from '../store/useVideoStore';

const CAPTION_STYLES = [
  { id: 'simple', name: 'Simple', description: 'White with black outline' },
  { id: 'bold', name: 'Bold', description: 'Large bold text' },
  { id: 'minimal', name: 'Minimal', description: 'Clean subtle look' },
  { id: 'cinematic', name: 'Cinematic', description: 'Professional cinema' },
  { id: 'horror', name: 'Horror', description: 'Red dramatic text' },
  { id: 'elegant', name: 'Elegant', description: 'Sophisticated style' },
];

const CAPTION_POSITIONS = [
  { id: 'bottom', name: 'Bottom' },
  { id: 'top', name: 'Top' },
  { id: 'center', name: 'Center' },
];

const CAPTION_ANIMATIONS = [
  { id: 'none', name: 'None', description: 'Static text' },
  { id: 'fade_in', name: 'Fade In', description: 'Smooth appearance' },
  { id: 'fade_out', name: 'Fade Out', description: 'Smooth disappearance' },
  { id: 'slide_up', name: 'Slide Up', description: 'Slide from bottom' },
];

export const CaptionEditor = () => {
  const { 
    captionEnabled, 
    setCaptionEnabled,
    captionText, 
    setCaptionText,
    captionStyle, 
    setCaptionStyle,
    captionPosition,
    setCaptionPosition,
    captionAnimation,
    setCaptionAnimation,
    autoCaptions,
    setAutoCaptions
  } = useVideoStore();

  return (
    <div className="bg-white rounded-xl shadow-md p-6 space-y-4">
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-2 flex items-center space-x-2">
          <Type className="w-6 h-6 text-indigo-600" />
          <span>Captions & Text Overlay</span>
        </h2>
        <p className="text-gray-600">Add animated captions to your video (FFmpeg-powered, no slowdown)</p>
      </div>

      {/* Auto Captions Toggle - NEW! */}
      <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-4 border-2 border-green-200">
        <label className="flex items-center space-x-3 cursor-pointer">
          <input
            type="checkbox"
            checked={autoCaptions}
            onChange={(e) => {
              setAutoCaptions(e.target.checked);
              if (e.target.checked) {
                setCaptionEnabled(false); // Disable manual captions
              }
            }}
            className="w-5 h-5 text-green-600 rounded focus:ring-2 focus:ring-green-500"
          />
          <div className="flex-1">
            <div className="flex items-center space-x-2">
              <span className="font-bold text-gray-900">✨ AUTO CAPTIONS (TikTok Style)</span>
              <span className="px-2 py-1 bg-green-500 text-white text-xs font-bold rounded">RECOMMENDED</span>
            </div>
            <p className="text-sm text-gray-600 mt-1">
              Automatically generate captions from your script! Perfect sync with audio.
              <br />
              <strong className="text-green-700">Medium size, bottom position, sentence-by-sentence with fade in/out.</strong>
            </p>
          </div>
        </label>
      </div>

      {/* Manual Caption Toggle */}
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-4">
        <label className="flex items-center space-x-3 cursor-pointer">
          <input
            type="checkbox"
            checked={captionEnabled}
            onChange={(e) => {
              setCaptionEnabled(e.target.checked);
              if (e.target.checked) {
                setAutoCaptions(false); // Disable auto captions
              }
            }}
            disabled={autoCaptions}
            className="w-5 h-5 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
          />
          <div>
            <span className="font-semibold text-gray-900">Manual Caption (Single Text)</span>
            <p className="text-sm text-gray-600">Add one custom text overlay for entire video</p>
          </div>
        </label>
      </div>

      {captionEnabled && (
        <div className="space-y-4 animate-in">
          {/* Caption Text */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Caption Text
            </label>
            <input
              type="text"
              value={captionText}
              onChange={(e) => setCaptionText(e.target.value)}
              placeholder="Enter your caption text..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>

          {/* Caption Style */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Caption Style
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {CAPTION_STYLES.map((style) => (
                <button
                  key={style.id}
                  onClick={() => setCaptionStyle(style.id)}
                  className={`p-2 rounded-lg border-2 transition-all text-left ${
                    captionStyle === style.id
                      ? 'border-indigo-600 bg-indigo-50'
                      : 'border-gray-200 hover:border-indigo-400'
                  }`}
                >
                  <div className="font-medium text-sm">{style.name}</div>
                  <div className="text-xs text-gray-600">{style.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Position and Animation */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Position
              </label>
              <select
                value={captionPosition}
                onChange={(e) => setCaptionPosition(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              >
                {CAPTION_POSITIONS.map((pos) => (
                  <option key={pos.id} value={pos.id}>
                    {pos.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Animation
              </label>
              <select
                value={captionAnimation}
                onChange={(e) => setCaptionAnimation(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              >
                {CAPTION_ANIMATIONS.map((anim) => (
                  <option key={anim.id} value={anim.id}>
                    {anim.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Preview */}
          {captionText && (
            <div className="bg-gray-900 rounded-lg p-8 relative h-48 flex items-center justify-center">
              <div className="absolute inset-0 flex items-center justify-center">
                <Eye className="w-16 h-16 text-gray-700" />
              </div>
              <div
                className={`relative z-10 font-bold ${
                  captionStyle === 'horror' ? 'text-red-500' : 'text-white'
                }`}
                style={{
                  textShadow: '2px 2px 4px rgba(0,0,0,0.8)',
                  fontSize: captionStyle === 'bold' ? '2rem' : '1.5rem'
                }}
              >
                {captionText}
              </div>
            </div>
          )}

          <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-sm text-green-800">
            <strong>⚡ Zero Slowdown:</strong> Captions use FFmpeg drawtext - renders in milliseconds!
          </div>
        </div>
      )}

      {/* Info about Auto Captions */}
      {autoCaptions && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-800 animate-in">
          <strong>✨ AUTO CAPTIONS ENABLED</strong>
          <ul className="mt-2 space-y-1 list-disc list-inside">
            <li>Script will be split into sentences</li>
            <li>Each sentence perfectly synced with audio timing</li>
            <li>Medium size (readable, not too big/small)</li>
            <li>Bottom position (professional style)</li>
            <li>Fade in/out transitions (smooth)</li>
            <li><strong>Zero slowdown - same generation time!</strong></li>
          </ul>
        </div>
      )}
    </div>
  );
};
