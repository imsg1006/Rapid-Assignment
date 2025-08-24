import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, Image, BarChart3, Plus, Trash2, Calendar, ExternalLink } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

function Dashboard() {
  const [data, setData] = useState({ searches: [], images: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const { user } = useAuth();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await api.get('/dashboard/');
      setData(response.data);
    } catch (err) {
      setError('Failed to fetch dashboard data');
      console.error('Dashboard fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const deleteSearchEntry = async (entryId) => {
    try {
      await api.delete(`/dashboard/search/${entryId}`);
      setData(prev => ({
        ...prev,
        searches: prev.searches.filter(search => search.id !== entryId)
      }));
    } catch (err) {
      console.error('Delete error:', err);
      console.error('Delete error details:', err.response?.data);
      alert('Failed to delete entry');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#b73939] via-[#976f3e] to-[#7d8f35] flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-[#b73939]"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#b73939] via-[#976f3e] to-[#7d8f35] flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-400 text-xl mb-4">{error}</div>
          <button
            onClick={fetchDashboardData}
            className="bg-[#b73939] hover:bg-[#976f3e] text-white px-4 py-2 rounded-lg"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#b73939] via-[#976f3e] to-[#7d8f35]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">
            Welcome back, {user?.username}!
          </h1>
          <p className="text-gray-200">
            Here's what's happening with your AI content exploration
          </p>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <Link to="/search" className="group">
            <div className="bg-black/20 backdrop-blur-sm border border-white/10 rounded-2xl p-6 hover:bg-black/30 transition-all duration-300 hover:border-[#b73939]/40 hover:shadow-lg hover:shadow-[#b73939]/20">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Web Search</h3>
                  <p className="text-gray-300">Search the web and save results</p>
                </div>
                <div className="p-3 bg-[#b73939]/20 rounded-lg group-hover:bg-[#b73939]/30 transition-colors duration-200">
                  <Search className="w-6 h-6 text-[#b73939]" />
                </div>
              </div>
            </div>
          </Link>

          <Link to="/image-gen" className="group">
            <div className="bg-black/20 backdrop-blur-sm border border-white/10 rounded-2xl p-6 hover:bg-black/30 transition-all duration-300 hover:border-[#7d8f35]/40 hover:shadow-lg hover:shadow-[#7d8f35]/20">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Image Generation</h3>
                  <p className="text-gray-300">Generate images from text prompts</p>
                </div>
                <div className="p-3 bg-[#7d8f35]/20 rounded-lg group-hover:bg-[#7d8f35]/30 transition-colors duration-200">
                  <Image className="w-6 h-6 text-[#7d8f35]" />
                </div>
              </div>
            </div>
          </Link>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-black/20 backdrop-blur-sm border border-white/10 rounded-2xl p-6">
            <div className="flex items-center">
              <div className="p-3 bg-[#b73939]/20 rounded-lg">
                <Search className="w-6 h-6 text-[#b73939]" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-300">Total Searches</p>
                <p className="text-2xl font-bold text-white">{data.searches?.length || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-black/20 backdrop-blur-sm border border-white/10 rounded-2xl p-6">
            <div className="flex items-center">
              <div className="p-3 bg-[#976f3e]/20 rounded-lg">
                <Image className="w-6 h-6 text-[#976f3e]" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-300">Images Generated</p>
                <p className="text-2xl font-bold text-white">{data.images?.length || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-black/20 backdrop-blur-sm border border-white/10 rounded-2xl p-6">
            <div className="flex items-center">
              <div className="p-3 bg-[#7d8f35]/20 rounded-lg">
                <BarChart3 className="w-6 h-6 text-[#7d8f35]" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-300">Total Activity</p>
                <p className="text-2xl font-bold text-white">{(data.searches?.length || 0) + (data.images?.length || 0)}</p>
              </div>
            </div>
          </div>
        </div>

        {/* The rest (Recent Searches & Images) remains same, only accent colors adjusted */}
        <div className="bg-gradient-to-r from-[#b73939] via-[#976f3e] to-[#7d8f35] backdrop-blur-sm border border-white/10 rounded-2xl p-6 mb-8">
  <div className="flex items-center justify-between mb-6">
    <h2 className="text-xl font-semibold text-white">Recent Searches</h2>
    <Link
      to="/search"
      className="inline-flex items-center gap-2 text-purple-200 hover:text-purple-100 transition-colors duration-200"
    >
      <Plus className="w-4 h-4" />
      New Search
    </Link>
  </div>

  {data.searches && data.searches.length > 0 ? (
    <div className="space-y-4">
      {data.searches.slice(0, 5).map((search) => (
        <div
          key={search.id}
          className="flex items-center justify-between p-4 bg-black/30 rounded-lg border border-white/10"
        >
          <div className="flex-1">
            <h3 className="text-white font-medium mb-1">{search.query}</h3>
            <div className="flex items-center gap-4 text-sm text-gray-200">
              <span className="flex items-center gap-1">
                <Calendar className="w-4 h-4" />
                {new Date(search.timestamp).toLocaleDateString()}
              </span>
              <span>{search.results?.length || 0} results</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Link
              to={`/search?query=${encodeURIComponent(search.query)}`}
              className="p-2 text-blue-200 hover:text-blue-100 transition-colors duration-200"
            >
              <ExternalLink className="w-4 h-4" />
            </Link>
            <button
              onClick={() => deleteSearchEntry(search.id)}
              className="p-2 text-red-300 hover:text-red-200 transition-colors duration-200"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      ))}
    </div>
  ) : (
    <div className="text-center py-8">
      <Search className="w-16 h-16 text-gray-200 mx-auto mb-4" />
      <p className="text-gray-200 mb-2">No web searches yet</p>
      <Link
        to="/search"
        className="inline-flex items-center gap-2 mt-2 text-purple-200 hover:text-purple-100 transition-colors duration-200"
      >
        Start your first search
        <Plus className="w-4 h-4" />
      </Link>
    </div>
  )}
</div>

{/* Recent Images */}
<div className="bg-gradient-to-r from-[#b73939] via-[#976f3e] to-[#7d8f35] backdrop-blur-sm border border-white/10 rounded-2xl p-6">
  <div className="flex items-center justify-between mb-6">
    <h2 className="text-xl font-semibold text-white">Recent Images</h2>
    <Link
      to="/image-gen"
      className="inline-flex items-center gap-2 text-blue-200 hover:text-blue-100 transition-colors duration-200"
    >
      <Plus className="w-4 h-4" />
      Generate New Image
    </Link>
  </div>

  {data.images && data.images.length > 0 ? (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {data.images.slice(0, 6).map((image) => (
        <div
          key={image.id}
          className="bg-black/30 rounded-lg border border-white/10 overflow-hidden"
        >
          <img
            src={image.image_url}
            alt={image.prompt}
            className="w-full h-32 object-cover"
            onError={(e) => {
              e.target.src =
                "https://via.placeholder.com/300x200?text=Image+Not+Available";
            }}
          />
          <div className="p-4">
            <p className="text-white text-sm mb-2 line-clamp-2">{image.prompt}</p>
            <div className="flex items-center justify-between text-xs text-gray-200">
              <span className="flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                {new Date(image.timestamp).toLocaleDateString()}
              </span>
              <Link
                to={`/image-gen?prompt=${encodeURIComponent(image.prompt)}`}
                className="text-blue-200 hover:text-blue-100 transition-colors duration-200"
              >
                Regenerate
              </Link>
            </div>
          </div>
        </div>
      ))}
    </div>
  ) : (
    <div className="text-center py-8">
      <Image className="w-16 h-16 text-gray-200 mx-auto mb-4" />
      <p className="text-gray-200 mb-2">No images generated yet</p>
      <Link
        to="/image-gen"
        className="inline-flex items-center gap-2 mt-2 text-blue-200 hover:text-blue-100 transition-colors duration-200"
      >
        Generate your first image
        <Plus className="w-4 h-4" />
      </Link>
    </div>
  )}
</div>

        </div>
    </div>
  );
}

export default Dashboard;
