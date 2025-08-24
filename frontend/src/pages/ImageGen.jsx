import React, { useState, useEffect } from 'react';
import { Image as ImageIcon, Send, Download, Copy, Sparkles, Palette, Lightbulb, Clock, Trash2, CheckCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

function ImageGen() {
  const [prompt, setPrompt] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);
  const [generationHistory, setGenerationHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(true);

  const { user } = useAuth();

  useEffect(() => {
    fetchGenerationHistory();
  }, [user?.id]);

  const fetchGenerationHistory = async () => {
    try {
      setLoadingHistory(true);
      const response = await api.get('/dashboard/');
      if (response.data.images) {
        setGenerationHistory(response.data.images);
      }
    } catch (err) {
      console.error('Failed to fetch generation history:', err);
      const savedHistory = localStorage.getItem(`generationHistory_${user?.id || 'anonymous'}`);
      if (savedHistory) {
        try {
          setGenerationHistory(JSON.parse(savedHistory));
        } catch (parseErr) {
          console.error('Failed to parse saved generation history:', parseErr);
          setGenerationHistory([]);
        }
      }
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await api.post('/images/generate', {
        prompt: prompt.trim()
      });
      setResult(response.data);
      await fetchGenerationHistory();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate image');
      console.error('Image generation error:', err);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const downloadImage = async (url, filename) => {
    try {
      const response = await fetch(url);
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename || 'generated-image.jpg';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (err) {
      console.error('Failed to download:', err);
    }
  };

  const clearHistory = async () => {
    try {
      setGenerationHistory([]);
    } catch (err) {
      console.error('Failed to clear generation history:', err);
      setGenerationHistory([]);
    }
  };

  const removeFromHistory = async (id) => {
    try {
      setGenerationHistory(prev => prev.filter(item => item.id !== id));
    } catch (err) {
      console.error('Failed to delete generation entry:', err);
      setGenerationHistory(prev => prev.filter(item => item.id !== id));
    }
  };

  const repeatGeneration = (prompt) => {
    setPrompt(prompt);
  };

  const samplePrompts = [
    "A futuristic cityscape with flying cars and neon lights",
    "A serene mountain landscape at sunset with golden clouds",
    "A cute robot playing with a cat in a garden",
    "An underwater palace with coral and sea creatures",
    "A steampunk airship flying over Victorian London"
  ];

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
            AI Image Generation
          </h1>
          <p className="text-lg text-gray-300">
            Transform your ideas into stunning visuals using advanced AI models
          </p>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Generation Form and Results */}
          <div className="lg:col-span-2 space-y-6">
            {/* Generation Form */}
            <div className="bg-black/20 backdrop-blur-sm border border-white/10 rounded-2xl p-6">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label htmlFor="prompt" className="block text-sm font-medium text-white mb-2">
                    Image Prompt
                  </label>
                  <textarea
                    id="prompt"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Describe the image you want to generate..."
                    rows={4}
                    className="w-full px-4 py-3 bg-gray-800/50 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#976f3e] focus:border-transparent transition-all duration-200 resize-none"
                    disabled={loading}
                  />
                </div>

                <div className="flex justify-between items-center">
                  <p className="text-sm text-gray-400">
                    Be descriptive for better results
                  </p>
                  <button
                    type="submit"
                    disabled={loading || !prompt.trim()}
                    className={`px-6 py-3 rounded-lg font-semibold text-white bg-transparent transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#976f3e] disabled:opacity-50 disabled:cursor-not-allowed ${
                      loading || !prompt.trim()
                        ? 'bg-gray-600 cursor-not-allowed'
                        : 'bg-gradient-to-r from-[#b73939] via-[#976f3e] to-[#7d8f35] hover:opacity-90 shadow-lg hover:shadow-[#976f3e]/30'
                    }`}
                  >
                    {loading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Generating...
                      </>
                    ) : (
                      <button className="flex items-center px-4 py-2 rounded-lg bg-[#f79627] text-white">
                       <Send className="w-5 h-5 mr-2" />
                        <span>Generate Image</span>
                      </button>

                    )}
                  </button>
                </div>
              </form>
            </div>

            {/* Error Display */}
            {error && (
              <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-3 rounded-lg">
                <p className="font-medium">Generation failed:</p>
                <p className="text-sm mt-1">{error}</p>
              </div>
            )}

            {/* Generated Image */}
            {result && (
              <div className="bg-black/20 backdrop-blur-sm border border-white/10 rounded-2xl p-6">
                <div className="mb-4">
                  <h2 className="text-xl font-semibold text-white mb-2">
                    Generated Image
                  </h2>
                  <p className="text-gray-400">
                    Prompt: "{result.message || result.prompt}"
                  </p>
                </div>
                
                <div className="space-y-4">
                  <div className="relative">
                    <img
                      src={result.image_url}
                      alt={result.message || result.prompt}
                      className="w-full h-96 object-contain bg-transparent rounded-lg border border-white/10"
                      onError={(e) => {
                        e.target.src = 'https://via.placeholder.com/600x400?text=Image+Not+Available';
                      }}
                    />
                  </div>
                  
                  <div className="flex flex-wrap gap-3">
                    <button
                      onClick={() => copyToClipboard(result.image_url)}
                      className="inline-flex items-center gap-2 px-4 py-2 bg-gray-800/50 border border-white/20 text-white rounded-lg hover:bg-gray-700/50 transition-colors duration-200"
                    >
                      {copied ? (
                        <>
                          <CheckCircle className="w-4 h-4 text-green-400" />
                          Copied!
                        </>
                      ) : (
                        <>
                          <Copy className="w-4 h-4" />
                          Copy URL
                        </>
                      )}
                    </button>
                    
                    <button
                      onClick={() => downloadImage(result.image_url, `generated-image-${Date.now()}.jpg`)}
                      className="inline-flex items-center gap-2 px-4 py-2 bg-gray-800/50 border border-white/20 text-white rounded-lg hover:bg-gray-700/50 transition-colors duration-200"
                    >
                      <Download className="w-4 h-4" />
                      Download
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>

          
<div className="space-y-6">
  {/* Generation Tips */}
  <div className="bg-black/20 backdrop-blur-sm border border-white/10 rounded-2xl p-6">
    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
      <Lightbulb className="w-5 h-5" style={{ color: "#b73939" }} />
      Generation Tips
    </h3>
    <ul className="space-y-2 text-sm text-gray-300">
      <li>• Be specific about style, colors, and mood</li>
      <li>• Mention artistic styles (e.g., "oil painting", "digital art")</li>
      <li>• Include lighting details (e.g., "golden hour", "dramatic shadows")</li>
      <li>• Specify perspective (e.g., "close-up", "aerial view")</li>
      <li>• Add atmospheric elements (e.g., "misty", "sunny")</li>
    </ul>
  </div>

  {/* Sample Prompts */}
  <div className="bg-black/20 backdrop-blur-sm border border-white/10 rounded-2xl p-6">
    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
      <Palette className="w-5 h-5" style={{ color: "#976f3e" }} />
      Sample Prompts
    </h3>
    <div className="space-y-3">
      {samplePrompts.map((samplePrompt, index) => (
        <button
          key={index}
          onClick={() => setPrompt(samplePrompt)}
          className="w-full text-left p-3 bg-gray-800/30 rounded-lg border border-white/10 text-sm text-gray-300 hover:bg-gray-700/50 transition-all duration-200"
          style={{
            borderColor: "#976f3e",
            hover: { borderColor: "#7d8f35" },
          }}
        >
          {samplePrompt}
        </button>
      ))}
    </div>
  </div>

  {/* Generation History */}
  <div className="bg-black/20 backdrop-blur-sm border border-white/10 rounded-2xl">
    <div className="p-6 border-b border-white/10 flex items-center justify-between">
      <h3 className="text-lg font-semibold text-white">Recent Generations</h3>
      {generationHistory.length > 0 && (
        <button
          onClick={clearHistory}
          className="text-sm transition-colors duration-200"
          style={{ color: "#b73939" }}
        >
          Clear All
        </button>
      )}
    </div>

    <div className="divide-y divide-white/10">
      {loadingHistory ? (
        <div className="p-6 text-center text-gray-400">
          <div
            className="animate-spin rounded-full h-6 w-6 border-b-2 mx-auto mb-4"
            style={{ borderColor: "#7d8f35" }}
          ></div>
          <p>Loading generation history...</p>
        </div>
      ) : generationHistory.length === 0 ? (
        <div className="p-6 text-center text-gray-400">
          <ImageIcon className="w-12 h-12 mx-auto text-gray-500 mb-4" />
          <p>No recent generations</p>
          <p className="text-sm">Your generation history will appear here</p>
        </div>
      ) : (
        generationHistory.map((item) => (
          <div
            key={item.id}
            className="p-4 hover:bg-gray-800/30 transition-colors duration-200"
          >
            <div className="flex items-start gap-3">
              <img
                src={item.image_url}
                alt={item.prompt}
                className="w-16 h-16 object-cover rounded-lg border border-white/10"
                onError={(e) => {
                  e.target.src =
                    "https://via.placeholder.com/64x64?text=Image";
                }}
              />
              <div className="flex-1 min-w-0">
                <button
                  onClick={() => repeatGeneration(item.prompt)}
                  className="text-sm font-medium text-white transition-colors duration-200 text-left w-full line-clamp-2"
                  style={{ color: "#976f3e" }}
                >
                  {item.prompt}
                </button>
                <p className="text-xs text-gray-400 flex items-center gap-1 mt-1">
                  <Clock className="w-3 h-3" />
                  {new Date(item.timestamp).toLocaleDateString()}
                </p>
              </div>
              <button
                onClick={() => removeFromHistory(item.id)}
                className="p-1 transition-colors duration-200"
                style={{ color: "#b73939" }}
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))
      )}
    </div>
  </div>
</div>
        </div>
      </div>
    </div>
  );
}

export default ImageGen;
