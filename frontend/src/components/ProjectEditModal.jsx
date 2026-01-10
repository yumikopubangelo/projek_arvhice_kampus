import React, { useState, useEffect } from 'react';
import { useProjects } from '../hooks/useProjects';
import FileUpload from './FileUpload';

const ProjectEditModal = ({ project, isOpen, onClose, onUpdate }) => {
  const [formData, setFormData] = useState({
    title: '',
    abstract: '',
    authors: '',
    tags: '',
    year: new Date().getFullYear(),
    assignment_type: '',
    semester: '',
    class_name: '',
    course_code: '',
    status: 'ongoing',
    privacy_level: 'private',
    code_repo_url: '',
    dataset_url: '',
    video_url: '',
    lecturer_name: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [supplementaryFiles, setSupplementaryFiles] = useState([]);
  const [pdfFile, setPdfFile] = useState(null);
  const { updateProject } = useProjects();

  useEffect(() => {
    if (project) {
      setFormData({
        title: project.title || '',
        abstract: project.abstract || '',
        authors: project.authors ? project.authors.join(', ') : '',
        tags: project.tags ? project.tags.join(', ') : '',
        year: project.year || new Date().getFullYear(),
        assignment_type: project.assignment_type || '',
        semester: project.semester || '',
        class_name: project.class_name || '',
        course_code: project.course_code || '',
        status: project.status || 'ongoing',
        privacy_level: project.privacy_level || 'private',
        code_repo_url: project.code_repo_url || '',
        dataset_url: project.dataset_url || '',
        video_url: project.video_url || '',
        lecturer_name: project.lecturer_name || ''
      });

      // Initialize supplementary files with size information
      const existingFiles = (project.supplementary_files_info || []).map(fileInfo => ({
        name: fileInfo.name,
        path: fileInfo.path,
        size: fileInfo.size,
        type: '',
        uploaded: true
      }));
      setSupplementaryFiles(existingFiles);
    }
  }, [project]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const formDataToSend = new FormData();

      // Append all text-based form fields
      Object.keys(formData).forEach(key => {
        // Ensure not to send null/undefined, but allow empty strings
        if (formData[key] !== null && formData[key] !== undefined) {
            formDataToSend.append(key, formData[key]);
        }
      });
      
      // Append the new PDF file if one was selected
      if (pdfFile) {
        formDataToSend.append('pdf_file', pdfFile);
      }

      // Filter out already existing files and append only new ones
      const newSupplementaryFiles = supplementaryFiles.filter(file => !file.uploaded);
      if (newSupplementaryFiles.length > 0) {
        newSupplementaryFiles.forEach(fileObject => {
          // The actual file is often stored in a 'file' property or is the object itself
          const file = fileObject.file || fileObject;
          formDataToSend.append('supplementary_files', file);
        });
      }

      // Call the update function from the hook
      const result = await updateProject(project.id, formDataToSend);

      if (result.success) {
        onUpdate(result.data); // Propagate update to parent component
        onClose(); // Close the modal
      } else {
        setError(result.error || 'An unknown error occurred.');
      }

    } catch (err) {
      console.error("Update project error:", err);
      setError(err.response?.data?.detail || err.message || 'Failed to update project.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Edit Proyek</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Judul
            </label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Abstrak
            </label>
            <textarea
              name="abstract"
              value={formData.abstract}
              onChange={handleChange}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Laporan PDF (Opsional - biarkan kosong untuk mempertahankan yang ada)
            </label>
            <input
              type="file"
              accept=".pdf"
              onChange={(e) => setPdfFile(e.target.files[0])}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
            <p className="mt-1 text-sm text-gray-500">
              Unggah laporan PDF baru (maks 10MB). File yang ada akan diganti.
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Penulis (dipisahkan koma)
            </label>
            <input
              type="text"
              name="authors"
              value={formData.authors}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tag (dipisahkan koma)
            </label>
            <input
              type="text"
              name="tags"
              value={formData.tags}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tahun
              </label>
              <input
                type="number"
                name="year"
                value={formData.year}
                onChange={handleChange}
                min="2000"
                max={new Date().getFullYear() + 1}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tipe Penugasan
              </label>
              <select
                name="assignment_type"
                value={formData.assignment_type}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Pilih tipe penugasan</option>
                <option value="skripsi">Tugas Akhir/Skripsi</option>
                <option value="tugas_matkul">Tugas Mata Kuliah</option>
                <option value="laporan_kp">Laporan Kerja Praktik</option>
                <option value="lainnya">Lainnya</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Semester
              </label>
              <input
                type="text"
                name="semester"
                value={formData.semester}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nama Kelas
              </label>
              <input
                type="text"
                name="class_name"
                value={formData.class_name}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Kode Mata Kuliah
              </label>
              <input
                type="text"
                name="course_code"
                value={formData.course_code}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nama Dosen
              </label>
              <input
                type="text"
                name="lecturer_name"
                value={formData.lecturer_name}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              name="status"
              value={formData.status}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="ongoing">Sedang Berlangsung</option>
              <option value="completed">Selesai</option>
              <option value="archived">Diarsipkan</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tingkat Privasi
            </label>
            <select
              name="privacy_level"
              value={formData.privacy_level}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="private">Privat</option>
              <option value="advisor">Pembimbing</option>
              <option value="class">Kelas</option>
              <option value="public">Publik</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              URL Repositori Kode
            </label>
            <input
              type="url"
              name="code_repo_url"
              value={formData.code_repo_url}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              URL Dataset
            </label>
            <input
              type="url"
              name="dataset_url"
              value={formData.dataset_url}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              URL Video
            </label>
            <input
              type="url"
              name="video_url"
              value={formData.video_url}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <FileUpload
            projectId={project?.id}
            existingFiles={supplementaryFiles}
            onFilesChange={setSupplementaryFiles}
          />

          {error && (
            <div className="text-red-600 text-sm">
              {typeof error === 'string' ? error : JSON.stringify(error)}
            </div>
          )}

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Batal
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Memperbarui...' : 'Perbarui Proyek'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProjectEditModal;