import { useVideoStore } from '../store/useVideoStore';
import { motion } from 'framer-motion';
import { Check, ArrowUp, ArrowDown, Trash2, Plus } from 'lucide-react';
import { useState } from 'react';

type MediaSource = 'ai' | 'stock' | 'manual';

interface MediaSourceOption {
  id: MediaSource;
  name: string;
  icon: string;
  description: string;
}

const MEDIA_SOURCES: MediaSourceOption[] = [
  {
    id: 'ai',
    name: 'AI Generated',
    icon: '🤖',
    description: 'SDXL-Turbo GPU images',
  },
  {
    id: 'stock',
    name: 'Stock Media',
    icon: '📸',
    description: 'Pexels professional media',
  },
  {
    id: 'manual',
    name: 'Manual Uploads',
    icon: '📁',
    description: 'Your own images/videos',
  },
];

export const MediaSourcePriority = () => {
  const store = useVideoStore();
  const [priorityMode, setPriorityMode] = useState<'sequential' | 'pattern'>('sequential');
  const [pattern, setPattern] = useState<string>('ai,stock,ai');

  // Initialize priority order if not set
  if (!store.mediaPriority || store.mediaPriority.length === 0) {
    store.setMediaPriority(['ai', 'stock', 'manual']);
  }

  const currentPriority = store.mediaPriority || ['ai', 'stock', 'manual'];

  const moveUp = (index: number) => {
    if (index === 0) return;
    const newPriority = [...currentPriority];
    [newPriority[index - 1], newPriority[index]] = [newPriority[index], newPriority[index - 1]];
    store.setMediaPriority(newPriority);
  };

  const moveDown = (index: number) => {
    if (index === currentPriority.length - 1) return;
    const newPriority = [...currentPriority];
    [newPriority[index], newPriority[index + 1]] = [newPriority[index + 1], newPriority[index]];
    store.setMediaPriority(newPriority);
  };

  const removeSource = (index: number) => {
    const newPriority = currentPriority.filter((_, i) => i !== index);
    if (newPriority.length > 0) {
      store.setMediaPriority(newPriority);
    }
  };

  const addSource = (source: MediaSource) => {
    if (!currentPriority.includes(source)) {
      store.setMediaPriority([...currentPriority, source]);
    }
  };

  const getSourceInfo = (id: MediaSource) => {
    return MEDIA_SOURCES.find((s) => s.id === id)!;
  };

  const availableSources = MEDIA_SOURCES.filter(
    (s) => !currentPriority.includes(s.id)
  );

  return (
    <div className="bg-white rounded-xl shadow-md p-6 space-y-4">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          🎬 Media Source Priority
        </h2>
        <p className="text-gray-600">
          Control which media sources are used and in what order
        </p>
      </div>

      {/* Mode Selector */}
      <div className="flex space-x-4 mb-4">
        <button
          onClick={() => setPriorityMode('sequential')}
          className={`flex-1 p-3 rounded-lg border-2 transition-all ${
            priorityMode === 'sequential'
              ? 'border-indigo-600 bg-indigo-50'
              : 'border-gray-200 hover:border-indigo-300'
          }`}
        >
          <div className="font-semibold">📋 Sequential Order</div>
          <div className="text-xs text-gray-600 mt-1">
            Use sources in priority order
          </div>
        </button>

        <button
          onClick={() => setPriorityMode('pattern')}
          className={`flex-1 p-3 rounded-lg border-2 transition-all ${
            priorityMode === 'pattern'
              ? 'border-indigo-600 bg-indigo-50'
              : 'border-gray-200 hover:border-indigo-300'
          }`}
        >
          <div className="font-semibold">🔀 Interleaved Pattern</div>
          <div className="text-xs text-gray-600 mt-1">
            Alternate between sources
          </div>
        </button>
      </div>

      {priorityMode === 'sequential' && (
        <div className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <p className="text-sm text-blue-800">
              <strong>How it works:</strong> Video will use all {currentPriority[0]} images
              first, then {currentPriority[1]}, then {currentPriority[2] || 'repeat'}.
            </p>
          </div>

          {/* Priority List */}
          <div className="space-y-2">
            <div className="text-sm font-medium text-gray-700 mb-2">
              Priority Order (drag to reorder):
            </div>
            {currentPriority.map((sourceId, index) => {
              const source = getSourceInfo(sourceId);
              return (
                <motion.div
                  key={sourceId}
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-center space-x-2 p-3 bg-gray-50 rounded-lg border border-gray-200"
                >
                  <div className="flex-shrink-0 w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center font-bold text-indigo-600">
                    {index + 1}
                  </div>

                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-xl">{source.icon}</span>
                      <div>
                        <div className="font-semibold text-gray-900">
                          {source.name}
                        </div>
                        <div className="text-xs text-gray-600">
                          {source.description}
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-1">
                    <button
                      onClick={() => moveUp(index)}
                      disabled={index === 0}
                      className="p-1 rounded hover:bg-gray-200 disabled:opacity-30 disabled:cursor-not-allowed"
                    >
                      <ArrowUp className="w-4 h-4 text-gray-600" />
                    </button>
                    <button
                      onClick={() => moveDown(index)}
                      disabled={index === currentPriority.length - 1}
                      className="p-1 rounded hover:bg-gray-200 disabled:opacity-30 disabled:cursor-not-allowed"
                    >
                      <ArrowDown className="w-4 h-4 text-gray-600" />
                    </button>
                    <button
                      onClick={() => removeSource(index)}
                      disabled={currentPriority.length === 1}
                      className="p-1 rounded hover:bg-red-100 disabled:opacity-30 disabled:cursor-not-allowed"
                    >
                      <Trash2 className="w-4 h-4 text-red-600" />
                    </button>
                  </div>
                </motion.div>
              );
            })}
          </div>

          {/* Add Source */}
          {availableSources.length > 0 && (
            <div className="border-t border-gray-200 pt-4">
              <div className="text-sm font-medium text-gray-700 mb-2">
                Add Source:
              </div>
              <div className="flex space-x-2">
                {availableSources.map((source) => (
                  <button
                    key={source.id}
                    onClick={() => addSource(source.id)}
                    className="flex items-center space-x-2 px-3 py-2 bg-green-50 hover:bg-green-100 border border-green-200 rounded-lg transition-colors"
                  >
                    <Plus className="w-4 h-4 text-green-600" />
                    <span className="text-sm text-green-800">
                      {source.icon} {source.name}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {priorityMode === 'pattern' && (
        <div className="space-y-4">
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
            <p className="text-sm text-purple-800">
              <strong>Pattern Mode:</strong> Define a repeating pattern like "ai,stock,ai,manual"
              to alternate between sources.
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Pattern (comma-separated):
            </label>
            <input
              type="text"
              value={pattern}
              onChange={(e) => {
                setPattern(e.target.value);
                store.setMediaPattern(e.target.value);
              }}
              placeholder="ai,stock,ai,manual"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
            <p className="text-xs text-gray-500 mt-1">
              Example: "ai,stock,ai" = AI → Stock → AI → (repeat)
            </p>
          </div>

          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <div className="text-sm font-medium text-gray-700 mb-2">
              Pattern Preview:
            </div>
            <div className="flex flex-wrap gap-2">
              {pattern.split(',').slice(0, 12).map((source, i) => {
                const trimmed = source.trim() as MediaSource;
                const sourceInfo = MEDIA_SOURCES.find((s) => s.id === trimmed);
                return (
                  <div
                    key={i}
                    className="px-3 py-1 bg-white border border-gray-300 rounded-full text-sm"
                  >
                    <span className="mr-1">{i + 1}.</span>
                    {sourceInfo?.icon} {sourceInfo?.name || trimmed}
                  </div>
                );
              })}
              {pattern.split(',').length > 12 && (
                <div className="px-3 py-1 bg-gray-100 rounded-full text-sm text-gray-600">
                  ... (repeats)
                </div>
              )}
            </div>
          </div>

          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
            <p className="text-xs text-yellow-800">
              <strong>Tips:</strong>
              <br />
              • Use source IDs: ai, stock, manual
              <br />
              • Pattern repeats to fill all scenes
              <br />
              • Example: "ai,ai,stock" = 2 AI images, then 1 stock
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
