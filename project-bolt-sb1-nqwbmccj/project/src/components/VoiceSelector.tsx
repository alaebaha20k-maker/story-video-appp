import { useVideoStore } from '../store/useVideoStore';
import { VOICES } from '../constants/options';
import { motion } from 'framer-motion';
import { Volume2 } from 'lucide-react';
import { useState } from 'react';

export const VoiceSelector = () => {
  const { voiceId, setVoiceId } = useVideoStore();
  const [selectedEngine, setSelectedEngine] = useState<'kokoro' | 'edge' | 'all'>('all');

  // Filter voices by engine
  const filteredVoices = VOICES.filter((voice) => {
    if (selectedEngine === 'all') return true;
    return voice.engine === selectedEngine;
  });

  // Group voices by gender
  const groupedVoices = filteredVoices.reduce((acc, voice) => {
    const gender = voice.description.includes('Male') ? 'Male' : 'Female';
    if (!acc[gender]) acc[gender] = [];
    acc[gender].push(voice);
    return acc;
  }, {} as Record<string, typeof VOICES>);

  return (
    <div className="bg-white rounded-xl shadow-md p-6 space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">🎤 Voice Selection</h2>
        <p className="text-gray-600">Choose the narrator voice for your story</p>
      </div>

      {/* Engine Selector */}
      <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg p-4">
        <p className="text-sm font-semibold text-gray-700 mb-3">Voice Engine</p>
        <div className="flex gap-3">
          <button
            onClick={() => setSelectedEngine('kokoro')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              selectedEngine === 'kokoro'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'bg-white text-gray-700 border-2 border-gray-200 hover:border-indigo-300'
            }`}
          >
            ✨ Kokoro TTS (18 voices)
          </button>
          <button
            onClick={() => setSelectedEngine('edge')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              selectedEngine === 'edge'
                ? 'bg-purple-600 text-white shadow-md'
                : 'bg-white text-gray-700 border-2 border-gray-200 hover:border-purple-300'
            }`}
          >
            🔄 Edge-TTS (Backup)
          </button>
          <button
            onClick={() => setSelectedEngine('all')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              selectedEngine === 'all'
                ? 'bg-pink-600 text-white shadow-md'
                : 'bg-white text-gray-700 border-2 border-gray-200 hover:border-pink-300'
            }`}
          >
            🎯 All Voices
          </button>
        </div>
      </div>

      {/* Voice Groups */}
      <div className="space-y-6">
        {Object.entries(groupedVoices).map(([gender, voices]) => (
          <div key={gender} className="space-y-3">
            <h3 className="text-lg font-bold text-gray-700 border-b-2 border-indigo-200 pb-2">
              {gender} Voices ({voices.length})
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {voices.map((voice) => (
                <motion.button
                  key={voice.id}
                  whileHover={{ scale: 1.01 }}
                  whileTap={{ scale: 0.99 }}
                  onClick={() => setVoiceId(voice.id)}
                  className={`text-left p-4 rounded-lg border-2 transition-all ${
                    voiceId === voice.id
                      ? 'border-indigo-600 bg-indigo-50 shadow-md ring-2 ring-indigo-200'
                      : 'border-gray-200 hover:border-indigo-300 hover:shadow-md'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center space-x-3 flex-1">
                      <span className="text-2xl">{voice.icon}</span>
                      <div className="min-w-0">
                        <h4 className="font-bold text-gray-900 text-sm">{voice.name}</h4>
                        <p className="text-xs text-gray-500">
                          {voice.accent} • {voice.engine === 'kokoro' ? '✨ Kokoro' : '🔄 Edge'}
                        </p>
                      </div>
                    </div>
                    <div className="flex-shrink-0 p-2 hover:bg-indigo-100 rounded-full transition-colors">
                      <Volume2 className="w-5 h-5 text-indigo-600" />
                    </div>
                  </div>

                  <p className="text-xs text-gray-700 mb-2 leading-tight">
                    {voice.description}
                  </p>

                  <div className="space-y-1">
                    <p className="text-xs text-gray-600">
                      <span className="font-medium">Tone:</span> {voice.tone}
                    </p>
                    <p className="text-xs text-indigo-600 font-medium">
                      Best for: {voice.bestFor}
                    </p>
                  </div>

                  {/* Engine Badge */}
                  <div className="mt-2 flex gap-1">
                    <span
                      className={`text-xs px-2 py-1 rounded font-medium ${
                        voice.engine === 'kokoro'
                          ? 'bg-indigo-100 text-indigo-700'
                          : 'bg-purple-100 text-purple-700'
                      }`}
                    >
                      {voice.engine === 'kokoro' ? '✨ Premium' : '🔄 Backup'}
                    </span>
                  </div>
                </motion.button>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Info Section */}
      <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
        <p className="text-sm text-blue-900">
          <span className="font-bold">💡 Tip:</span> Kokoro TTS offers 18 professional voices
          with natural pronunciation. Edge-TTS is a reliable fallback.
        </p>
      </div>

      {/* Currently Selected */}
      <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg p-4 text-white">
        <p className="text-sm font-medium mb-1">Currently Selected:</p>
        <p className="text-lg font-bold">
          {VOICES.find((v) => v.id === voiceId)?.name}
        </p>
      </div>
    </div>
  );
};