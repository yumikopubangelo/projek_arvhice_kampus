import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useProjects } from '../hooks/useProjects';
import ProjectCard from '../components/ProjectCard';
import ProjectEditModal from '../components/ProjectEditModal';
import ConfirmationModal from '../components/ConfirmationModal'; // Import the modal

const DashboardPage = () => {
  const { user } = useAuth();
  const { getProjects, getMyProjects, deleteProject } = useProjects();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editingProject, setEditingProject] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  
  // State for delete confirmation
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deletingProject, setDeletingProject] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      setError('');
      const result = user?.role === 'student' ? await getMyProjects() : await getProjects();
      if (result.success) {
        setProjects(result.data);
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  const handleProjectClick = (project) => {
    if (user?.role === 'student' && user?.id === project.uploaded_by) {
      setEditingProject(project);
      setShowEditModal(true);
    } else {
      window.location.href = `/projects/${project.id}`;
    }
  };

  const handleProjectUpdate = (updatedProject) => {
    setProjects(projects.map(p => p.id === updatedProject.id ? updatedProject : p));
  };

  // Step 1: Open confirmation modal
  const handleProjectDelete = (project) => {
    setDeletingProject(project);
    setShowDeleteConfirm(true);
  };

  // Step 2: Confirm deletion and execute
  const confirmProjectDelete = async () => {
    if (!deletingProject) return;

    setIsDeleting(true);
    setError('');
    try {
      const result = await deleteProject(deletingProject.id);
      if (result.success) {
        setProjects(projects.filter(p => p.id !== deletingProject.id));
        setShowDeleteConfirm(false);
        setDeletingProject(null);
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('Failed to delete project');
    } finally {
      setIsDeleting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading projects...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-600 mt-1">Welcome, {user?.full_name || user?.email}</p>
          </div>
          
          {user?.role === 'student' && (
            <Link
              to="/upload"
              className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
            >
              Add Project
            </Link>
          )}
        </div>

        {error && <p className="text-red-600 mb-4">{error}</p>}
        
        {projects.length === 0 && !loading ? (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No projects found.</p>
            {user?.role === 'student' && (
              <Link
                to="/upload"
                className="mt-4 inline-block bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
              >
                Upload your first project
              </Link>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                onClick={handleProjectClick}
                user={user}
                onDelete={handleProjectDelete}
              />
            ))}
          </div>
        )}

        <ProjectEditModal
          project={editingProject}
          isOpen={showEditModal}
          onClose={() => setShowEditModal(false)}
          onUpdate={handleProjectUpdate}
        />

        <ConfirmationModal
          isOpen={showDeleteConfirm}
          onClose={() => setShowDeleteConfirm(false)}
          onConfirm={confirmProjectDelete}
          title="Confirm Project Deletion"
          message={`Are you sure you want to delete the project "${deletingProject?.title}"? This action cannot be undone.`}
          confirmText="Delete"
          loading={isDeleting}
        />
      </div>
    </div>
  );
};