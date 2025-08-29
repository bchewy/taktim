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
            <div className="space-y-6 max-h-96 overflow-y-auto">
              {/* Analysis Summary */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-blue-900">Analysis Complete</h3>
                  <span className={`px-2 py-1 text-xs rounded-full ${result.regulatory_inquiry_ready ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                    {result.regulatory_inquiry_ready ? 'Audit Ready' : 'In Progress'}
                  </span>
                </div>
                <div className="grid grid-cols-1 gap-2 text-sm">
                  <p className="text-blue-800"><span className="font-medium">Feature:</span> {result.feature_analyzed}</p>
                  <p className="text-blue-800"><span className="font-medium">Analysis Type:</span> {result.analysis_type?.replace(/_/g, ' ')}</p>
                </div>
              </div>

              {/* Legal Analysis Results */}
              {result.result?.legal_research && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <h4 className="font-semibold text-yellow-900 mb-3 flex items-center">
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 19 7.5 19s3.332-.523 4.5-1.253m0-13C13.168 5.477 14.754 5 16.5 5s3.332.477 4.5 1.253v13C19.832 18.477 18.246 19 16.5 19s-3.332-.523-4.5-1.253m0 0V9"></path>
                    </svg>
                    Legal Research Analysis
                  </h4>
                  <div className="text-sm text-yellow-800 space-y-2">
                    <p>✅ Real-time legal research completed using government APIs</p>
                    <div className="flex flex-wrap gap-2 mt-2">
                      <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">GovInfo.gov</span>
                      <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">Congress.gov</span>
                      <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">State Regulations</span>
                    </div>
                    
                    {/* Display legal analysis content if available */}
                    {result.result.legal_research.legal_analysis && (
                      <div className="mt-3 p-3 bg-white rounded border border-yellow-300">
                        <div className="text-sm text-gray-700 max-h-32 overflow-y-auto">
                          <pre className="whitespace-pre-wrap font-sans">{result.result.legal_research.legal_analysis}</pre>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Geo-Regulatory Mapping */}
              {result.result?.geo_regulatory_mapping && (
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"></path>
                    </svg>
                    Geo-Regulatory Compliance Analysis
                  </h4>
                  
                  {/* Parse and display geo-regulatory analysis text */}
                  <div className="space-y-3">
                    {typeof result.result.geo_regulatory_mapping === 'string' ? (
                      <div className="prose prose-sm max-w-none">
                        {result.result.geo_regulatory_mapping.split('\n').map((line, index) => {
                          if (line.trim() === '') return <br key={index} />;
                          
                          // Headers
                          if (line.startsWith('# ')) {
                            return <h3 key={index} className="text-lg font-bold text-gray-900 mt-4 mb-2">{line.substring(2)}</h3>;
                          }
                          if (line.startsWith('## ')) {
                            return <h4 key={index} className="text-base font-semibold text-gray-800 mt-3 mb-2">{line.substring(3)}</h4>;
                          }
                          if (line.startsWith('### ')) {
                            return <h5 key={index} className="text-sm font-semibold text-gray-700 mt-2 mb-1">{line.substring(4)}</h5>;
                          }
                          
                          // Bold text
                          if (line.includes('**') && line.includes('**')) {
                            return (
                              <p key={index} className="text-sm text-gray-700 mb-1">
                                {line.split('**').map((part, i) => i % 2 === 1 ? <strong key={i}>{part}</strong> : part)}
                              </p>
                            );
                          }
                          
                          // List items
                          if (line.trim().startsWith('- ')) {
                            return <li key={index} className="text-sm text-gray-600 ml-4 mb-1 list-disc">{line.substring(2)}</li>;
                          }
                          
                          // Regular paragraphs
                          if (line.trim()) {
                            return <p key={index} className="text-sm text-gray-700 mb-1">{line}</p>;
                          }
                          
                          return null;
                        })}
                      </div>
                    ) : (
                      <div className="text-sm text-gray-600">
                        <pre className="whitespace-pre-wrap">{JSON.stringify(result.result.geo_regulatory_mapping, null, 2)}</pre>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Compliance Status */}
              {result.result?.compliance_status && (
                <div className={`border rounded-lg p-4 ${
                  result.result.compliance_status.risk_level === 'HIGH' ? 'bg-red-50 border-red-200' :
                  result.result.compliance_status.risk_level === 'MEDIUM' ? 'bg-yellow-50 border-yellow-200' :
                  'bg-green-50 border-green-200'
                }`}>
                  <h4 className="font-semibold mb-3 flex items-center">
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    Overall Compliance Status
                  </h4>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium text-gray-700">Status:</span>
                      <p className="text-gray-900">{result.result.compliance_status.overall_status?.replace(/_/g, ' ')}</p>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Risk Level:</span>
                      <span className={`inline-block px-2 py-1 text-xs font-medium rounded-full ml-2 ${
                        result.result.compliance_status.risk_level === 'HIGH' ? 'bg-red-100 text-red-800' :
                        result.result.compliance_status.risk_level === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {result.result.compliance_status.risk_level}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex flex-wrap gap-3 pt-4 border-t border-gray-200">
                <button 
                  className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors"
                  onClick={() => window.print()}
                >
                  Print Report
                </button>
                <button 
                  className="px-4 py-2 bg-green-600 text-white text-sm rounded-md hover:bg-green-700 transition-colors"
                  onClick={() => {
                    const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `${result.feature_analyzed}-analysis.json`;
                    a.click();
                  }}
                >
                  Export JSON
                </button>
                <button 
                  className="px-4 py-2 bg-purple-600 text-white text-sm rounded-md hover:bg-purple-700 transition-colors"
                  onClick={() => navigator.clipboard.writeText(JSON.stringify(result, null, 2))}
                >
                  Copy to Clipboard
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SingleAnalysis;