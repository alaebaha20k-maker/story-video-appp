import { Mic2, Zap } from 'lucide-react';
import { useVideoStore } from '../store/useVideoStore';

// ✅ PUTER TTS VOICES - FREE & UNLIMITED!
const PUTER_VOICES = [
  // FEMALE VOICES (4)
  { id: 'joanna', name: 'Joanna', gender: 'Female', style: 'Natural & Warm', icon: '👩', bestFor: 'General narration, storytelling' },
  { id: 'ivy', name: 'Ivy', gender: 'Female', style: 'Soft & Friendly', icon: '👩', bestFor: 'Lifestyle, general content' },
  { id: 'kimberly', name: 'Kimberly', gender: 'Female', style: 'Young & Energetic', icon: '👩', bestFor: 'Adventure, action' },
  { id: 'salli', name: 'Salli', gender: 'Female', style: 'Professional & Clear', icon: '👩', bestFor: 'Education, tutorials' },
  
  // MALE VOICES (4)
  { id: 'matthew', name: 'Matthew', gender: 'Male', style: 'Natural & Clear', icon: '👨', bestFor: 'Documentaries, narration' },
  { id: 'joey', name: 'Joey', gender: 'Male', style: 'Young & Energetic', icon: '👨', bestFor: 'Gaming, entertainment' },
  { id: 'brian', name: 'Brian', gender: 'Male', style: 'Professional', icon: '👨', bestFor: 'Business, formal content' },
  { id: 'justin', name: 'Justin', gender: 'Male', style: 'Casual & Friendly', icon: '👨', bestFor: 'Vlogs, tutorials' },
];

export const VoiceSelector = () => {
  const { voiceId, setVoiceId } = useVideoStore();

  // Group by gender
  const femaleVoices = PUTER_VOICES.filter(v => v.gender === 'Female');
  const maleVoices = PUTER_VOICES.filter(v => v.gender === 'Male');

  return (
    <div className="bg-white rounded-xl shadow-md p-6 space-y-4">
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-2 flex items-center space-x-2">
          <Mic2 className="w-6 h-6 text-purple-600" />
          <span>Voice Selection</span>
        </h2>
        <p className="text-gray-600">Choose your narrator's voice (Puter TTS - FREE & Unlimited!)</p>
      </div>

      {/* Puter TTS Info */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-4 border-2 border-green-200">
        <div className="flex items-center space-x-2 mb-2">
          <Zap className="w-5 h-5 text-green-600" />
          <span className="font-bold text-gray-900">PUTER TTS - FREE & UNLIMITED!</span>
          <span className="px-2 py-1 bg-green-600 text-white text-xs font-bold rounded">$0 FOREVER</span>
        </div>
        <p className="text-sm text-gray-600">
          Professional voices with NO API key - Unlimited usage - Perfect for YouTube!
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
              <div className="text-xs text-green-600 font-semibold mt-1">
                💰 FREE Forever
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
              <div className="text-xs text-green-600 font-semibold mt-1">
                💰 FREE Forever
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Current Selection */}
      <div className="bg-gradient-to-r from-green-500 to-blue-600 rounded-lg p-4 text-white">
        <p className="text-sm font-medium mb-1">Currently Selected:</p>
        <p className="text-lg font-bold">
          {PUTER_VOICES.find((v) => v.id === voiceId)?.name || 'Matthew'}
        </p>
        <p className="text-sm opacity-90">
          {PUTER_VOICES.find((v) => v.id === voiceId)?.style || 'Natural & Clear'}
        </p>
        <p className="text-xs mt-2 opacity-80">
          💰 FREE & Unlimited - No costs ever!
        </p>
      </div>
    </div>
  );
};
