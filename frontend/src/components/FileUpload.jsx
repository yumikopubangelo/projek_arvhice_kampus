import React, { useState, useRef } from 'react';
import api from '../api/client';

const FileUpload = ({
  projectId,
  existingFiles = [],
  onFilesChange,
  maxFiles = 10,
  allowedTypes = ['.pdf', '.docx', '.doc', '.txt', '.csv', '.xlsx', '.xls', '.zip', '.rar', '.tar.gz', '.py', '.ipynb', '.r', '.sql', '.md', '.pptx', '.ppt'],
  maxFileSize = 20 // MB
}) => {
  const [files, setFiles] = useState(existingFiles);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const fileInputRef = useRef(null);

  const validateFile = (file) => {
    // Check file size
    if (file.size > maxFileSize * 1024 * 1024) {
      return `File size exceeds ${maxFileSize}MB limit`;
    }

    // Check file type
    const fileExt = '.' + file.name.split('.').pop().toLowerCase();
    if (!allowedTypes.includes(fileExt)) {
      return `File type ${fileExt} not allowed. Allowed types: ${allowedTypes.join(', ')}`;
    }

    return null;
  };

  const handleFileSelect = async (event) => {
    const selectedFiles = Array.from(event.target.files);
    if (selectedFiles.length === 0) return;

    setError('');
    setSuccess('');

    // Validate files before creating FormData
    for (const file of selectedFiles) {
      const validationError = validateFile(file);
      if (validationError) {
        setError(validationError);
        return;
      }
    }

    if (files.length + selectedFiles.length > maxFiles) {
      setError(`Cannot upload ${selectedFiles.length} file(s). Maximum of ${maxFiles} files allowed.`);
      return;
    }

    setUploading(true);
    const formData = new FormData();
    selectedFiles.forEach(file => {
      formData.append('files', file); // The backend expects a list of files under the key 'files'
    });

    try {
      const response = await api.post(`/projects/${projectId}/files`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          // Simple progress for the whole batch
          setUploadProgress({ batch: percentCompleted });
        }
      });

      // The response.data should be an array of the newly created file objects
      const newFiles = response.data.map(f => ({
        id: f.id, // Make sure to use the ID from the backend response
        name: f.original_filename,
        size: f.file_size,
        path: f.saved_path,
        uploaded: true,
      }));

      const updatedFiles = [...files, ...newFiles];
      setFiles(updatedFiles);
      if (onFilesChange) {
        onFilesChange(updatedFiles);
      }

      const uploadedCount = newFiles.length;
      setSuccess(`${uploadedCount} file${uploadedCount > 1 ? 's' : ''} uploaded successfully!`);

    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload files');
    } finally {
      setUploading(false);
      setUploadProgress({});
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDeleteFile = async (fileId) => {
    try {
      // Use the new, correct endpoint for deleting a file by its ID
      await api.delete(`/files/${fileId}`);
      const updatedFiles = files.filter(file => file.id !== fileId);
      setFiles(updatedFiles);
      if (onFilesChange) {
        onFilesChange(updatedFiles);
      }
      setSuccess('File deleted successfully.');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete file');
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (fileName) => {
    const ext = fileName.split('.').pop().toLowerCase();
    const iconMap = {
      pdf: '📄',
      docx: '📝',
      doc: '📝',
      txt: '📄',
      csv: '📊',
      xlsx: '📊',
      xls: '📊',
      zip: '📦',
      rar: '📦',
      'tar.gz': '📦',
      py: '🐍',
      ipynb: '📓',
      r: '📈',
      sql: '🗄️',
      md: '📝',
      pptx: '📊',
      ppt: '📊'
    };
    return iconMap[ext] || '📄';
  };

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Additional Files
        </label>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={allowedTypes.join(',')}
          onChange={handleFileSelect}
          disabled={uploading}
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 disabled:opacity-50"
        />
        <p className="mt-1 text-sm text-gray-500">
          Upload additional files (max {maxFiles} files, {maxFileSize}MB each). Allowed types: {allowedTypes.join(', ')}
        </p>
      </div>

      {error && (
        <div className="text-red-600 text-sm bg-red-50 p-3 rounded-md">
          {typeof error === 'string' ? error : JSON.stringify(error)}
        </div>
      )}

      {success && (
        <div className="text-green-600 text-sm bg-green-50 p-3 rounded-md">
          {success}
        </div>
      )}

      <div className="space-y-2">
        <h4 className="text-sm font-medium text-gray-700">Uploaded Files ({files.length})</h4>
        <div className="max-h-60 overflow-y-auto space-y-2">
          {files.length > 0 ? (
            files.map((file, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                <div className="flex items-center space-x-3">
                  <span className="text-lg">{getFileIcon(file.name)}</span>
                  <div>
                    <p className="text-sm font-medium text-gray-900 truncate max-w-xs">
                      {file.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatFileSize(file.size)}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {uploadProgress[file.name] !== undefined && uploadProgress[file.name] < 100 && (
                    <div className="text-xs text-blue-600">
                      {uploadProgress[file.name]}%
                    </div>
                  )}
                  <button
                    onClick={() => handleDeleteFile(file.id)}
                    className="text-red-600 hover:text-red-800 text-sm"
                    disabled={uploading}
                  >
                    ✕
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="p-4 bg-gray-50 rounded-md text-center">
              <p className="text-sm text-gray-500">Belum ada file yang diupload</p>
            </div>
          )}
        </div>
      </div>

      {uploading && (
        <div className="text-sm text-blue-600">
          Uploading files...
        </div>
      )}
    </div>
  );
};

export default FileUpload;