import { useState } from 'react';
import api from '../api/client';

const useProjects = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const getProjects = async (params = {}) => {
    setLoading(true);
    try {
      const response = await api.get('/projects', { params });
      return { success: true, data: response.data };
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to fetch projects';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const getProject = async (projectId) => {
    setLoading(true);
    try {
      const response = await api.get(`/projects/${projectId}`);
      return { success: true, data: response.data };
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to fetch project';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const createProject = async (projectData) => {
    setLoading(true);
    try {
      const response = await api.post('/projects', projectData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return { success: true, data: response.data };
    } catch (err) {
      let errorMessage = 'Failed to create project';
      if (err.response && err.response.data && err.response.data.detail) {
        if (Array.isArray(err.response.data.detail)) {
          errorMessage = err.response.data.detail.map(e => `${e.loc.join('.')} - ${e.msg}`).join('; ');
        } else if (typeof err.response.data.detail === 'object') {
          errorMessage = JSON.stringify(err.response.data.detail);
        } else {
          errorMessage = err.response.data.detail;
        }
      }
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const updateProject = async (projectId, projectData) => {
    setLoading(true);
    try {
      // Check if projectData is FormData (for file uploads)
      const isFormData = projectData instanceof FormData;
      const response = await api.post(`/projects/${projectId}`, projectData, {
        headers: isFormData ? { 'Content-Type': 'multipart/form-data' } : {}
      });
      return { success: true, data: response.data };
    } catch (err) {
      let errorMessage = 'Failed to update project.';
      if (err.response && err.response.data && err.response.data.detail) {
        if (Array.isArray(err.response.data.detail)) {
          errorMessage = err.response.data.detail.map(e => `${e.loc.join('.')} - ${e.msg}`).join('; ');
        } else if (typeof err.response.data.detail === 'object') {
          errorMessage = JSON.stringify(err.response.data.detail);
        } else {
          errorMessage = err.response.data.detail;
        }
      }
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const deleteProject = async (projectId) => {
    setLoading(true);
    try {
      await api.delete(`/projects/${projectId}`);
      return { success: true };
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to delete project';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const getMyProjects = async () => {
    setLoading(true);
    try {
      const response = await api.get('/projects/me/projects');
      return { success: true, data: response.data };
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to fetch your projects';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    error,
    getProjects,
    getProject,
    createProject,
    updateProject,
    deleteProject,
    getMyProjects
  };
};

export { useProjects };