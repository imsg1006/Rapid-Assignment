import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, Image, BarChart3, Trash2, Calendar, ExternalLink, Edit2, Check, X } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

function Dashboard() {
  const [data, setData] = useState({ searches: [], images: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState("all");
  const [sortOrder, setSortOrder] = useState("newest"); // newest | oldest

  const [editingSearchId, setEditingSearchId] = useState(null);
  const [editingImageId, setEditingImageId] = useState(null);
  const [editValue, setEditValue] = useState("");

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
      alert('Failed to delete entry');
    }
  };

  const deleteImageEntry = async (entryId) => {
    try {
      await api.delete(`/dashboard/image/${entryId}`);
      setData(prev => ({
        ...prev,
        images: prev.images.filter(image => image.id !== entryId)
      }));
    } catch (err) {
      console.error('Delete error:', err);
      alert('Failed to delete image');
    }
  };

  const startEditing = (type, id, currentValue) => {
    if (type === "search") {
      setEditingSearchId(id);
    } else {
      setEditingImageId(id);
    }
    setEditValue(currentValue);
  };

  const cancelEditing = () => {
    setEditingSearchId(null);
    setEditingImageId(null);
    setEditValue("");
  };

  const saveEdit = async (type, id) => {
    try {
      if (type === "search") {
        await api.patch(`/dashboard/search/${id}`, { query: editValue });
        setData(prev => ({
          ...prev,
          searches: prev.searches.map(s =>
            s.id === id ? { ...s, query: editValue } : s
          )
        }));
        setEditingSearchId(null);
      } else {
        await api.patch(`/dashboard/image/${id}`, { prompt: editValue });
        setData(prev => ({
          ...prev,
          images: prev.images.map(img =>
            img.id === id ? { ...img, prompt: editValue } : img
          )
        }));
        setEditingImageId(null);
      }
      setEditValue("");
    } catch (err) {
      console.error("Edit error:", err);
      alert("Failed to update entry");
    }
  };

  const sortByDate = (arr) => {
    return [...arr].sort((a, b) => {
      const dateA = new Date(a.timestamp);
      const dateB = new Date(b.timestamp);
      return sortOrder === "newest" ? dateB - dateA : dateA - dateB;
    });
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
            Welcome back!
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

        {/* Recent Results with Tabs & Sort */}
        <div className="bg-black/30 backdrop-blur-sm border border-white/10 rounded-2xl p-6 mb-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
            <h2 className="text-xl font-semibold text-white">Recent Results</h2>

            <div className="flex flex-wrap gap-2">
              {["all", "search", "image"].map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200 ${
                    activeTab === tab
                      ? tab === "all"
                        ? "bg-[#976f3e] text-white"
                        : tab === "search"
                        ? "bg-[#b73939] text-white"
                        : "bg-[#7d8f35] text-white"
                      : "bg-black/40 text-gray-300 hover:bg-black/60"
                  }`}
                >
                  {tab === "all" ? "All" : tab === "search" ? "Web Search" : "Image Gen"}
                </button>
              ))}

              {/* Sort Dropdown */}
              <select
                value={sortOrder}
                onChange={(e) => setSortOrder(e.target.value)}
                className="px-3 py-2 rounded-lg bg-black/40 text-gray-200 text-sm border border-white/10"
              >
                <option value="newest">Latest</option>
                <option value="oldest">Oldest</option>
              </select>
            </div>
          </div>

          {/* Content */}
          <div className="space-y-8">
            {(activeTab === "all" || activeTab === "search") && (
              <div>
                <h3 className="text-lg font-semibold text-white mb-4">Recent Searches</h3>
                {data.searches && data.searches.length > 0 ? (
                  <div className="space-y-4">
                    {sortByDate(data.searches).slice(0, 5).map((search) => (
                      <div
                        key={search.id}
                        className="flex items-center justify-between p-4 bg-black/30 rounded-lg border border-white/10"
                      >
                        <div className="flex-1">
                          {editingSearchId === search.id ? (
                            <input
                              type="text"
                              value={editValue}
                              onChange={(e) => setEditValue(e.target.value)}
                              className="w-full p-2 rounded bg-black/50 text-white border border-white/20"
                            />
                          ) : (
                            <h3 className="text-white font-medium mb-1">{search.query}</h3>
                          )}
                          <div className="flex items-center gap-4 text-sm text-gray-200">
                            <span className="flex items-center gap-1">
                              <Calendar className="w-4 h-4" />
                              {new Date(search.timestamp).toLocaleDateString()}
                            </span>
                            <span>{search.results?.length || 0} results</span>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {editingSearchId === search.id ? (
                            <>
                              <button
                                onClick={() => saveEdit("search", search.id)}
                                className="p-2 text-green-300 hover:text-green-200"
                              >
                                <Check className="w-4 h-4" />
                              </button>
                              <button
                                onClick={cancelEditing}
                                className="p-2 text-gray-300 hover:text-gray-200"
                              >
                                <X className="w-4 h-4" />
                              </button>
                            </>
                          ) : (
                            <>
                              <Link
                                to={`/search?query=${encodeURIComponent(search.query)}`}
                                className="p-2 text-blue-200 hover:text-blue-100 transition-colors duration-200"
                              >
                                <ExternalLink className="w-4 h-4" />
                              </Link>
                              <button
                                onClick={() => startEditing("search", search.id, search.query)}
                                className="p-2 text-yellow-300 hover:text-yellow-200"
                              >
                                <Edit2 className="w-4 h-4" />
                              </button>
                              <button
                                onClick={() => deleteSearchEntry(search.id)}
                                className="p-2 text-red-300 hover:text-red-200 transition-colors duration-200"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-300">No web searches yet</p>
                )}
              </div>
            )}

            {(activeTab === "all" || activeTab === "image") && (
              <div>
                <h3 className="text-lg font-semibold text-white mb-4">Recent Images</h3>
                {data.images && data.images.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {sortByDate(data.images).slice(0, 6).map((image) => (
                      <div
                        key={image.id}
                        className="bg-black/30 rounded-lg border border-white/10 overflow-hidden flex flex-col"
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
                        <div className="p-4 flex-1 flex flex-col justify-between">
                          <div>
                            {editingImageId === image.id ? (
                              <input
                                type="text"
                                value={editValue}
                                onChange={(e) => setEditValue(e.target.value)}
                                className="w-full p-2 rounded bg-black/50 text-white border border-white/20 text-sm"
                              />
                            ) : (
                              <p className="text-white text-sm mb-2 line-clamp-2">{image.prompt}</p>
                            )}
                            <div className="flex items-center justify-between text-xs text-gray-200">
                              <span className="flex items-center gap-1">
                                <Calendar className="w-3 h-3" />
                                {new Date(image.timestamp).toLocaleDateString()}
                              </span>
                            </div>
                          </div>
                          <div className="flex items-center justify-between mt-2">
                            {editingImageId === image.id ? (
                              <div className="flex gap-2">
                                <button
                                  onClick={() => saveEdit("image", image.id)}
                                  className="p-2 text-green-300 hover:text-green-200"
                                >
                                  <Check className="w-4 h-4" />
                                </button>
                                <button
                                  onClick={cancelEditing}
                                  className="p-2 text-gray-300 hover:text-gray-200"
                                >
                                  <X className="w-4 h-4" />
                                </button>
                              </div>
                            ) : (
                              <>
                                <Link
                                  to={`/image-gen?prompt=${encodeURIComponent(image.prompt)}`}
                                  className="text-blue-200 hover:text-blue-100 text-xs transition-colors duration-200"
                                >
                                  Regenerate
                                </Link>
                                <div className="flex gap-2">
                                  <button
                                    onClick={() => startEditing("image", image.id, image.prompt)}
                                    className="p-2 text-yellow-300 hover:text-yellow-200"
                                  >
                                    <Edit2 className="w-4 h-4" />
                                  </button>
                                  <button
                                    onClick={() => deleteImageEntry(image.id)}
                                    className="p-2 text-red-300 hover:text-red-200 transition-colors duration-200"
                                  >
                                    <Trash2 className="w-4 h-4" />
                                  </button>
                                </div>
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-300">No images generated yet</p>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
