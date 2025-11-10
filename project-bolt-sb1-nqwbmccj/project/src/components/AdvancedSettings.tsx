import { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { useVideoStore } from '../store/useVideoStore';
import { HOOK_INTENSITIES, PACING_STYLES } from '../constants/options';

export const AdvancedSettings = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { hookIntensity, pacing, numScenes, useAdvancedAnalysis, setHookIntensity, setPacing, setNumScenes, setUseAdvancedAnalysis } =
    useVideoStore();

  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
      >
        <div className="text-left">
          <h2 className="text-xl font-bold text-gray-900">Advanced Script Settings</h2>
          <p className="text-sm text-gray-600">Fine-tune your story generation</p>
        </div>
        {isOpen ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
      </button>

      {isOpen && (
        <div className="px-6 pb-6 space-y-6 border-t border-gray-100">
          <div className="pt-6">
            <label htmlFor="hook" className="block text-sm font-medium text-gray-700 mb-2">
              Hook Intensity
            </label>
            <select
              id="hook"
              value={hookIntensity}
              onChange={(e) => setHookIntensity(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              {HOOK_INTENSITIES.map((hook) => (
                <option key={hook.value} value={hook.value}>
                  {hook.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="pacing" className="block text-sm font-medium text-gray-700 mb-2">
              Pacing Style
            </label>
            <select
              id="pacing"
              value={pacing}
              onChange={(e) => setPacing(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              {PACING_STYLES.map((style) => (
                <option key={style.value} value={style.value}>
                  {style.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <div className="flex justify-between items-center mb-3">
              <label htmlFor="scenes" className="block text-sm font-medium text-gray-700">
                Number of Scenes
              </label>
              <span className="text-sm font-semibold text-indigo-600">{numScenes} scenes</span>
            </div>
            <input
              id="scenes"
              type="range"
              min="5"
              max="20"
              value={numScenes}
              onChange={(e) => setNumScenes(Number(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between mt-2 text-xs text-gray-500">
              <span>5</span>
              <span>10</span>
              <span>15</span>
              <span>20</span>
            </div>
            <p className="text-sm text-gray-600 mt-2">More scenes = more images generated</p>
          </div>

          {/* ✨ NEW: Advanced Script Analysis Toggle */}
          <div className="pt-4 border-t border-gray-100">
            <div className="flex items-start space-x-3">
              <input
                id="advancedAnalysis"
                type="checkbox"
                checked={useAdvancedAnalysis}
                onChange={(e) => setUseAdvancedAnalysis(e.target.checked)}
                className="mt-1 h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded cursor-pointer"
              />
              <div className="flex-1">
                <label htmlFor="advancedAnalysis" className="block text-sm font-medium text-gray-700 cursor-pointer">
                  ✨ Advanced Script Analysis (NEW)
                </label>
                <p className="text-xs text-gray-600 mt-1">
                  Separates narration from visual descriptions for cleaner voice output and more detailed image prompts.
                  <span className="font-semibold text-indigo-600"> Adds ~10 seconds to generation.</span>
                </p>
                <div className="mt-2 text-xs bg-indigo-50 border border-indigo-200 rounded-lg p-2">
                  <div className="flex items-center space-x-1">
                    <span className="text-indigo-700">✓</span>
                    <span className="text-indigo-700">Clean narration (no image prompts spoken)</span>
                  </div>
                  <div className="flex items-center space-x-1 mt-1">
                    <span className="text-indigo-700">✓</span>
                    <span className="text-indigo-700">Professional AI-generated image prompts</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
