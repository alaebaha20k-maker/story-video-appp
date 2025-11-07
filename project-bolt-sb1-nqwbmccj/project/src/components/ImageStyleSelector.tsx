import { useVideoStore } from '../store/useVideoStore';
import { IMAGE_STYLES } from '../constants/options';
import { motion } from 'framer-motion';

export const ImageStyleSelector = () => {
  const { imageStyle, setImageStyle } = useVideoStore();

  return (
    <div className="bg-white rounded-xl shadow-md p-6 space-y-4">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Image Generation Style</h2>
        <p className="text-gray-600">Select the visual style for your video</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {IMAGE_STYLES.map((style) => (
          <motion.button
            key={style.id}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setImageStyle(style.id)}
            className={`text-left rounded-lg border-2 overflow-hidden transition-all ${
              imageStyle === style.id
                ? 'border-indigo-600 shadow-md'
                : 'border-gray-200 hover:border-indigo-300 hover:shadow'
            }`}
          >
            <div
              className="h-24 flex items-center justify-center"
              style={{ background: style.preview }}
            >
              <span className="text-4xl drop-shadow-lg">{style.icon}</span>
            </div>
            <div className="p-3">
              <h3 className="font-semibold text-gray-900 mb-1">{style.name}</h3>
              <p className="text-xs text-gray-600">{style.description}</p>
            </div>
          </motion.button>
        ))}
      </div>
    </div>
  );
};
