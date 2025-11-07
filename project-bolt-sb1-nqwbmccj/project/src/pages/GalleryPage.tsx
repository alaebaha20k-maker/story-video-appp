import { useEffect, useState } from 'react';
import { Film, Calendar, Trash2, Loader2 } from 'lucide-react';
import { supabase, SavedVideo } from '../lib/supabase';
import { getVideoUrl } from '../utils/api';
import { motion } from 'framer-motion';

export const GalleryPage = () => {
  const [videos, setVideos] = useState<SavedVideo[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedVideo, setSelectedVideo] = useState<SavedVideo | null>(null);

  useEffect(() => {
    loadVideos();
  }, []);

  const loadVideos = async () => {
    try {
      const { data, error } = await supabase
        .from('generated_videos')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) throw error;
      setVideos(data || []);
    } catch (error) {
      console.error('Error loading videos:', error);
    } finally {
      setLoading(false);
    }
  };

  const deleteVideo = async (id: string) => {
    if (!confirm('Are you sure you want to delete this video?')) return;

    try {
      const { error } = await supabase
        .from('generated_videos')
        .delete()
        .eq('id', id);

      if (error) throw error;
      setVideos(videos.filter(v => v.id !== id));
      if (selectedVideo?.id === id) setSelectedVideo(null);
    } catch (error) {
      console.error('Error deleting video:', error);
      alert('Failed to delete video');
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto p-4">
        <div className="flex items-center justify-center h-96">
          <Loader2 className="w-12 h-12 animate-spin text-indigo-600" />
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-4 space-y-6">
      <div className="bg-white rounded-xl shadow-md p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-3xl font-bold text-gray-900">Your Video Gallery</h2>
            <p className="text-gray-600 mt-1">
              {videos.length} {videos.length === 1 ? 'video' : 'videos'} generated
            </p>
          </div>
          <Film className="w-12 h-12 text-indigo-600" />
        </div>

        {videos.length === 0 ? (
          <div className="text-center py-12">
            <Film className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No videos yet</h3>
            <p className="text-gray-600">
              Generate your first video to see it appear here
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {videos.map((video) => (
              <motion.div
                key={video.id}
                whileHover={{ scale: 1.02 }}
                className="bg-gray-50 rounded-lg overflow-hidden border-2 border-gray-200 hover:border-indigo-400 transition-all cursor-pointer"
                onClick={() => setSelectedVideo(video)}
              >
                <div className="aspect-video bg-gradient-to-br from-indigo-600 to-pink-600 flex items-center justify-center">
                  <Film className="w-16 h-16 text-white opacity-50" />
                </div>
                <div className="p-4">
                  <h3 className="font-bold text-gray-900 mb-2 truncate">{video.topic}</h3>
                  <div className="space-y-1 text-sm text-gray-600 mb-3">
                    <div className="flex items-center space-x-2">
                      <Calendar className="w-4 h-4" />
                      <span>{new Date(video.created_at).toLocaleDateString()}</span>
                    </div>
                    <p>Duration: {video.duration} min</p>
                  </div>
                  <div className="flex flex-wrap gap-1 mb-3">
                    <span className="px-2 py-1 bg-indigo-100 text-indigo-700 rounded text-xs">
                      {video.story_type}
                    </span>
                    <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs">
                      {video.image_style}
                    </span>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteVideo(video.id);
                    }}
                    className="w-full py-2 bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors flex items-center justify-center space-x-2"
                  >
                    <Trash2 className="w-4 h-4" />
                    <span>Delete</span>
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {selectedVideo && (
        <div
          className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4 z-50"
          onClick={() => setSelectedVideo(null)}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-2xl font-bold text-gray-900">{selectedVideo.topic}</h3>
                <button
                  onClick={() => setSelectedVideo(null)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ✕
                </button>
              </div>
              <div className="aspect-video bg-black rounded-lg overflow-hidden mb-4">
                <video
                  src={getVideoUrl(selectedVideo.video_path)}
                  controls
                  className="w-full h-full"
                  autoPlay
                >
                  Your browser does not support the video tag.
                </video>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">Story Type</p>
                  <p className="font-semibold">{selectedVideo.story_type}</p>
                </div>
                <div>
                  <p className="text-gray-600">Image Style</p>
                  <p className="font-semibold">{selectedVideo.image_style}</p>
                </div>
                <div>
                  <p className="text-gray-600">Duration</p>
                  <p className="font-semibold">{selectedVideo.duration} min</p>
                </div>
                <div>
                  <p className="text-gray-600">Created</p>
                  <p className="font-semibold">
                    {new Date(selectedVideo.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};
