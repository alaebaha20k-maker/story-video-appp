import { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { GeneratorPage } from './pages/GeneratorPage';
import { GalleryPage } from './pages/GalleryPage';
import { checkHealth } from './utils/api';
import { AlertCircle, CheckCircle, Loader2 } from 'lucide-react';

function App() {
  const [currentPage, setCurrentPage] = useState<'home' | 'gallery'>('home');
  const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    const checkApiStatus = async () => {
      const isOnline = await checkHealth();
      setApiStatus(isOnline ? 'online' : 'offline');
    };

    checkApiStatus();
    const interval = setInterval(checkApiStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gray-100">
      <Header currentPage={currentPage} onNavigate={setCurrentPage} />

      <div className="py-8">
        {apiStatus === 'offline' && (
          <div className="max-w-7xl mx-auto px-4 mb-6">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
              <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-red-900 mb-1">API Server Offline</h3>
                <p className="text-red-700 text-sm">
                  Cannot connect to http://localhost:5000. Please ensure the API server is running.
                </p>
              </div>
            </div>
          </div>
        )}

        {apiStatus === 'online' && (
          <div className="max-w-7xl mx-auto px-4 mb-6">
            <div className="bg-green-50 border border-green-200 rounded-lg p-3 flex items-center space-x-2">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <p className="text-green-800 text-sm font-medium">API Server Connected</p>
            </div>
          </div>
        )}

        {apiStatus === 'checking' && (
          <div className="max-w-7xl mx-auto px-4 mb-6">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-center space-x-2">
              <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
              <p className="text-blue-800 text-sm font-medium">Checking API connection...</p>
            </div>
          </div>
        )}

        {currentPage === 'home' ? <GeneratorPage /> : <GalleryPage />}
      </div>

      <footer className="bg-white border-t border-gray-200 mt-12 py-8">
        <div className="max-w-7xl mx-auto px-4 text-center text-gray-600">
          <p className="text-sm">
            AI Video Generator - Professional Story Videos in Minutes
          </p>
          <p className="text-xs mt-2">Powered by AI technology</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
