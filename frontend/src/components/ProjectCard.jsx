import React from 'react';

const ProjectCard = ({ project }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <h3 className="text-xl font-semibold text-gray-900 mb-2">
        {project.title}
      </h3>
      <p className="text-gray-600 mb-4 line-clamp-3">
        {project.description}
      </p>
      <div className="flex justify-between items-center text-sm text-gray-500">
        <span>By: {project.uploaded_by_name || project.uploaded_by}</span>
        <span>{project.year}</span>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
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