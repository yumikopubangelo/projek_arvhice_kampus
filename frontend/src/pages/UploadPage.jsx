import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import useCourses from '../hooks/useCourses';

const UploadPage = () => {
  const { courses } = useCourses();
  const [formData, setFormData] = useState({
    title: '',
    abstract: '',
    authors: '',
    year: new Date().getFullYear(),
    tags: '',
    assignment_type: '',
    semester: '',
    kelas: '',
    course_code: '',
    lecturer_name: '',
    course_id: '',
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
        throw new Error("Laporan PDF wajib diunggah.");
      }
      if (!formData.title || !formData.abstract || !formData.authors || !formData.assignment_type) {
        throw new Error("Harap isi semua field yang wajib diisi.");
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
      setStatus({ loading: false, error: null, success: 'Proyek berhasil diunggah! Mengalihkan ke dasbor...' });
      setTimeout(() => {
        navigate('/dashboard');
      }, 2000);

    } catch (err) {
      // 5. Menangani error
      let errorMessage = err.response?.data?.detail || err.message || 'Gagal mengunggah proyek. Silakan coba lagi.';
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
          <h1 className="text-2xl font-bold text-gray-900 mb-6">Unggah Proyek</h1>

          {/* Status Messages */}
          {status.error && (
            <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
              <p className="font-bold">Error!</p>
              <p>{status.error}</p>
            </div>
          )}
          {status.success && (
            <div className="mb-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded-lg">
              <p className="font-bold">Sukses!</p>
              <p>{status.success}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                Judul *
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
                Abstrak *
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
                Penulis (pisahkan dengan koma) *
              </label>
              <input
                type="text"
                id="authors"
                name="authors"
                required
                value={formData.authors}
                onChange={handleInputChange}
                placeholder="cth. John Doe, Jane Smith"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label htmlFor="year" className="block text-sm font-medium text-gray-700">
                Tahun *
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
              <label htmlFor="semester" className="block text-sm font-medium text-gray-700">
                Semester
              </label>
              <input
                type="number"
                id="semester"
                name="semester"
                value={formData.semester}
                onChange={handleInputChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label htmlFor="kelas" className="block text-sm font-medium text-gray-700">
                Kelas
              </label>
              <input
                type="text"
                id="kelas"
                name="kelas"
                value={formData.kelas}
                onChange={handleInputChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label htmlFor="course_code" className="block text-sm font-medium text-gray-700">
                Kode Mata Kuliah
              </label>
              <input
                type="text"
                id="course_code"
                name="course_code"
                value={formData.course_code}
                onChange={handleInputChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
            
            <div>
              <label htmlFor="lecturer_name" className="block text-sm font-medium text-gray-700">
                Nama Dosen
              </label>
              <input
                type="text"
                id="lecturer_name"
                name="lecturer_name"
                value={formData.lecturer_name}
                onChange={handleInputChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label htmlFor="course_id" className="block text-sm font-medium text-gray-700">
                Asosiasikan dengan Mata Kuliah (Opsional)
              </label>
              <select
                id="course_id"
                name="course_id"
                value={formData.course_id}
                onChange={handleInputChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="">Pilih mata kuliah (opsional)</option>
                {courses.map((course) => (
                  <option key={course.id} value={course.id}>
                    {course.course_code} - {course.course_name} ({course.semester} {course.year})
                  </option>
                ))}
              </select>
              <p className="mt-1 text-sm text-gray-500">
                Jika proyek ini terkait dengan mata kuliah tertentu
              </p>
            </div>

            <div>
              <label htmlFor="assignment_type" className="block text-sm font-medium text-gray-700">
                Jenis Tugas *
              </label>
              <select
                id="assignment_type"
                name="assignment_type"
                required
                value={formData.assignment_type}
                onChange={handleInputChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="">Pilih jenis tugas</option>
                <option value="skripsi">Tugas Akhir/Skripsi</option>
                <option value="tugas_matkul">Tugas Mata Kuliah</option>
                <option value="laporan_kp">Laporan Kerja Praktik</option>
                <option value="lainnya">Lainnya</option>
              </select>
            </div>

            <div>
              <label htmlFor="tags" className="block text-sm font-medium text-gray-700">
                Tags (pisahkan dengan koma)
              </label>
              <input
                type="text"
                id="tags"
                name="tags"
                value={formData.tags}
                onChange={handleInputChange}
                placeholder="cth. pengembangan web, react, api"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label htmlFor="privacy_level" className="block text-sm font-medium text-gray-700">
                Tingkat Privasi
              </label>
              <select
                id="privacy_level"
                name="privacy_level"
                value={formData.privacy_level}
                onChange={handleInputChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="private">Pribadi</option>
                <option value="advisor">Dosen Pembimbing</option>
                <option value="class">Kelas</option>
                <option value="public">Publik</option>
              </select>
            </div>

            <div>
              <label htmlFor="code_repo_url" className="block text-sm font-medium text-gray-700">
                URL Repositori Kode
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
                URL Dataset
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
                URL Video Demo
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
                Laporan PDF *
              </label>
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange('pdf')}
                className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
              />
              <p className="mt-1 text-sm text-gray-500">
                Wajib: Laporan PDF (maks 10MB)
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                File Kode
              </label>
              <input
                type="file"
                accept=".zip,.py,.ipynb,.r,.sql,.md"
                multiple
                onChange={handleFileChange('codeZip')}
                className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
              />
              <p className="mt-1 text-sm text-gray-500">
                Opsional: File kode (ZIP, Python, Jupyter, R, SQL, Markdown) - maks 20MB per file
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                File Dataset
              </label>
              <input
                type="file"
                accept=".csv,.xlsx,.xls,.json,.txt"
                multiple
                onChange={handleFileChange('dataset')}
                className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
              />
              <p className="mt-1 text-sm text-gray-500">
                Opsional: File dataset (CSV, Excel, JSON, TXT) - maks 15MB per file
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Slide Presentasi
              </label>
              <input
                type="file"
                accept=".pptx,.ppt"
                multiple
                onChange={handleFileChange('slides')}
                className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
              />
              <p className="mt-1 text-sm text-gray-500">
                Opsional: File PowerPoint - maks 10MB per file
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                File Tambahan
              </label>
              <input
                type="file"
                accept=".pdf,.docx,.doc,.txt,.csv,.xlsx,.xls,.zip,.rar,.tar.gz,.py,.ipynb,.r,.sql,.md,.pptx,.ppt"
                multiple
                onChange={handleFileChange('additional')}
                className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
              />
              <p className="mt-1 text-sm text-gray-500">
                Opsional: File tambahan (dokumen, gambar, arsip, dll.) - maks 20MB per file
              </p>
            </div>

            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => navigate('/dashboard')}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Batal
              </button>
              <button
                type="submit"
                disabled={status.loading || status.success}
                className="px-4 py-2 bg-indigo-600 text-white rounded-md text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {status.loading ? 'Mengunggah...' : 'Unggah Proyek'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;