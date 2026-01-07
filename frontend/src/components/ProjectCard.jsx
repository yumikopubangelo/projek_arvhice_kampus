import React from 'react';
import { useNavigate } from 'react-router-dom';

const ProjectCard = ({ project, onClick }) => {
  const navigate = useNavigate();

  const handleClick = () => {
    if (onClick) {
      onClick(project);
    } else {
      navigate(`/projects/${project.id}`);
    }
  };

  return (
    <div
      className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer"
      onClick={handleClick}
    >
      <h3 className="text-xl font-semibold text-gray-900 mb-2">
        {project.title}
      </h3>
      <p className="text-gray-600 mb-4 line-clamp-3">
        {project.abstract_preview || project.abstract}
      </p>
      <div className="flex justify-between items-center text-sm text-gray-500 mb-2">
        <span>By: {project.uploader?.full_name || project.uploaded_by_name || project.uploaded_by}</span>
        <span>{project.year}</span>
      </div>
      <div className="flex justify-between items-center mb-4">
        <span className={`px-2 py-1 text-xs rounded-full ${
          project.status === 'completed' ? 'bg-green-100 text-green-800' :
          project.status === 'ongoing' ? 'bg-yellow-100 text-yellow-800' :
          'bg-gray-100 text-gray-800'
        }`}>
          {project.status}
        </span>
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
    </div>
  );
};

export default ProjectCard;