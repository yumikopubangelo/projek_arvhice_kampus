import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '../api/client';
import ProjectCard from '../components/ProjectCard';

const SearchPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [filters, setFilters] = useState({
    query: searchParams.get('query') || '',
    year: searchParams.get('year') || '',
    tag: searchParams.get('tag') || '',
    privacy_level: searchParams.get('privacy_level') || '',
  });

  const searchProjects = async () => {
    setLoading(true);
    setError('');

    try {
      const params = new URLSearchParams();
      if (filters.query) params.append('query', filters.query);
      if (filters.year) params.append('year', filters.year);
      if (filters.tag) params.append('tag', filters.tag);
      if (filters.privacy_level) params.append('privacy_level', filters.privacy_level);

      const response = await api.get(`/search?${params.toString()}`);
      setProjects(response.data);
    } catch (err) {
      setError('Failed to search projects');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSearch = (e) => {
    e.preventDefault();
    // Update URL params
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.append(key, value);
    });
    setSearchParams(params);
    searchProjects();
  };

  useEffect(() => {
    searchProjects();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Search Projects</h1>

          {/* Search Form */}
          <form onSubmit={handleSearch} className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-1">
                  Search Query
                </label>
                <input
                  type="text"
                  id="query"
                  name="query"
                  value={filters.query}
                  onChange={handleFilterChange}
                  placeholder="Title, abstract, authors..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div>
                <label htmlFor="year" className="block text-sm font-medium text-gray-700 mb-1">
                  Year
                </label>
                <input
                  type="number"
                  id="year"
                  name="year"
                  value={filters.year}
                  onChange={handleFilterChange}
                  placeholder="2024"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div>
                <label htmlFor="tag" className="block text-sm font-medium text-gray-700 mb-1">
                  Tag
                </label>
                <input
                  type="text"
                  id="tag"
                  name="tag"
                  value={filters.tag}
                  onChange={handleFilterChange}
                  placeholder="Machine Learning"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div>
                <label htmlFor="privacy_level" className="block text-sm font-medium text-gray-700 mb-1">
                  Privacy Level
                </label>
                <select
                  id="privacy_level"
                  name="privacy_level"
                  value={filters.privacy_level}
                  onChange={handleFilterChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="">All</option>
                  <option value="public">Public</option>
                  <option value="advisor">Advisor</option>
                  <option value="class">Class</option>
                  <option value="private">Private</option>
                </select>
              </div>
            </div>

            <div className="mt-4">
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50"
              >
                {loading ? 'Searching...' : 'Search'}
              </button>
            </div>
          </form>
        </div>

        {/* Results */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-600">{error}</p>
          </div>
        )}

        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-900">
            {loading ? 'Searching...' : `Found ${projects.length} projects`}
          </h2>
        </div>

        {projects.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </div>
        ) : (
          !loading && (
            <div className="text-center py-12">
              <p className="text-gray-500">No projects found matching your criteria.</p>
            </div>
          )
        )}
      </div>
    </div>
  );
};

export default SearchPage;