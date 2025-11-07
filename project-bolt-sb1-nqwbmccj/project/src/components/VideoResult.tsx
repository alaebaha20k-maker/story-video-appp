import { Download, Share2, RotateCcw, FileText, Calendar, Clock } from 'lucide-react';
import { VideoResult as VideoResultType } from '../types';
import { getVideoUrl } from '../utils/api';
import { motion } from 'framer-motion';

interface VideoResultProps {
  result: VideoResultType;
  onGenerateAnother: () => void;
}

export const VideoResult = ({ result, onGenerateAnother }: VideoResultProps) => {
  const videoUrl = getVideoUrl(result.videoPath);

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = videoUrl;
    link.download = `${result.topic.replace(/\s+/g, '_')}.mp4`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: result.topic,
          text: `Check out my AI-generated video: ${result.topic}`,
          url: videoUrl,
        });
      } catch (err) {
        console.log('Share canceled');
      }
    } else {
      navigator.clipboard.writeText(videoUrl);
      alert('Link copied to clipboard!');
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl shadow-md overflow-hidden"
    >
      <div className="bg-gradient-to-r from-green-600 to-emerald-600 p-6 text-white">
        <h2 className="text-3xl font-bold mb-2">Your Video is Ready!</h2>
        <p className="text-green-100">Professional video generated successfully</p>
      </div>

      <div className="p-6 space-y-6">
        <div className="aspect-video bg-black rounded-lg overflow-hidden">
          <video
            src={videoUrl}
            controls
            className="w-full h-full"
            preload="metadata"
          >
            Your browser does not support the video tag.
          </video>
        </div>

        <div className="bg-gray-50 rounded-lg p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">{result.topic}</h3>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
            <div className="flex items-center space-x-2 text-gray-700">
              <Clock className="w-5 h-5 text-indigo-600" />
              <div>
                <p className="text-xs text-gray-500">Duration</p>
                <p className="font-semibold">{result.duration}</p>
              </div>
            </div>
            <div className="flex items-center space-x-2 text-gray-700">
              <Calendar className="w-5 h-5 text-indigo-600" />
              <div>
                <p className="text-xs text-gray-500">Generated</p>
                <p className="font-semibold">
                  {new Date(result.generatedAt).toLocaleDateString()}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2 text-gray-700">
              <FileText className="w-5 h-5 text-indigo-600" />
              <div>
                <p className="text-xs text-gray-500">Scenes</p>
                <p className="font-semibold">{result.sceneCount || 'N/A'}</p>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <span className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm font-medium">
              {result.storyType}
            </span>
            <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium">
              {result.imageStyle}
            </span>
            <span className="px-3 py-1 bg-pink-100 text-pink-700 rounded-full text-sm font-medium">
              {result.voice}
            </span>
          </div>

          {result.wordCount && (
            <p className="text-sm text-gray-600 mt-4">
              <span className="font-semibold">Word count:</span> {result.wordCount} words
            </p>
          )}

          {result.characters && result.characters.length > 0 && (
            <div className="mt-4">
              <p className="text-sm font-semibold text-gray-700 mb-2">Characters:</p>
              <div className="flex flex-wrap gap-2">
                {result.characters.map((char, i) => (
                  <span
                    key={i}
                    className="px-3 py-1 bg-gray-200 text-gray-700 rounded-full text-sm"
                  >
                    {char}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <button
            onClick={handleDownload}
            className="flex items-center justify-center space-x-2 px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg hover:from-green-700 hover:to-emerald-700 transition-all shadow-md hover:shadow-lg"
          >
            <Download className="w-5 h-5" />
            <span className="font-semibold">Download Video</span>
          </button>

          <button
            onClick={handleShare}
            className="flex items-center justify-center space-x-2 px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-all"
          >
            <Share2 className="w-5 h-5" />
            <span className="font-semibold">Share</span>
          </button>

          <button
            onClick={onGenerateAnother}
            className="flex items-center justify-center space-x-2 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-all"
          >
            <RotateCcw className="w-5 h-5" />
            <span className="font-semibold">Generate Another</span>
          </button>
        </div>
      </div>
    </motion.div>
  );
};
