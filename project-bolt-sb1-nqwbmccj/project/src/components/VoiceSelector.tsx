import { Mic2, Zap } from 'lucide-react';
import { useVideoStore } from '../store/useVideoStore';

const INWORLD_VOICES = [
  { id: 'ashley', name: 'Ashley', gender: 'Female', style: 'Natural & Clear', icon: '👩', bestFor: 'General narration, storytelling' },
  { id: 'brian', name: 'Brian', gender: 'Male', style: 'Professional', icon: '👨', bestFor: 'Business, documentaries' },
  { id: 'emma', name: 'Emma', gender: 'Female', style: 'Warm & Friendly', icon: '👩', bestFor: 'Lifestyle, tutorials' },
  { id: 'john', name: 'John', gender: 'Male', style: 'Deep & Powerful', icon: '👨', bestFor: 'Horror, dramatic stories' },
  { id: 'sarah', name: 'Sarah', gender: 'Female', style: 'Energetic', icon: '👩', bestFor: 'Adventure, action' },
  { id: 'mike', name: 'Mike', gender: 'Male', style: 'Casual', icon: '👨', bestFor: 'Vlogs, casual content' },
  { id: 'rachel', name: 'Rachel', gender: 'Female', style: 'Clear & Precise', icon: '👩', bestFor: 'Education, explanations' },
  { id: 'david', name: 'David', gender: 'Male', style: 'Authoritative', icon: '👨', bestFor: 'News, formal content' },
];

export const VoiceSelector = () => {
  const { voiceId, setVoiceId } = useVideoStore();

  // Group by gender
  const femaleVoices = INWORLD_VOICES.filter(v => v.gender === 'Female');
  const maleVoices = INWORLD_VOICES.filter(v => v.gender === 'Male');

  return (
    <div className="bg-white rounded-xl shadow-md p-6 space-y-4">
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-2 flex items-center space-x-2">
          <Mic2 className="w-6 h-6 text-purple-600" />
          <span>Voice Selection</span>
        </h2>
        <p className="text-gray-600">Choose your narrator's voice (Inworld AI - Super Fast!)</p>
      </div>

      {/* Inworld AI Info */}
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-4 border-2 border-purple-200">
        <div className="flex items-center space-x-2 mb-2">
          <Zap className="w-5 h-5 text-purple-600" />
          <span className="font-bold text-gray-900">INWORLD AI - Premium Voices</span>
          <span className="px-2 py-1 bg-purple-600 text-white text-xs font-bold rounded">SUPER FAST</span>
        </div>
        <p className="text-sm text-gray-600">
          Professional-grade TTS with parallel processing - 10x faster generation!
        </p>
      </div>

      {/* Female Voices */}
      <div>
        <h3 className="font-semibold text-gray-900 mb-3">👩 Female Voices ({femaleVoices.length})</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {femaleVoices.map((voice) => (
            <button
              key={voice.id}
              onClick={() => setVoiceId(voice.id)}
              className={`text-left p-4 rounded-lg border-2 transition-all ${
                voiceId === voice.id
                  ? 'border-purple-600 bg-purple-50 ring-2 ring-purple-200'
                  : 'border-gray-200 hover:border-purple-400 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center space-x-2 mb-2">
                <span className="text-2xl">{voice.icon}</span>
                <div>
                  <div className="font-bold text-gray-900">{voice.name}</div>
                  <div className="text-xs text-gray-600">{voice.style}</div>
                </div>
              </div>
              <div className="text-xs text-gray-600 mt-2">
                <strong>Best for:</strong> {voice.bestFor}
              </div>
              <div className="text-xs text-purple-600 font-semibold mt-1">
                ⚡ Premium Quality
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Male Voices */}
      <div>
        <h3 className="font-semibold text-gray-900 mb-3">👨 Male Voices ({maleVoices.length})</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {maleVoices.map((voice) => (
            <button
              key={voice.id}
              onClick={() => setVoiceId(voice.id)}
              className={`text-left p-4 rounded-lg border-2 transition-all ${
                voiceId === voice.id
                  ? 'border-purple-600 bg-purple-50 ring-2 ring-purple-200'
                  : 'border-gray-200 hover:border-purple-400 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center space-x-2 mb-2">
                <span className="text-2xl">{voice.icon}</span>
                <div>
                  <div className="font-bold text-gray-900">{voice.name}</div>
                  <div className="text-xs text-gray-600">{voice.style}</div>
                </div>
              </div>
              <div className="text-xs text-gray-600 mt-2">
                <strong>Best for:</strong> {voice.bestFor}
              </div>
              <div className="text-xs text-purple-600 font-semibold mt-1">
                ⚡ Premium Quality
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Current Selection */}
      <div className="bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg p-4 text-white">
        <p className="text-sm font-medium mb-1">Currently Selected:</p>
        <p className="text-lg font-bold">
          {INWORLD_VOICES.find((v) => v.id === voiceId)?.name || 'Ashley'}
        </p>
        <p className="text-sm opacity-90">
          {INWORLD_VOICES.find((v) => v.id === voiceId)?.style || 'Natural & Clear'}
        </p>
      </div>
    </div>
  );
};
