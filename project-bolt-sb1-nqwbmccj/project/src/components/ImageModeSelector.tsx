import { useVideoStore } from '../store/useVideoStore';
import { IMAGE_MODES } from '../constants/options';
import { motion } from 'framer-motion';
import { Check } from 'lucide-react';

export const ImageModeSelector = () => {
  const { imageMode, setImageMode } = useVideoStore();

  return (
    <div className="bg-white rounded-xl shadow-md p-6 space-y-4">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Image Mode</h2>
        <p className="text-gray-600">Choose how images will be generated for your video</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {IMAGE_MODES.map((mode) => (
          <motion.button
            key={mode.id}
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            onClick={() => setImageMode(mode.id)}
            className={`text-left p-5 rounded-lg border-2 transition-all ${
              imageMode === mode.id
                ? 'border-indigo-600 bg-indigo-50 shadow-md'
                : 'border-gray-200 hover:border-indigo-300 hover:shadow'
            }`}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-3">
                <span className="text-3xl">{mode.icon}</span>
                <h3 className="font-bold text-gray-900">{mode.name}</h3>
              </div>
              {imageMode === mode.id && (
                <div className="bg-indigo-600 rounded-full p-1">
                  <Check className="w-4 h-4 text-white" />
                </div>
              )}
            </div>
            <p className="text-sm text-gray-700 mb-3">{mode.description}</p>
            <ul className="space-y-1 mb-3">
              {mode.features.map((feature, idx) => (
                <li key={idx} className="text-xs text-gray-600 flex items-start">
                  <span className="mr-2">•</span>
                  <span>{feature}</span>
                </li>
              ))}
            </ul>
            <div className="text-xs font-medium text-indigo-600">
              Best for: {mode.bestFor}
            </div>
          </motion.button>
        ))}
      </div>
    </div>
  );
};
