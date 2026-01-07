import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';

const UploadPage = () => {
  const [formData, setFormData] = useState({
    title: '',
    abstract: '',
    authors: '',
    year: new Date().getFullYear(),
    tags: '',
    privacy_level: 'private',
  });
  const [pdfFile, setPdfFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setPdfFile(file);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const submitData = new FormData();
      submitData.append('title', formData.title);
      submitData.append('abstract', formData.abstract);
      submitData.append('authors', formData.authors);
      submitData.append('year', formData.year.toString());
      submitData.append('privacy_level', formData.privacy_level);

      if (formData.tags) {
        submitData.append('tags', formData.tags);
      }

      if (pdfFile) {
        submitData.append('pdf_file', pdfFile);
      }

      await api.post('/projects/', submitData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload project');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-6">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow rounded-lg p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">Upload Project</h1>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                Title *
              </label>
              <input
                type="text"
                id="title"
                name="title"
                required
                value={formData.title}
                onChange={handleInputChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label htmlFor="abstract" className="block text-sm font-medium text-gray-700">
                Abstract *
              </label>
              <textarea
                id="abstract"
                name="abstract"
                required
                rows={4}
                value={formData.abstract}
                onChange={handleInputChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label htmlFor="authors" className="block text-sm font-medium text-gray-700">
                Authors (comma separated) *
              </label>
              <input
                type="text"
                id="authors"
                name="authors"
                required
                value={formData.authors}
                onChange={handleInputChange}
                placeholder="e.g. John Doe, Jane Smith"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label htmlFor="year" className="block text-sm font-medium text-gray-700">
                Year *
              </label>
              <input
                type="number"
                id="year"
                name="year"
                required
                min="2000"
                max={new Date().getFullYear() + 1}
                value={formData.year}
                onChange={handleInputChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label htmlFor="tags" className="block text-sm font-medium text-gray-700">
                Tags (comma separated)
              </label>
              <input
                type="text"
                id="tags"
                name="tags"
                value={formData.tags}
                onChange={handleInputChange}
                placeholder="e.g. web development, react, api"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label htmlFor="privacy_level" className="block text-sm font-medium text-gray-700">
                Privacy Level
              </label>
              <select
                id="privacy_level"
                name="privacy_level"
                value={formData.privacy_level}
                onChange={handleInputChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="public">Public</option>
                <option value="private">Private</option>
                <option value="restricted">Restricted</option>
              </select>
            </div>

            <div>
              <label htmlFor="files" className="block text-sm font-medium text-gray-700">
                Files
              </label>
              <input
                type="file"
                id="files"
                multiple
                accept=".pdf,.zip,.docx,.pptx"
                onChange={handleFileChange}
                className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
              />
              <p className="mt-1 text-sm text-gray-500">
                Supported formats: PDF, ZIP, DOCX, PPTX
              </p>
            </div>

            {error && (
              <div className="text-red-600 text-sm">
                {error}
              </div>
            )}

            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => navigate('/dashboard')}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 bg-indigo-600 text-white rounded-md text-sm font-medium hover:bg-indigo-700 disabled:opacity-50"
              >
                {loading ? 'Uploading...' : 'Upload Project'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;