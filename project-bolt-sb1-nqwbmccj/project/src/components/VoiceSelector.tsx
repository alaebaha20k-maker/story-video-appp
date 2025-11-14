import { Mic2, Cpu } from 'lucide-react';
import { useVideoStore } from '../store/useVideoStore';

// ✅ KOKORO TTS VOICES - GPU-ACCELERATED ON GOOGLE COLAB!
const KOKORO_VOICES = [
  // FEMALE VOICES
  { id: 'aria', name: 'Aria (Bella)', gender: 'Female', style: 'Natural & Warm', icon: '👩', bestFor: 'Stories, lifestyle, general narration' },
  { id: 'sarah_pro', name: 'Sarah', gender: 'Female', style: 'Professional', icon: '👩', bestFor: 'Business, professional content' },
  { id: 'nicole', name: 'Nicole', gender: 'Female', style: 'Cheerful & Clear', icon: '👩', bestFor: 'Education, tutorials' },
  { id: 'jenny', name: 'Jenny', gender: 'Female', style: 'Young & Energetic', icon: '👩', bestFor: 'Adventure, action' },
  { id: 'sara', name: 'Sara', gender: 'Female', style: 'Natural', icon: '👩', bestFor: 'Narration, storytelling' },
  { id: 'emma', name: 'Emma', gender: 'Female', style: 'British Accent', icon: '👩', bestFor: 'Documentaries, British content' },

  // MALE VOICES
  { id: 'guy', name: 'Guy (Adam)', gender: 'Male', style: 'Natural & Clear', icon: '👨', bestFor: 'Documentaries, narration' },
  { id: 'adam_narration', name: 'Adam', gender: 'Male', style: 'Professional Narration', icon: '👨', bestFor: 'Professional narration' },
  { id: 'michael', name: 'Michael', gender: 'Male', style: 'Warm & Friendly', icon: '👨', bestFor: 'Casual content, vlogs' },
  { id: 'brian', name: 'Brian', gender: 'Male', style: 'Casual', icon: '👨', bestFor: 'Casual narration' },
  { id: 'andrew', name: 'Andrew', gender: 'Male', style: 'Professional', icon: '👨', bestFor: 'Business, formal content' },
  { id: 'christopher', name: 'Christopher', gender: 'Male', style: 'Friendly', icon: '👨', bestFor: 'Vlogs, tutorials' },
  { id: 'george', name: 'George', gender: 'Male', style: 'British Accent', icon: '👨', bestFor: 'British content, documentaries' },
];

export const VoiceSelector = () => {
  const { voiceId, setVoiceId } = useVideoStore();

  // Group by gender
  const femaleVoices = KOKORO_VOICES.filter(v => v.gender === 'Female');
  const maleVoices = KOKORO_VOICES.filter(v => v.gender === 'Male');

  return (
    <div className="bg-white rounded-xl shadow-md p-6 space-y-4">
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-2 flex items-center space-x-2">
          <Mic2 className="w-6 h-6 text-purple-600" />
          <span>Voice Selection</span>
        </h2>
        <p className="text-gray-600">Choose your narrator's voice (Kokoro TTS - GPU-Accelerated!)</p>
      </div>

      {/* Kokoro TTS Info */}
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-4 border-2 border-purple-200">
        <div className="flex items-center space-x-2 mb-2">
          <Cpu className="w-5 h-5 text-purple-600" />
          <span className="font-bold text-gray-900">KOKORO TTS (Google Colab GPU)</span>
          <span className="px-2 py-1 bg-purple-600 text-white text-xs font-bold rounded">GPU ACCELERATED</span>
        </div>
        <p className="text-sm text-gray-600">
          Professional AI voices powered by GPU - Natural speech - High quality - FREE!
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
              <div className="text-xs text-purple-600 font-semibold mt-1 flex items-center space-x-1">
                <Cpu className="w-3 h-3" />
                <span>GPU Accelerated</span>
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
              <div className="text-xs text-purple-600 font-semibold mt-1 flex items-center space-x-1">
                <Cpu className="w-3 h-3" />
                <span>GPU Accelerated</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Current Selection */}
      <div className="bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg p-4 text-white">
        <p className="text-sm font-medium mb-1">Currently Selected:</p>
        <p className="text-lg font-bold">
          {KOKORO_VOICES.find((v) => v.id === voiceId)?.name || 'Guy (Adam)'}
        </p>
        <p className="text-sm opacity-90">
          {KOKORO_VOICES.find((v) => v.id === voiceId)?.style || 'Natural & Clear'}
        </p>
        <p className="text-xs mt-2 opacity-80 flex items-center space-x-1">
          <Cpu className="w-4 h-4" />
          <span>Powered by Kokoro TTS on Google Colab GPU!</span>
        </p>
      </div>
    </div>
  );
};
