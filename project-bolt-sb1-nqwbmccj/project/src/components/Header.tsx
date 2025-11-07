import { Video } from 'lucide-react';

interface HeaderProps {
  currentPage: 'home' | 'gallery';
  onNavigate: (page: 'home' | 'gallery') => void;
}

export const Header = ({ currentPage, onNavigate }: HeaderProps) => {
  return (
    <header className="bg-gradient-to-r from-indigo-600 to-pink-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Video className="w-8 h-8" />
            <div>
              <h1 className="text-2xl font-bold">AI Video Generator</h1>
              <p className="text-sm text-indigo-100">Professional Story Videos in Minutes</p>
            </div>
          </div>
          <nav className="flex space-x-4">
            <button
              onClick={() => onNavigate('home')}
              className={`px-4 py-2 rounded-lg transition-all ${
                currentPage === 'home'
                  ? 'bg-white text-indigo-600 font-semibold'
                  : 'bg-indigo-700 hover:bg-indigo-800'
              }`}
            >
              Home
            </button>
            <button
              onClick={() => onNavigate('gallery')}
              className={`px-4 py-2 rounded-lg transition-all ${
                currentPage === 'gallery'
                  ? 'bg-white text-indigo-600 font-semibold'
                  : 'bg-indigo-700 hover:bg-indigo-800'
              }`}
            >
              Gallery
            </button>
          </nav>
        </div>
      </div>
    </header>
  );
};
