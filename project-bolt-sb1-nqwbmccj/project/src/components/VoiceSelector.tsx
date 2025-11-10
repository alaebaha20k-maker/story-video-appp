import { Mic2, Zap } from 'lucide-react';
import { useVideoStore } from '../store/useVideoStore';

// ✅ KOKORO TTS VOICES - GPU-POWERED!
const KOKORO_VOICES = [
  // FEMALE VOICES (4)
  { id: 'aria', name: 'Sarah', gender: 'Female', style: 'Clear & Professional', icon: '👩', bestFor: 'General narration, storytelling', kokoro: 'af_sarah' },
  { id: 'jenny', name: 'Nicole', gender: 'Female', style: 'Warm & Friendly', icon: '👩', bestFor: 'Education, tutorials', kokoro: 'af_nicole' },
  { id: 'sara', name: 'Sarah', gender: 'Female', style: 'Clear & Natural', icon: '👩', bestFor: 'Adventure, action', kokoro: 'af_sarah' },
  { id: 'libby', name: 'Emma (British)', gender: 'Female', style: 'British Professional', icon: '🇬🇧', bestFor: 'Business, formal content', kokoro: 'bf_emma' },

  // MALE VOICES (4)
  { id: 'guy', name: 'Adam', gender: 'Male', style: 'Deep & Natural', icon: '👨', bestFor: 'Documentaries, narration', kokoro: 'am_adam' },
  { id: 'andrew', name: 'Adam', gender: 'Male', style: 'Deep & Natural', icon: '👨', bestFor: 'Business, formal content', kokoro: 'am_adam' },
  { id: 'christopher', name: 'Michael', gender: 'Male', style: 'Friendly & Warm', icon: '👨', bestFor: 'Vlogs, tutorials', kokoro: 'am_michael' },
  { id: 'george', name: 'George (British)', gender: 'Male', style: 'British Authoritative', icon: '🇬🇧', bestFor: 'News, documentaries', kokoro: 'bm_george' },
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
        <p className="text-gray-600">Choose your narrator's voice (Kokoro TTS - GPU-Powered!)</p>
      </div>

      {/* Kokoro TTS Info */}
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-4 border-2 border-purple-200">
        <div className="flex items-center space-x-2 mb-2">
          <Zap className="w-5 h-5 text-purple-600" />
          <span className="font-bold text-gray-900">KOKORO TTS - GPU-POWERED!</span>
          <span className="px-2 py-1 bg-purple-600 text-white text-xs font-bold rounded">⚡ HIGH QUALITY</span>
        </div>
        <p className="text-sm text-gray-600">
          Premium GPU-powered voices - High quality - American & British accents - Variable speed control!
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
                ⚡ GPU Quality
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
                ⚡ GPU Quality
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Current Selection */}
      <div className="bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg p-4 text-white">
        <p className="text-sm font-medium mb-1">Currently Selected:</p>
        <p className="text-lg font-bold">
          {KOKORO_VOICES.find((v) => v.id === voiceId)?.name || 'Adam'}
        </p>
        <p className="text-sm opacity-90">
          {KOKORO_VOICES.find((v) => v.id === voiceId)?.style || 'Deep & Natural'}
        </p>
        <p className="text-xs mt-2 opacity-80">
          ⚡ GPU-Powered - High Quality Kokoro TTS!
        </p>
      </div>
    </div>
  );
};