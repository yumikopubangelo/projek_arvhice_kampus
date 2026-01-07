import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useProjects } from '../hooks/useProjects';
import ProjectCard from '../components/ProjectCard';
import ProjectEditModal from '../components/ProjectEditModal';

const DashboardPage = () => {
  const { user } = useAuth();
  const { getProjects, getMyProjects } = useProjects();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editingProject, setEditingProject] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      console.log('📥 Fetching projects...');

      setLoading(true);
      setError('');

      let result;
      if (user?.role === 'student') {
        // Students see their own projects
        result = await getMyProjects();
      } else {
        // Others see all projects
        result = await getProjects();
      }

      if (result.success) {
        console.log('✅ Projects loaded:', result.data);
        setProjects(result.data);
      } else {
        setError(result.error);
      }
    } catch (err) {
      console.error('❌ Failed to load projects:', err);
      setError('Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  const handleProjectClick = (project) => {
    // Only allow editing if user is the owner and is a student
    if (user?.role === 'student' && user?.id === project.uploaded_by) {
      setEditingProject(project);
      setShowEditModal(true);
    } else {
      // For others, navigate to project detail
      window.location.href = `/projects/${project.id}`;
    }
  };

  const handleProjectUpdate = (updatedProject) => {
    setProjects(projects.map(p => p.id === updatedProject.id ? updatedProject : p));
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading projects...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button 
            onClick={fetchProjects}
            className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {/* Header */}
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

        {/* Projects Grid */}
        {projects.length === 0 ? (
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
              />
            ))}
          </div>
        )}

        {/* Edit Modal */}
        <ProjectEditModal
          project={editingProject}
          isOpen={showEditModal}
          onClose={() => setShowEditModal(false)}
          onUpdate={handleProjectUpdate}
        />
      </div>
    </div>
  );
};

export default DashboardPage;