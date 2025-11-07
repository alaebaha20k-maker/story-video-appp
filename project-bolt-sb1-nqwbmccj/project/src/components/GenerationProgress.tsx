import { motion } from 'framer-motion';
import { Loader2, FileText, Image, Mic, Video } from 'lucide-react';

interface GenerationProgressProps {
  progress: number;
  status: string;
  substatus?: string;
  details?: string;
}

export const GenerationProgress = ({
  progress,
  status,
  substatus,
  details,
}: GenerationProgressProps) => {
  const getStageInfo = () => {
    if (progress < 25) {
      return {
        icon: FileText,
        color: 'text-blue-600',
        bg: 'bg-blue-50',
        title: 'Script Generation',
      };
    } else if (progress < 50) {
      return {
        icon: Image,
        color: 'text-purple-600',
        bg: 'bg-purple-50',
        title: 'Image Generation',
      };
    } else if (progress < 75) {
      return {
        icon: Mic,
        color: 'text-green-600',
        bg: 'bg-green-50',
        title: 'Voice Narration',
      };
    } else {
      return {
        icon: Video,
        color: 'text-pink-600',
        bg: 'bg-pink-50',
        title: 'Video Compilation',
      };
    }
  };

  const stage = getStageInfo();
  const StageIcon = stage.icon;

  return (
    <div className="bg-white rounded-xl shadow-md p-8">
      <div className="text-center mb-8">
        <motion.div
          className={`inline-flex items-center justify-center w-20 h-20 rounded-full ${stage.bg} mb-4`}
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
        >
          <StageIcon className={`w-10 h-10 ${stage.color}`} />
        </motion.div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">{status}</h2>
        {substatus && <p className="text-gray-600">{substatus}</p>}
      </div>

      <div className="mb-6">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>{stage.title}</span>
          <span>{Math.round(progress)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-indigo-600 to-pink-600"
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>
      </div>

      {details && (
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-2">Details:</h3>
          <ul className="space-y-1 text-sm text-gray-700">
            {details.split('\n').map((line, i) => (
              <li key={i} className="flex items-start">
                <span className="mr-2">•</span>
                <span>{line}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-6 grid grid-cols-4 gap-4">
        {[
          { label: 'Script', range: [0, 25], icon: FileText },
          { label: 'Images', range: [25, 50], icon: Image },
          { label: 'Voice', range: [50, 75], icon: Mic },
          { label: 'Video', range: [75, 100], icon: Video },
        ].map((step) => {
          const StepIcon = step.icon;
          const isActive = progress >= step.range[0] && progress < step.range[1];
          const isComplete = progress >= step.range[1];
          return (
            <div
              key={step.label}
              className={`text-center p-3 rounded-lg transition-all ${
                isActive
                  ? 'bg-indigo-50 border-2 border-indigo-600'
                  : isComplete
                  ? 'bg-green-50 border-2 border-green-600'
                  : 'bg-gray-50 border-2 border-gray-200'
              }`}
            >
              <StepIcon
                className={`w-6 h-6 mx-auto mb-1 ${
                  isActive
                    ? 'text-indigo-600'
                    : isComplete
                    ? 'text-green-600'
                    : 'text-gray-400'
                }`}
              />
              <p className="text-xs font-medium text-gray-700">{step.label}</p>
            </div>
          );
        })}
      </div>

      <div className="mt-6 flex items-center justify-center space-x-2 text-sm text-gray-500">
        <Loader2 className="w-4 h-4 animate-spin" />
        <span>This may take 2-5 minutes depending on your settings...</span>
      </div>
    </div>
  );
};
