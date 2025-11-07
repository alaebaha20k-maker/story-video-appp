import { useVideoStore } from '../store/useVideoStore';
import { DURATION_LABELS } from '../constants/options';

export const BasicSettings = () => {
  const { topic, duration, setTopic, setDuration } = useVideoStore();

  const getDurationLabel = (dur: number) => {
    const label = DURATION_LABELS.find((l) => dur >= l.min && dur <= l.max);
    return label ? label.label : 'Custom';
  };

  const estimatedWords = Math.round(duration * 150);

  return (
    <div className="bg-white rounded-xl shadow-md p-6 space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Basic Settings</h2>
        <p className="text-gray-600">Start by describing your story topic and desired length</p>
      </div>

      <div>
        <label htmlFor="topic" className="block text-sm font-medium text-gray-700 mb-2">
          Story Topic
        </label>
        <textarea
          id="topic"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Enter your story topic... (e.g., The Vanishing Lighthouse)"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none transition-shadow"
          rows={3}
        />
        <div className="flex justify-between mt-2 text-sm text-gray-500">
          <span>Describe your story in a few words</span>
          <span>{topic.length} characters</span>
        </div>
      </div>

      <div>
        <div className="flex justify-between items-center mb-3">
          <label htmlFor="duration" className="block text-sm font-medium text-gray-700">
            Video Duration
          </label>
          <span className="text-sm font-semibold text-indigo-600">
            {duration} minutes ({getDurationLabel(duration)})
          </span>
        </div>
        <input
          id="duration"
          type="range"
          min="1"
          max="60"
          value={duration}
          onChange={(e) => setDuration(Number(e.target.value))}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
        />
        <div className="flex justify-between mt-2 text-xs text-gray-500">
          <span>Quick (1-5 min)</span>
          <span>Medium (6-15 min)</span>
          <span>Long (16-30 min)</span>
          <span>Epic (31-60 min)</span>
        </div>
        <p className="text-sm text-gray-600 mt-2">
          Selected: {duration} minutes (~{estimatedWords} words)
        </p>
      </div>
    </div>
  );
};
