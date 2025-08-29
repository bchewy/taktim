import React, { useState } from 'react';

const SingleAnalysis = () => {
  const [formData, setFormData] = useState({
    feature_name: '',
    description: '',
    target_markets: ['US'],
    data_collected: [],
    user_demographics: ['general_audience'],
    ai_components: []
  });
  
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsAnalyzing(true);
    
    try {
      const response = await fetch('http://localhost:8001/api/comprehensive-compliance-analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Analysis failed:', error);
      setResult({ error: 'Analysis failed. Please try again.' });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleArrayChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value.split(',').map(item => item.trim()).filter(item => item)
    }));
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Single Feature Analysis</h1>
        <p className="text-gray-600">Analyze a TikTok feature for geo-specific compliance requirements</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Form */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Feature Details</h2>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Feature Name *
              </label>
              <input
                type="text"
                required
                value={formData.feature_name}
                onChange={(e) => setFormData(prev => ({ ...prev, feature_name: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., AI Teen Discovery Feed"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description *
              </label>
              <textarea
                required
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Detailed description of the feature functionality"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Target Markets (comma-separated)
              </label>
              <input
                type="text"
                value={formData.target_markets.join(', ')}
                onChange={(e) => handleArrayChange('target_markets', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="US, EU, Canada, Australia"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Data Collected (comma-separated)
              </label>
              <input
                type="text"
                value={formData.data_collected.join(', ')}
                onChange={(e) => handleArrayChange('data_collected', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="viewing_history, location_data, biometric_data"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                User Demographics (comma-separated)
              </label>
              <input
                type="text"
                value={formData.user_demographics.join(', ')}
                onChange={(e) => handleArrayChange('user_demographics', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="13-17, adult_users, general_audience"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                AI Components (comma-separated)
              </label>
              <input
                type="text"
                value={formData.ai_components.join(', ')}
                onChange={(e) => handleArrayChange('ai_components', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="recommendation_engine, facial_recognition, behavioral_analysis"
              />
            </div>

            <button
              type="submit"
              disabled={isAnalyzing}
              className={`w-full py-3 px-4 rounded-md font-medium ${
                isAnalyzing
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500'
              } text-white transition-colors`}
            >
              {isAnalyzing ? 'Analyzing...' : 'Analyze Feature'}
            </button>
          </form>
        </div>

        {/* Results */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Analysis Results</h2>
          
          {!result && (
            <div className="text-center text-gray-500 py-8">
              <p>Submit a feature for analysis to see results here.</p>
            </div>
          )}

          {isAnalyzing && (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Analyzing feature compliance...</p>
            </div>
          )}

          {result && result.error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-800">{result.error}</p>
            </div>
          )}

          {result && !result.error && (
            <div className="space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-semibold text-blue-900 mb-2">Analysis Complete</h3>
                <p className="text-blue-800">Feature: {result.feature_analyzed}</p>
                <p className="text-blue-800">Type: {result.analysis_type}</p>
                <p className="text-blue-800">Regulatory Ready: {result.regulatory_inquiry_ready ? 'Yes' : 'No'}</p>
              </div>
              
              {result.result && (
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2">Detailed Results</h4>
                  <pre className="text-sm text-gray-700 whitespace-pre-wrap overflow-x-auto">
                    {JSON.stringify(result.result, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SingleAnalysis;