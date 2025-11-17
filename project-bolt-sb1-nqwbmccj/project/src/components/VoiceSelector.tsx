import { Mic2, Zap } from 'lucide-react';
import { useVideoStore } from '../store/useVideoStore';

// ✅ COQUI TTS VOICES - HIGH QUALITY AI VOICES!
const COQUI_VOICES = [
  // FEMALE VOICES (4)
  { id: 'aria', name: 'Aria', gender: 'Female', style: 'Natural & Warm', icon: '👩', bestFor: 'General narration, storytelling' },
  { id: 'jenny', name: 'Jenny', gender: 'Female', style: 'Cheerful & Clear', icon: '👩', bestFor: 'Education, tutorials' },
  { id: 'sara', name: 'Sara', gender: 'Female', style: 'Young & Energetic', icon: '👩', bestFor: 'Adventure, action' },
  { id: 'nancy', name: 'Nancy', gender: 'Female', style: 'Professional', icon: '👩', bestFor: 'Business, formal content' },
  
  // MALE VOICES (4)
  { id: 'guy', name: 'Guy', gender: 'Male', style: 'Natural & Clear', icon: '👨', bestFor: 'Documentaries, narration' },
  { id: 'andrew', name: 'Andrew', gender: 'Male', style: 'Professional', icon: '👨', bestFor: 'Business, formal content' },
  { id: 'christopher', name: 'Christopher', gender: 'Male', style: 'Casual & Friendly', icon: '👨', bestFor: 'Vlogs, tutorials' },
  { id: 'roger', name: 'Roger', gender: 'Male', style: 'Authoritative', icon: '👨', bestFor: 'News, documentaries' },
];

export const VoiceSelector = () => {
  const { voiceId, setVoiceId } = useVideoStore();

  // Group by gender
  const femaleVoices = COQUI_VOICES.filter(v => v.gender === 'Female');
  const maleVoices = COQUI_VOICES.filter(v => v.gender === 'Male');

  return (
    <div className="bg-white rounded-xl shadow-md p-6 space-y-4">
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-2 flex items-center space-x-2">
          <Mic2 className="w-6 h-6 text-purple-600" />
          <span>Voice Selection</span>
        </h2>
        <p className="text-gray-600">Choose your narrator's voice (Coqui TTS - High Quality AI Voices!)</p>
      </div>

      {/* Coqui TTS Info */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4 border-2 border-blue-200">
        <div className="flex items-center space-x-2 mb-2">
          <Zap className="w-5 h-5 text-blue-600" />
          <span className="font-bold text-gray-900">COQUI TTS - HIGH QUALITY AI VOICES!</span>
          <span className="px-2 py-1 bg-purple-600 text-white text-xs font-bold rounded">GOOGLE COLAB</span>
        </div>
        <p className="text-sm text-gray-600">
          Professional AI-generated voices - Processed in Google Colab - Natural & Expressive!
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
              <div className="text-xs text-blue-600 font-semibold mt-1">
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
              <div className="text-xs text-blue-600 font-semibold mt-1">
                💰 FREE Forever
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Current Selection */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-4 text-white">
        <p className="text-sm font-medium mb-1">Currently Selected:</p>
        <p className="text-lg font-bold">
          {COQUI_VOICES.find((v) => v.id === voiceId)?.name || 'Guy'}
        </p>
        <p className="text-sm opacity-90">
          {COQUI_VOICES.find((v) => v.id === voiceId)?.style || 'Natural & Clear'}
        </p>
        <p className="text-xs mt-2 opacity-80">
          🎙️ Coqui TTS - Processed in Google Colab!
        </p>
      </div>
    </div>
  );
};