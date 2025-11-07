import { useVideoStore } from '../store/useVideoStore';
import { STORY_TYPES } from '../constants/options';
import { motion } from 'framer-motion';

export const StoryTypeSelector = () => {
  const { storyType, setStoryType } = useVideoStore();

  return (
    <div className="bg-white rounded-xl shadow-md p-6 space-y-4">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Story Type</h2>
        <p className="text-gray-600">Choose the style and tone of your narrative</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {STORY_TYPES.map((type) => (
          <motion.button
            key={type.id}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setStoryType(type.id)}
            className={`text-left p-4 rounded-lg border-2 transition-all ${
              storyType === type.id
                ? 'border-indigo-600 bg-indigo-50 shadow-md'
                : 'border-gray-200 hover:border-indigo-300 hover:shadow'
            }`}
          >
            <div className="flex items-start space-x-3">
              <span className="text-3xl">{type.icon}</span>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-gray-900 mb-1">{type.name}</h3>
                <p className="text-sm text-gray-600 mb-2">{type.description}</p>
                <p className="text-xs text-indigo-600 font-medium">
                  Best for: {type.bestFor}
                </p>
              </div>
            </div>
          </motion.button>
        ))}
      </div>
    </div>
  );
};
