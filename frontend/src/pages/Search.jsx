import React, { useState, useEffect } from 'react';
import { Search as SearchIcon, ExternalLink, Calendar, Trash2, Plus, TrendingUp, Globe, Clock, Sparkles } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

function Search() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchHistory, setSearchHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(true);

  const { user } = useAuth();

  // Load search history from backend on component mount
  useEffect(() => {
    fetchSearchHistory();
  }, [user?.id]);

  const fetchSearchHistory = async () => {
    try {
      setLoadingHistory(true);
      const response = await api.get('/dashboard/');
      if (response.data.searches) {
        setSearchHistory(response.data.searches);
      }
    } catch (err) {
      console.error('Failed to fetch search history:', err);
      // Fallback to localStorage if backend fails
      const savedHistory = localStorage.getItem(`searchHistory_${user?.id || 'anonymous'}`);
      if (savedHistory) {
        try {
          setSearchHistory(JSON.parse(savedHistory));
        } catch (parseErr) {
          console.error('Failed to parse saved search history:', parseErr);
          setSearchHistory([]);
        }
      }
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError('');
    setResults(null);

    try {
      const response = await api.get(`/search/?query=${encodeURIComponent(query.trim())}`);
      setResults(response.data);
      
      // Refresh search history from backend after new search
      await fetchSearchHistory();
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to perform search');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = async () => {
    try {
      // Clear from backend (delete all search entries)
      const response = await api.get('/dashboard/');
      if (response.data.searches) {
        for (const search of response.data.searches) {
          try {
            await api.delete(`/dashboard/search/${search.id}`);
          } catch (err) {
            console.error(`Failed to delete search ${search.id}:`, err);
          }
        }
      }
      setSearchHistory([]);
    } catch (err) {
      console.error('Failed to clear search history:', err);
      // Fallback to just clearing local state
      setSearchHistory([]);
    }
  };

  const removeFromHistory = async (id) => {
    try {
      await api.delete(`/dashboard/search/${id}`);
      setSearchHistory(prev => prev.filter(item => item.id !== id));
    } catch (err) {
      console.error('Failed to delete search entry:', err);
      // Fallback to just removing from local state
      setSearchHistory(prev => prev.filter(item => item.id !== id));
    }
  };

  const repeatSearch = (query) => {
    setQuery(query);
    // Optionally auto-submit the search
    // handleSubmit(new Event('submit'));
  };

  const formatUrl = (url) => {
    try {
      const urlObj = new URL(url);
      return urlObj.hostname;
    } catch {
      return url;
    }
  };

  const parseSearchResults = (resultsJson) => {
    try {
      if (typeof resultsJson === 'string') {
        return JSON.parse(resultsJson);
      }
      return resultsJson || [];
    } catch (err) {
      console.error('Failed to parse search results:', err);
      return [];
    }
  };

  return (
  <div className="min-h-screen bg-gradient-to-br from-[#b73939] via-[#976f3e] to-[#7d8f35]">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="flex items-center justify-center space-x-2 mb-4">
          <div className="w-10 h-10 bg-gradient-to-r from-[#b73939] via-[#976f3e] to-[#7d8f35] rounded-lg flex items-center justify-center">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <span className="text-2xl font-bold text-white">AI Explorer</span>
        </div>
        <h1 className="text-3xl font-bold text-white mb-2">
          Web Search
        </h1>
        <p className="text-lg text-gray-300">
          Discover information from across the web with AI-powered search
        </p>
      </div>

      {/* Search Form */}
      <div className="max-w-2xl mx-auto mb-8">
        <form onSubmit={handleSubmit} className="flex items-center gap-4">
          <div className="flex-1 relative">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your search query..."
              className="w-full px-4 py-3 bg-gray-800/50 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#976f3e] focus:border-transparent transition-all duration-200"
              disabled={loading}
            />
          </div>
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className={`px-6 py-3 rounded-lg font-semibold bg-transparent text-white transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#976f3e] disabled:opacity-50 disabled:cursor-not-allowed ${
              loading || !query.trim()
                ? 'bg-gray-600 cursor-not-allowed'
                : ' '
            }`}
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Searching...
              </>
            ) : (
               <button className="flex items-center px-4 py-2 rounded-lg bg-[#f79627] text-white">      
                <SearchIcon className="w-5 h-5 mr-2" />
                Search
              </button>
            )}
          </button>
        </form>
      </div>

      {/* Results */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2">
          {results && (
            <div className="bg-black/20 backdrop-blur-sm border border-white/10 rounded-2xl p-6">
              <div className="mb-6">
                <h2 className="text-xl font-semibold text-white mb-2">
                  Search Results for: "{results.query}"
                </h2>
                <p className="text-gray-400">
                  Found {results.results?.length || 0} results
                </p>
              </div>
              
              <div className="divide-y divide-white/10">
                {results.results.map((result, index) => (
                  <div key={index} className="p-6 hover:bg-gray-800/30 transition-colors duration-200">
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-[#976f3e]/20 rounded-lg flex items-center justify-center">
                          <Globe className="w-4 h-4 text-[#976f3e]" />
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="text-lg font-medium text-white mb-2">
                          <a
                            href={result.href}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="hover:text-[#b73939] transition-colors duration-200"
                          >
                            {result.title}
                          </a>
                        </h3>
                        <p className="text-gray-300 mb-3 leading-relaxed">
                          {result.body}
                        </p>
                        <div className="flex items-center gap-4 text-sm text-gray-400">
                          <span className="flex items-center gap-1">
                            <ExternalLink className="w-3 h-3" />
                            {formatUrl(result.href)}
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            Just now
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Search History Sidebar */}
        <div className="space-y-6">
          {/* Search Tips */}
          <div className="bg-black/20 backdrop-blur-sm border border-white/10 rounded-2xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-[#7d8f35]" />
              Search Tips
            </h3>
            <ul className="space-y-2 text-sm text-gray-300">
              <li>• Use specific keywords for better results</li>
              <li>• Try different search terms if results aren't relevant</li>
              <li>• Use quotes for exact phrase matching</li>
              <li>• Add site:domain.com to search specific websites</li>
            </ul>
          </div>

          {/* Recent Searches */}
          <div className="bg-black/20 backdrop-blur-sm border border-white/10 rounded-2xl">
            <div className="p-6 border-b border-white/10 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white">Recent Searches</h3>
              {searchHistory.length > 0 && (
                <button
                  onClick={clearHistory}
                  className="text-sm text-red-400 hover:text-red-300 transition-colors duration-200"
                >
                  Clear All
                </button>
              )}
            </div>
            
            <div className="divide-y divide-white/10">
              {loadingHistory ? (
                <div className="p-6 text-center text-gray-400">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-[#976f3e] mx-auto mb-4"></div>
                  <p>Loading search history...</p>
                </div>
              ) : searchHistory.length === 0 ? (
                <div className="p-6 text-center text-gray-400">
                  <SearchIcon className="w-12 h-12 mx-auto text-gray-500 mb-4" />
                  <p>No recent searches</p>
                  <p className="text-sm">Your search history will appear here</p>
                </div>
              ) : (
                searchHistory.map((item) => {
                  const parsedResults = parseSearchResults(item.results);
                  return (
                    <div key={item.id} className="p-4 hover:bg-gray-800/30 transition-colors duration-200">
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <button
                            onClick={() => repeatSearch(item.query)}
                            className="text-sm font-medium text-white hover:text-[#7d8f35] transition-colors duration-200 text-left w-full"
                          >
                            {item.query}
                          </button>
                          <p className="text-xs text-gray-400 flex items-center gap-1 mt-1">
                            <Calendar className="w-3 h-3" />
                            {new Date(item.timestamp).toLocaleDateString()}
                          </p>
                          <p className="text-xs text-gray-400 mt-1">
                            {parsedResults.length} results
                          </p>
                        </div>
                        <button
                          onClick={() => removeFromHistory(item.id)}
                          className="ml-2 p-1 text-red-400 hover:text-red-300 transition-colors duration-200"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      </div>
      </div>
    </div>
  );

}

export default Search;