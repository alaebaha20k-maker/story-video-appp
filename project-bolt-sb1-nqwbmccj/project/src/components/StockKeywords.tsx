import { useState } from 'react';
import { X, Plus } from 'lucide-react';
import { useVideoStore } from '../store/useVideoStore';

export const StockKeywords = () => {
  const { stockKeywords, setStockKeywords } = useVideoStore();
  const [inputValue, setInputValue] = useState('');

  const addKeyword = () => {
    if (inputValue.trim()) {
      setStockKeywords([...stockKeywords, inputValue.trim()]);
      setInputValue('');
    }
  };

  const removeKeyword = (index: number) => {
    setStockKeywords(stockKeywords.filter((_, i) => i !== index));
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addKeyword();
    } else if (e.key === ',') {
      e.preventDefault();
      addKeyword();
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-md p-6 space-y-4">
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-2">Stock Search Keywords</h2>
        <p className="text-gray-600">Add keywords to find relevant stock media from Pexels</p>
      </div>

      <div className="flex space-x-2">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="Enter keyword and press Enter or comma"
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
        />
        <button
          onClick={addKeyword}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center space-x-2"
        >
          <Plus className="w-5 h-5" />
          <span>Add</span>
        </button>
      </div>

      {stockKeywords.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {stockKeywords.map((keyword, index) => (
            <span
              key={index}
              className="inline-flex items-center space-x-2 bg-indigo-100 text-indigo-700 px-3 py-1 rounded-full"
            >
              <span className="text-sm font-medium">{keyword}</span>
              <button
                onClick={() => removeKeyword(index)}
                className="hover:bg-indigo-200 rounded-full p-0.5 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </span>
          ))}
        </div>
      )}

      <p className="text-sm text-gray-500">
        Or leave empty for automatic keyword detection from your story
      </p>
      <div className="flex flex-wrap gap-2">
        <span className="text-xs text-gray-500">Example tags:</span>
        {['nature', 'city', 'ocean', 'mountain', 'space', 'people'].map((example) => (
          <button
            key={example}
            onClick={() => setStockKeywords([...stockKeywords, example])}
            className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded hover:bg-gray-200 transition-colors"
          >
            {example}
          </button>
        ))}
      </div>
    </div>
  );
};
