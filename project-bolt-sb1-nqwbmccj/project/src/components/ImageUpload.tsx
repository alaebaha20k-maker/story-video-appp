import { useCallback, useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, X, Image as ImageIcon, Film } from 'lucide-react';
import { useVideoStore } from '../store/useVideoStore';

export const ImageUpload = () => {
  const { manualImages, setManualImages } = useVideoStore();
  const [previews, setPreviews] = useState<{ [key: number]: string }>({});

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      setManualImages([...manualImages, ...acceptedFiles]);
    },
    [manualImages, setManualImages]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.webp'],
      'video/*': ['.mp4', '.mov', '.avi', '.webm'],
    },
    multiple: true,
  });

  // Generate previews for uploaded files
  useEffect(() => {
    const newPreviews: { [key: number]: string } = {};
    
    manualImages.forEach((file, index) => {
      if (file instanceof File) {
        const url = URL.createObjectURL(file);
        newPreviews[index] = url;
      }
    });
    
    setPreviews(newPreviews);
    
    // Cleanup URLs on unmount
    return () => {
      Object.values(newPreviews).forEach(url => URL.revokeObjectURL(url));
    };
  }, [manualImages]);

  const removeImage = (index: number) => {
    setManualImages(manualImages.filter((_, i) => i !== index));
  };

  const isVideo = (file: File) => file.type.startsWith('video/');
  const isImage = (file: File) => file.type.startsWith('image/');

  return (
    <div className="bg-white rounded-xl shadow-md p-6 space-y-4">
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-2">Upload Media (Images & Videos)</h2>
        <p className="text-gray-600">Add custom images or video clips for your video</p>
      </div>

      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-indigo-600 bg-indigo-50'
            : 'border-gray-300 hover:border-indigo-400 hover:bg-gray-50'
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
        {isDragActive ? (
          <p className="text-indigo-600 font-medium">Drop the files here...</p>
        ) : (
          <div>
            <p className="text-gray-700 font-medium mb-1">
              Drag & drop images or videos here, or click to select
            </p>
            <p className="text-sm text-gray-500">
              Images: PNG, JPG, WEBP | Videos: MP4, MOV, AVI, WEBM
            </p>
          </div>
        )}
      </div>

      {manualImages.length > 0 && (
        <div>
          <h3 className="font-semibold text-gray-900 mb-3">
            Uploaded Media ({manualImages.length})
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {manualImages.map((file, index) => (
              <div key={index} className="relative group">
                <div className="aspect-square rounded-lg overflow-hidden border-2 border-gray-200 bg-gray-100">
                  {isVideo(file) ? (
                    <div className="relative w-full h-full">
                      <video
                        src={previews[index]}
                        className="w-full h-full object-cover"
                        muted
                        loop
                        onMouseEnter={(e) => e.currentTarget.play()}
                        onMouseLeave={(e) => {
                          e.currentTarget.pause();
                          e.currentTarget.currentTime = 0;
                        }}
                      />
                      <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-30 pointer-events-none">
                        <Film className="w-8 h-8 text-white" />
                      </div>
                    </div>
                  ) : isImage(file) ? (
                    <img
                      src={previews[index]}
                      alt={file.name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <ImageIcon className="w-8 h-8 text-gray-400" />
                    </div>
                  )}
                </div>
                <button
                  onClick={() => removeImage(index)}
                  className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <X className="w-4 h-4" />
                </button>
                <div className="mt-1 flex items-center space-x-1">
                  {isVideo(file) && (
                    <Film className="w-3 h-3 text-indigo-600" />
                  )}
                  {isImage(file) && (
                    <ImageIcon className="w-3 h-3 text-green-600" />
                  )}
                  <p className="text-xs text-gray-600 truncate">{file.name}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
