import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, X, Image as ImageIcon } from 'lucide-react';
import { useVideoStore } from '../store/useVideoStore';

export const ImageUpload = () => {
  const { manualImages, setManualImages } = useVideoStore();

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
    },
    multiple: true,
  });

  const removeImage = (index: number) => {
    setManualImages(manualImages.filter((_, i) => i !== index));
  };

  return (
    <div className="bg-white rounded-xl shadow-md p-6 space-y-4">
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-2">Upload Your Images</h2>
        <p className="text-gray-600">Add custom images for your video</p>
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
          <p className="text-indigo-600 font-medium">Drop the images here...</p>
        ) : (
          <div>
            <p className="text-gray-700 font-medium mb-1">
              Drag & drop images here, or click to select
            </p>
            <p className="text-sm text-gray-500">Accepts: PNG, JPG, WEBP</p>
          </div>
        )}
      </div>

      {manualImages.length > 0 && (
        <div>
          <h3 className="font-semibold text-gray-900 mb-3">
            Uploaded Images ({manualImages.length})
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {manualImages.map((file, index) => (
              <div key={index} className="relative group">
                <div className="aspect-square rounded-lg overflow-hidden border-2 border-gray-200 bg-gray-100 flex items-center justify-center">
                  <ImageIcon className="w-8 h-8 text-gray-400" />
                </div>
                <button
                  onClick={() => removeImage(index)}
                  className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <X className="w-4 h-4" />
                </button>
                <p className="text-xs text-gray-600 mt-1 truncate">{file.name}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
