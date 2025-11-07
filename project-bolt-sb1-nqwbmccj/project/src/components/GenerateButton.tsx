import { Sparkles, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';

interface GenerateButtonProps {
  onClick: () => void;
  isGenerating: boolean;
  disabled?: boolean;
}

export const GenerateButton = ({ onClick, isGenerating, disabled }: GenerateButtonProps) => {
  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <motion.button
        whileHover={!isGenerating && !disabled ? { scale: 1.02 } : {}}
        whileTap={!isGenerating && !disabled ? { scale: 0.98 } : {}}
        onClick={onClick}
        disabled={isGenerating || disabled}
        className={`w-full py-6 rounded-xl font-bold text-xl text-white transition-all shadow-lg ${
          isGenerating || disabled
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-gradient-to-r from-indigo-600 to-pink-600 hover:from-indigo-700 hover:to-pink-700 hover:shadow-xl'
        }`}
      >
        <span className="flex items-center justify-center space-x-3">
          {isGenerating ? (
            <>
              <Loader2 className="w-7 h-7 animate-spin" />
              <span>Generating Your Professional Video...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-7 h-7" />
              <span>Generate Professional Video</span>
            </>
          )}
        </span>
      </motion.button>

      <div className="mt-4 text-center">
        <p className="text-sm text-gray-600">
          Typically takes 2-5 minutes depending on your settings
        </p>
      </div>
    </div>
  );
};
