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
    assignment_type: '',
    privacy_level: 'private',
    code_repo_url: '',
    dataset_url: '',
    video_url: '',
  });
  const [files, setFiles] = useState({
    pdf: null,
    codeZip: [],
    dataset: [],
    slides: [],
    additional: []
  });
  const [status, setStatus] = useState({
    loading: false,
    error: null,
    success: null,
  });
  const navigate = useNavigate();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleFileChange = (fileType) => (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles(prev => ({
      ...prev,
      [fileType]: fileType === 'pdf' ? selectedFiles[0] : selectedFiles
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus({ loading: true, error: null, success: null });

    try {
      // 1. Validasi Frontend Sederhana
      if (!files.pdf) {
        throw new Error("PDF report is required.");
      }
      if (!formData.title || !formData.abstract || !formData.authors || !formData.assignment_type) {
        throw new Error("Please fill in all required fields.");
      }

      // 2. Mempersiapkan data untuk dikirim
      const submitData = new FormData();
      Object.keys(formData).forEach(key => {
        if (formData[key]) {
          submitData.append(key, formData[key]);
        }
      });
      
      submitData.append('main_file', files.pdf);

      const supplementaryFiles = [
        ...(files.codeZip || []),
        ...(files.dataset || []),
        ...(files.slides || []),
        ...(files.additional || [])
      ];

      supplementaryFiles.forEach(file => {
        submitData.append('supplementary_files', file);
      });

      // 3. Melakukan panggilan API
      await api.post('/projects/', submitData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // 4. Menangani keberhasilan
      setStatus({ loading: false, error: null, success: 'Project uploaded successfully! Redirecting to dashboard...' });
      setTimeout(() => {
        navigate('/dashboard');
      }, 2000);

    } catch (err) {
      // 5. Menangani error
      let errorMessage = err.response?.data?.detail || err.message || 'Failed to upload project. Please try again.';
      if (typeof errorMessage === 'object') {
        errorMessage = JSON.stringify(errorMessage);
      }
      setStatus({ loading: false, error: errorMessage, success: null });
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-6">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow rounded-lg p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">Upload Project</h1>

          {/* Status Messages */}
          {status.error && (
            <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
              <p className="font-bold">Error!</p>
              <p>{status.error}</p>
            </div>
          )}
          {status.success && (
            <div className="mb-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded-lg">
              <p className="font-bold">Success!</p>
              <p>{status.success}</p>
            </div>
          )}

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
              <label htmlFor="assignment_type" className="block text-sm font-medium text-gray-700">
                Assignment Type *
              </label>
              <select
                id="assignment_type"
                name="assignment_type"
                required
                value={formData.assignment_type}
                onChange={handleInputChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="">Select assignment type</option>
                <option value="skripsi">Tugas Akhir/Skripsi</option>
                <option value="tugas_matkul">Tugas Mata Kuliah</option>
                <option value="laporan_kp">Laporan Kerja Praktik</option>
                <option value="lainnya">Lainnya</option>
              </select>
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
                <option value="private">Private</option>
                <option value="advisor">Advisor</option>
                <option value="class">Class</option>
                <option value="public">Public</option>
              </select>
            </div>

            <div>
              <label htmlFor="code_repo_url" className="block text-sm font-medium text-gray-700">
                Code Repository URL
              </label>
              <input
                type="url"
                id="code_repo_url"
                name="code_repo_url"
                value={formData.code_repo_url}
                onChange={handleInputChange}
                placeholder="https://github.com/username/repo"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label htmlFor="dataset_url" className="block text-sm font-medium text-gray-700">
                Dataset URL
              </label>
              <input
                type="url"
                id="dataset_url"
                name="dataset_url"
                value={formData.dataset_url}
                onChange={handleInputChange}
                placeholder="https://example.com/dataset"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label htmlFor="video_url" className="block text-sm font-medium text-gray-700">
                Demo Video URL
              </label>
              <input
                type="url"
                id="video_url"
                name="video_url"
                value={formData.video_url}
                onChange={handleInputChange}
                placeholder="https://youtube.com/watch?v=..."
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                PDF Report *
              </label>
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange('pdf')}
                className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
              />
              <p className="mt-1 text-sm text-gray-500">
                Required: PDF report (max 10MB)
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Code Files
              </label>
              <input
                type="file"
                accept=".zip,.py,.ipynb,.r,.sql,.md"
                multiple
                onChange={handleFileChange('codeZip')}
                className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
              />
              <p className="mt-1 text-sm text-gray-500">
                Optional: Code files (ZIP, Python, Jupyter, R, SQL, Markdown) - max 20MB each
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Dataset Files
              </label>
              <input
                type="file"
                accept=".csv,.xlsx,.xls,.json,.txt"
                multiple
                onChange={handleFileChange('dataset')}
                className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
              />
              <p className="mt-1 text-sm text-gray-500">
                Optional: Dataset files (CSV, Excel, JSON, TXT) - max 15MB each
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Presentation Slides
              </label>
              <input
                type="file"
                accept=".pptx,.ppt"
                multiple
                onChange={handleFileChange('slides')}
                className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
              />
              <p className="mt-1 text-sm text-gray-500">
                Optional: PowerPoint files - max 10MB each
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Additional Files
              </label>
              <input
                type="file"
                accept=".pdf,.docx,.doc,.txt,.csv,.xlsx,.xls,.zip,.rar,.tar.gz,.py,.ipynb,.r,.sql,.md,.pptx,.ppt"
                multiple
                onChange={handleFileChange('additional')}
                className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
              />
              <p className="mt-1 text-sm text-gray-500">
                Optional: Any additional files (documents, images, archives, etc.) - max 20MB each
              </p>
            </div>

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
                disabled={status.loading || status.success}
                className="px-4 py-2 bg-indigo-600 text-white rounded-md text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {status.loading ? 'Uploading...' : 'Upload Project'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;