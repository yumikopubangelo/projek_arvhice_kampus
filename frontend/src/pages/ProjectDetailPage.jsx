import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';

const ProjectDetailPage = () => {
  const { projectId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const hasFetched = useRef(false);

  useEffect(() => {
    if (!hasFetched.current) {
      hasFetched.current = true;
      fetchProject();
    }
  }, [projectId]);

  const fetchProject = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/projects/${projectId}`);
      setProject(response.data);
    } catch (err) {
      setError('Failed to load project');
      console.error('Project fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const canAccessFullContent = () => {
    if (!project || !user) return false;

    // Owner can always access
    if (project.uploaded_by === user.id) return true;

    // Public projects are fully accessible
    if (project.privacy_level === 'public') return true;

    // Dosen can only see metadata for private projects
    if (user.role === 'dosen' && project.privacy_level === 'private') return false;

    // Advisor access
    if (project.advisor_id === user.id) return true;

    return false;
  };

  const handleDownloadFile = async (file, e) => {
    e.preventDefault();
    try {
      const response = await api.get(`/files/${file.id}/download`, {
        responseType: 'blob',
      });

      // Create a blob URL and trigger download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', file.original_filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
      alert('Failed to download file. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Memuat proyek...</div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Proyek Tidak Ditemukan</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => navigate('/search')}
            className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
          >
            Kembali ke Pencarian
          </button>
        </div>
      </div>
    );
  }

  const hasFullAccess = canAccessFullContent();

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate(-1)}
            className="mb-4 px-4 py-2 text-indigo-600 hover:text-indigo-800 flex items-center"
          >
            ← Back
          </button>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">{project.title}</h1>
                <p className="text-lg text-gray-600 mb-2">
                  Oleh: {project.uploader?.full_name || project.uploaded_by}
                </p>
                {project.lecturer_name && (
                  <p className="text-md text-gray-600 mb-2">
                    Dosen: {project.lecturer_name}
                  </p>
                )}
                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  <span>Tahun: {project.year}</span>
                  {project.semester && <span>Semester: {project.semester}</span>}
                  <span>Dilihat: {project.view_count}</span>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <span className={`px-3 py-1 text-sm rounded-full ${
                  project.status === 'completed' ? 'bg-green-100 text-green-800' :
                  project.status === 'ongoing' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {project.status === 'ongoing' && 'Sedang Berlangsung'}
                  {project.status === 'completed' && 'Selesai'}
                  {project.status === 'archived' && 'Diarsipkan'}
                </span>
                <span className={`px-3 py-1 text-sm rounded-full ${
                  project.privacy_level === 'public' ? 'bg-green-100 text-green-800' :
                  project.privacy_level === 'advisor' ? 'bg-blue-100 text-blue-800' :
                  project.privacy_level === 'class' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {project.privacy_level === 'private' && 'Privat'}
                  {project.privacy_level === 'advisor' && 'Pembimbing'}
                  {project.privacy_level === 'class' && 'Kelas'}
                  {project.privacy_level === 'public' && 'Publik'}
                </span>
              </div>
            </div>

            {/* Tags */}
            {project.tags && project.tags.length > 0 && (
              <div className="mb-4">
                <div className="flex flex-wrap gap-2">
                  {project.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Abstract */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Abstrak</h2>
              <p className="text-gray-700 leading-relaxed">{project.abstract}</p>
            </div>

            {/* Authors */}
            {project.authors && project.authors.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Penulis</h2>
                <div className="flex flex-wrap gap-2">
                  {project.authors.map((author, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-gray-100 text-gray-800 rounded-md"
                    >
                      {author}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Academic Info */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Informasi Akademik</h2>
              <div className="grid grid-cols-2 gap-4">
                {project.assignment_type && (
                  <div>
                    <span className="font-medium text-gray-700">Tipe Penugasan:</span>
                    <p className="text-gray-600">
                      {project.assignment_type === 'skripsi' && 'Tugas Akhir/Skripsi'}
                      {project.assignment_type === 'tugas_matkul' && 'Tugas Mata Kuliah'}
                      {project.assignment_type === 'laporan_kp' && 'Laporan Kerja Praktik'}
                      {project.assignment_type === 'lainnya' && 'Lainnya'}
                    </p>
                  </div>
                )}
                {project.class_name && (
                  <div>
                    <span className="font-medium text-gray-700">Kelas:</span>
                    <p className="text-gray-600">{project.class_name}</p>
                  </div>
                )}
                {project.course_code && (
                  <div>
                    <span className="font-medium text-gray-700">Kode Mata Kuliah:</span>
                    <p className="text-gray-600">{project.course_code}</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Access Notice */}
            {user?.role === 'dosen' && project.privacy_level === 'private' && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <h3 className="text-sm font-medium text-yellow-800 mb-2">Akses Terbatas</h3>
                <p className="text-sm text-yellow-700">
                  Sebagai dosen, Anda dapat melihat metadata proyek dasar tetapi tidak dapat melihat konten lengkap proyek pribadi.
                </p>
              </div>
            )}

            {/* Full Content Access */}
            {hasFullAccess && (
              <>
                {/* Project Files */}
                {project.files && project.files.length > 0 && (
                  <div className="bg-white rounded-lg shadow-sm p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">File Proyek</h3>
                    <div className="space-y-2">
                      {project.files.map((file) => (
                        <button
                          key={file.id}
                          onClick={(e) => handleDownloadFile(file, e)}
                          className={`block w-full text-left px-3 py-2 text-gray-600 hover:text-gray-800 border border-gray-200 rounded-md hover:bg-gray-50 ${
                            file.file_type === 'main_report' ? 'bg-red-50 border-red-200' : ''
                          }`}
                        >
                          {file.file_type === 'main_report' ? '📄' : '📎'} {file.original_filename}
                          {file.file_size && ` (${(file.file_size / 1024 / 1024).toFixed(1)}MB)`}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Links */}
                {(project.code_repo_url || project.dataset_url || project.video_url) && (
                  <div className="bg-white rounded-lg shadow-sm p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Tautan</h3>
                    <div className="space-y-2">
                      {project.code_repo_url && (
                        <a
                          href={project.code_repo_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="block px-3 py-2 text-indigo-600 hover:text-indigo-800 border border-indigo-200 rounded-md hover:bg-indigo-50"
                        >
                          🔗 Repositori Kode
                        </a>
                      )}
                      {project.dataset_url && (
                        <a
                          href={project.dataset_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="block px-3 py-2 text-indigo-600 hover:text-indigo-800 border border-indigo-200 rounded-md hover:bg-indigo-50"
                        >
                          📊 Dataset
                        </a>
                      )}
                      {project.video_url && (
                        <a
                          href={project.video_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="block px-3 py-2 text-indigo-600 hover:text-indigo-800 border border-indigo-200 rounded-md hover:bg-indigo-50"
                        >
                          🎥 Video Demo
                        </a>
                      )}
                    </div>
                  </div>
                )}
              </>
            )}

            {/* Metadata */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Informasi Proyek</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Dibuat:</span>
                  <span className="text-gray-900">{new Date(project.created_at).toLocaleDateString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Terakhir Diperbarui:</span>
                  <span className="text-gray-900">{new Date(project.updated_at).toLocaleDateString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Unduhan:</span>
                  <span className="text-gray-900">{project.download_count}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProjectDetailPage;