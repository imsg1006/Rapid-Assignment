import React from 'react';
import { Link } from 'react-router-dom';
import { Search, Image, BarChart3, Sparkles, ArrowRight, CheckCircle, Users, Zap, Shield, Globe, Brain, Network } from 'lucide-react';

function Landing() {
  const features = [
    {
      icon: Search,
      title: 'AI-Powered Web Search',
      description: 'Get intelligent summaries from across the web with our advanced search capabilities.',
      color: 'text-[#F75C5C]',
      bgColor: 'bg-[#F75C5C]/10'
    },
    {
      icon: Image,
      title: 'Image Generation',
      description: 'Transform your ideas into stunning visuals using state-of-the-art AI models.',
      color: 'text-[#F2B366]',
      bgColor: 'bg-[#F2B366]/10'
    },
    {
      icon: BarChart3,
      title: 'Smart Dashboard',
      description: 'Organize and manage all your searches and generated content in one place.',
      color: 'text-[#DBF573]',
      bgColor: 'bg-[#DBF573]/10'
    },
    {
      icon: Shield,
      title: 'Secure & Private',
      description: 'Your data is protected with enterprise-grade security and privacy controls.',
      color: 'text-[#F75C5C]',
      bgColor: 'bg-[#F75C5C]/10'
    }
  ];

  const benefits = [
    'Live AI Processing',
    'Secure & Private',
    'Real-time Results',
    'High-quality Generation',
    'Personal History',
    'Responsive Design'
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#b73939] via-[#976f3e] to-[#7d8f35]">
      {/* Navigation */}
      <nav className="bg-black/20 backdrop-blur-sm border-b border-white/10 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-[#F75C5C] to-[#DBF573] rounded-lg flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-white">AI Explorer</span>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                to="/login"
                className="text-gray-200 hover:text-white transition-colors duration-200 px-4 py-2 rounded-lg hover:bg-white/10"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                className="bg-gradient-to-r from-[#F75C5C] via-[#F2B366] to-[#DBF573] text-white px-6 py-2 rounded-lg font-semibold hover:opacity-90 transition-all duration-200 shadow-lg"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Left Content */}
            <div className="space-y-8">
               
              
              <h1 className="text-5xl md:text-6xl font-bold text-white leading-tight">
                Discover the
                <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#f30707] via-[#fa9b28] to-[#e1f889]">
                  Future of AI
                </span>
                <br />
                Content
                <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#f30707] via-[#fa9b28] to-[#e1f889]">
                  Exploration
                </span>
              </h1>
              
              <p className="text-xl text-gray-100 leading-relaxed max-w-lg">
                Use the power of AI to search smarter, create amazing images, and keep all your discoveries neatly organized in one place.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4">
                <Link
                  to="/register"
                  className="bg-gradient-to-r from-[#F75C5C] via-[#F2B366] to-[#DBF573] text-white px-8 py-4 rounded-lg font-semibold text-lg hover:opacity-90 transition-all duration-200 flex items-center justify-center gap-2 shadow-lg group"
                >
                  Start Exploring
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-200" />
                </Link>
                <Link
                  to="/login"
                  className="border border-white/20 text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-white/10 transition-all duration-200 flex items-center justify-center gap-2"
                >
                  <Globe className="w-5 h-5" />
                  View Demo
                </Link>
              </div>
              
              <div className="flex items-center gap-6 pt-4">
                {benefits.slice(0, 2).map((benefit, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-[#DBF573] rounded-full"></div>
                    <span className="text-sm text-gray-200">{benefit}</span>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Right Visual */}
            <div className="relative">
              <div className="relative w-full h-96 bg-gradient-to-br from-[#F75C5C]/40 via-[#F2B366]/40 to-[#DBF573]/40 rounded-2xl border border-white/10 backdrop-blur-sm overflow-hidden">
                <div className="absolute inset-0 opacity-30">
                  <div className="absolute top-1/4 left-1/4 w-32 h-32 bg-[#F75C5C]/20 rounded-full blur-xl"></div>
                  <div className="absolute bottom-1/4 right-1/4 w-40 h-40 bg-[#DBF573]/20 rounded-full blur-xl"></div>
                </div>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="relative">
                    <div className="w-32 h-32 bg-gradient-to-br from-[#F75C5C] via-[#F2B366] to-[#DBF573] rounded-full flex items-center justify-center opacity-80">
                      <Brain className="w-20 h-20 text-white" />
                    </div>
                  </div>
                </div>
                <div className="absolute top-8 left-8 w-16 h-16 bg-[#F75C5C]/30 rounded-full blur-md animate-pulse"></div>
                <div className="absolute bottom-8 right-8 w-20 h-20 bg-[#DBF573]/30 rounded-full blur-md animate-pulse animation-delay-1000"></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
             
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Everything you need to explore
            </h2>
            <p className="text-xl text-gray-200 max-w-2xl mx-auto">
              Our comprehensive AI toolkit provides everything you need to discover, create, and organize digital content.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div key={index} className="group">
                  <div className="bg-black/20 backdrop-blur-sm border border-white/10 rounded-2xl p-6 hover:bg-black/30 transition-all duration-300 hover:border-[#F2B366]/30 hover:shadow-lg hover:shadow-[#F2B366]/20">
                    <div className={`w-12 h-12 ${feature.bgColor} rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300`}>
                      <Icon className={`w-6 h-6 ${feature.color}`} />
                    </div>
                    <h3 className="text-lg font-semibold text-white mb-3">{feature.title}</h3>
                    <p className="text-gray-300 leading-relaxed text-sm">{feature.description}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      {/* <section className="py-20 relative">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <div className="bg-black/20 backdrop-blur-sm border border-white/10 rounded-2xl p-12">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
              Ready to explore the future?
            </h2>
            <p className="text-xl text-gray-200 mb-8 leading-relaxed">
              Join thousands of users who are already using AI Explorer to discover, create, and organize their digital world.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/register"
                className="bg-gradient-to-r from-[#F75C5C] via-[#F2B366] to-[#DBF573] text-white px-8 py-4 rounded-lg font-semibold text-lg hover:opacity-90 transition-all duration-200 flex items-center justify-center gap-2 shadow-lg group"
              >
                Get Started for Free
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-200" />
              </Link>
              <Link
                to="/login"
                className="border border-white/20 text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-white/10 transition-all duration-200"
              >
                Sign In
              </Link>
            </div>
          </div>
        </div>
      </section> */}

      {/* Footer */}
      <footer className="bg-black/40 border-t border-white/10 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-r from-[#F75C5C] via-[#F2B366] to-[#DBF573] rounded-lg flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold text-white">AI Explorer</span>
              </div>
              <p className="text-gray-300 mb-4 max-w-md">
                The ultimate platform for AI-powered web search and image generation. 
                Discover, create, and organize your digital world.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold text-white mb-4">Features</h3>
              <ul className="space-y-2 text-gray-300">
                <li><Link to="/search" className="hover:text-white transition-colors">Web Search</Link></li>
                <li><Link to="/image-gen" className="hover:text-white transition-colors">Image Generation</Link></li>
                <li><Link to="/dashboard" className="hover:text-white transition-colors">Dashboard</Link></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold text-white mb-4">Account</h3>
              <ul className="space-y-2 text-gray-300">
                <li><Link to="/login" className="hover:text-white transition-colors">Sign In</Link></li>
                <li><Link to="/register" className="hover:text-white transition-colors">Register</Link></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-white/10 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; Powered by advanced AI technology.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default Landing;
