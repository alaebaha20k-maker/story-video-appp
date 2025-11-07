import { useState, useEffect } from 'react';
import { Search, X, Film, Image as ImageIcon, Check, Loader2 } from 'lucide-react';
import { useVideoStore } from '../store/useVideoStore';

interface MediaItem {
  id: number;
  type: 'image' | 'video';
  thumbnail: string;
  videoUrl?: string;
  photographer: string;
}

export const StockMediaSelector = () => {
  const { stockKeywords, selectedStockMedia, setSelectedStockMedia } = useVideoStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [mediaItems, setMediaItems] = useState<MediaItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'images' | 'videos' | 'both'>('both');

  const searchMedia = async () => {
    if (!searchQuery.trim() && stockKeywords.length === 0) return;

    setLoading(true);
    try {
      const query = searchQuery.trim() || stockKeywords[0] || 'nature';
      
      // Mock data for demonstration (replace with actual Pexels API calls)
      const mockData: MediaItem[] = [
        {
          id: 1,
          type: 'image',
          thumbnail: 'https://images.pexels.com/photos/248797/pexels-photo-248797.jpeg?auto=compress&cs=tinysrgb&w=400',
          photographer: 'Pixabay'
        },
        {
          id: 2,
          type: 'video',
          thumbnail: 'https://images.pexels.com/videos/3045163/free-video-3045163.jpg?auto=compress&cs=tinysrgb&w=400',
          videoUrl: 'https://player.vimeo.com/external/374155469.hd.mp4',
          photographer: 'Pressmaster'
        },
        {
          id: 3,
          type: 'image',
          thumbnail: 'https://images.pexels.com/photos/414612/pexels-photo-414612.jpeg?auto=compress&cs=tinysrgb&w=400',
          photographer: 'James Wheeler'
        },
      ];

      setMediaItems(mockData);
    } catch (error) {
      console.error('Failed to fetch media:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleSelection = (item: MediaItem) => {
    const isSelected = selectedStockMedia.some(m => m.id === item.id);
    if (isSelected) {
      setSelectedStockMedia(selectedStockMedia.filter(m => m.id !== item.id));
    } else {
      setSelectedStockMedia([...selectedStockMedia, item]);
    }
  };

  const isSelected = (id: number) => selectedStockMedia.some(m => m.id === id);

  const filteredMedia = mediaItems.filter(item => {
    if (activeTab === 'both') return true;
    return item.type === activeTab.slice(0, -1) as 'image' | 'video';
  });

  return (
    <div className="bg-white rounded-xl shadow-md p-6 space-y-4">
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-2">Stock Media Library</h2>
        <p className="text-gray-600">Search and select images & videos from Pexels</p>
      </div>

      {/* Search Bar */}
      <div className="flex space-x-2">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && searchMedia()}
          placeholder="Search for stock media..."
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
        />
        <button
          onClick={searchMedia}
          disabled={loading}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center space-x-2 disabled:opacity-50"
        >
          {loading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Search className="w-5 h-5" />
          )}
          <span>Search</span>
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="flex space-x-2 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('both')}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'both'
              ? 'text-indigo-600 border-b-2 border-indigo-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          All Media
        </button>
        <button
          onClick={() => setActiveTab('images')}
          className={`px-4 py-2 font-medium transition-colors flex items-center space-x-1 ${
            activeTab === 'images'
              ? 'text-indigo-600 border-b-2 border-indigo-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <ImageIcon className="w-4 h-4" />
          <span>Images</span>
        </button>
        <button
          onClick={() => setActiveTab('videos')}
          className={`px-4 py-2 font-medium transition-colors flex items-center space-x-1 ${
            activeTab === 'videos'
              ? 'text-indigo-600 border-b-2 border-indigo-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Film className="w-4 h-4" />
          <span>Videos</span>
        </button>
      </div>

      {/* Media Grid */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
        </div>
      ) : filteredMedia.length > 0 ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
          {filteredMedia.map((item) => (
            <div
              key={item.id}
              onClick={() => toggleSelection(item)}
              className={`relative group cursor-pointer rounded-lg overflow-hidden border-2 transition-all ${
                isSelected(item.id)
                  ? 'border-indigo-600 ring-2 ring-indigo-200'
                  : 'border-gray-200 hover:border-indigo-400'
              }`}
            >
              <div className="aspect-square bg-gray-100">
                {item.type === 'video' ? (
                  <div className="relative w-full h-full">
                    <img
                      src={item.thumbnail}
                      alt="Video thumbnail"
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-30">
                      <Film className="w-8 h-8 text-white" />
                    </div>
                  </div>
                ) : (
                  <img
                    src={item.thumbnail}
                    alt="Stock media"
                    className="w-full h-full object-cover"
                  />
                )}
              </div>

              {/* Selection Indicator */}
              {isSelected(item.id) && (
                <div className="absolute top-2 right-2 bg-indigo-600 text-white rounded-full p-1">
                  <Check className="w-4 h-4" />
                </div>
              )}

              {/* Type Badge */}
              <div className="absolute bottom-2 left-2">
                {item.type === 'video' ? (
                  <span className="bg-indigo-600 text-white text-xs px-2 py-1 rounded flex items-center space-x-1">
                    <Film className="w-3 h-3" />
                    <span>Video</span>
                  </span>
                ) : (
                  <span className="bg-green-600 text-white text-xs px-2 py-1 rounded flex items-center space-x-1">
                    <ImageIcon className="w-3 h-3" />
                    <span>Image</span>
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 text-gray-500">
          <Search className="w-12 h-12 mx-auto mb-2 text-gray-400" />
          <p>Search for stock media to get started</p>
        </div>
      )}

      {/* Selected Count */}
      {selectedStockMedia.length > 0 && (
        <div className="flex items-center justify-between p-4 bg-indigo-50 rounded-lg">
          <span className="text-indigo-900 font-medium">
            {selectedStockMedia.length} item{selectedStockMedia.length !== 1 ? 's' : ''} selected
          </span>
          <button
            onClick={() => setSelectedStockMedia([])}
            className="text-indigo-600 hover:text-indigo-800 font-medium"
          >
            Clear All
          </button>
        </div>
      )}
    </div>
  );
};
