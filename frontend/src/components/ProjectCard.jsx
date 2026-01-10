import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client'; // Import the api client

const ProjectCard = ({ project, onClick, user, onDelete }) => {
  const navigate = useNavigate();
  const [files, setFiles] = useState(project.files || []);
  const [fileError, setFileError] = useState('');

  const handleClick = (e) => {
    // Prevent navigation if clicking on a button or link inside the card
    if (e.target.closest('button, a')) {
      return;
    }

    if (onClick) {
      onClick(project);
    } else {
      navigate(`/projects/${project.id}`);
    }
  };

  const handleDeleteProject = (e) => {
    e.stopPropagation();
    if (onDelete) {
      onDelete(project);
    }
  };

  const handleDeleteFile = async (e, fileId, fileName) => {
    e.stopPropagation(); // Prevent card click
    if (!window.confirm(`Are you sure you want to delete the file "${fileName}"?`)) {
      return;
    }

    setFileError(''); // Clear previous errors
    try {
      await api.delete(`/files/${fileId}`);
      // Update the state to remove the file from the list
      setFiles(files.filter(f => f.id !== fileId));
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to delete the file.';
      setFileError(errorMessage);
    }
  };

  const isOwner = user?.id === project.uploaded_by;

  return (
    <div
      className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer flex flex-col justify-between"
      onClick={handleClick}
    >
      <div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          {project.title}
        </h3>
        <p className="text-gray-600 mb-4 text-sm line-clamp-3">
          {project.abstract_preview || project.abstract}
        </p>
        <div className="flex justify-between items-center text-sm text-gray-500 mb-2">
          <span>By: {project.uploader?.full_name || '...'}</span>
          <span>{project.year}</span>
        </div>
        <div className="flex justify-between items-center mb-4">
          <div className="flex space-x-2">
            <span className={`px-2 py-1 text-xs rounded-full ${
              project.status === 'completed' ? 'bg-green-100 text-green-800' :
              project.status === 'ongoing' ? 'bg-yellow-100 text-yellow-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              {project.status}
            </span>
            <span className={`px-2 py-1 text-xs rounded-full ${
              project.privacy_level === 'public' ? 'bg-blue-100 text-blue-800' :
              project.privacy_level === 'advisor' ? 'bg-purple-100 text-purple-800' :
              project.privacy_level === 'class' ? 'bg-orange-100 text-orange-800' :
              'bg-red-100 text-red-800'
            }`}>
              {project.privacy_level}
            </span>
          </div>
          <span className="text-sm text-gray-500">
            Views: {project.view_count}
          </span>
        </div>
        <div className="flex flex-wrap gap-2">
          {project.tags && project.tags.map((tag, index) => (
            <span
              key={index}
              className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
            >
              {tag}
            </span>
          ))}
        </div>

        {/* Files List */}
        {files.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <h4 className="text-sm font-semibold text-gray-700 mb-2">Attached Files:</h4>
            {fileError && <p className="text-red-500 text-xs mb-2">{fileError}</p>}
            <ul className="space-y-2">
              {files.map((file) => (
                <li key={file.id} className="flex items-center justify-between group">
                  <a
                    href={`/api/files/${file.id}/download`}
                    download
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 hover:underline text-sm truncate pr-2"
                    onClick={(e) => e.stopPropagation()}
                  >
                    {file.original_filename}
                  </a>
                  {isOwner && (
                    <button
                      onClick={(e) => handleDeleteFile(e, file.id, file.original_filename)}
                      className="text-gray-400 hover:text-red-600 opacity-0 group-hover:opacity-100 transition-opacity"
                      title="Delete file"
                    >
                      ✕
                    </button>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Delete button for owners */}
      {isOwner && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <button
            onClick={handleDeleteProject}
            className="w-full px-3 py-2 bg-red-600 text-white text-sm rounded-md hover:bg-red-700 transition-colors"
          >
            Delete Project
          </button>
        </div>
      )}
    </div>
  );
};

export default ProjectCard;