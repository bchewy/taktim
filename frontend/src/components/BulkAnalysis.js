import React, { useState } from 'react';

const BulkAnalysis = () => {
  const [features, setFeatures] = useState([
    {
      id: 1,
      summary: '',
      project_name: '',
      project_description: '',
      project_type: '',
      priority: '',
      due_date: ''
    }
  ]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState([]);

  const addFeature = () => {
    setFeatures(prev => [...prev, {
      id: prev.length + 1,
      summary: '',
      project_name: '',
      project_description: '',
      project_type: '',
      priority: '',
      due_date: ''
    }]);
  };

  const removeFeature = (id) => {
    setFeatures(prev => prev.filter(feature => feature.id !== id));
  };

  const updateFeature = (id, field, value) => {
    setFeatures(prev => prev.map(feature => 
      feature.id === id ? { ...feature, [field]: value } : feature
    ));
  };

  const handleBulkAnalysis = async () => {
    setIsAnalyzing(true);
    setResults([]);
    
    try {
      const promises = features.map(async (feature) => {
        if (!feature.summary || !feature.project_name || !feature.project_description) return null;
        
        const response = await fetch('http://localhost:8001/api/comprehensive-compliance-analysis', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(feature),
        });
        
        const data = await response.json();
        return { ...data, feature_id: feature.id };
      });
      
      const results = await Promise.all(promises);
      setResults(results.filter(result => result !== null));
    } catch (error) {
      console.error('Bulk analysis failed:', error);
      setResults([{ error: 'Bulk analysis failed. Please try again.' }]);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Bulk Feature Analysis</h1>
        <p className="text-gray-600">Analyze multiple features for compliance simultaneously</p>
      </div>

      <div className="space-y-8">
        {/* Features Input */}
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Features to Analyze</h2>
            <button
              onClick={addFeature}
              className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors"
            >
              + Add Feature
            </button>
          </div>

          <div className="space-y-6">
            {features.map((feature) => (
              <div key={feature.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="font-medium text-gray-900">Feature #{feature.id}</h3>
                  {features.length > 1 && (
                    <button
                      onClick={() => removeFeature(feature.id)}
                      className="text-red-600 hover:text-red-800"
                    >
                      Remove
                    </button>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Feature Name *
                    </label>
                    <input
                      type="text"
                      value={feature.project_name}
                      onChange={(e) => updateFeature(feature.id, 'project_name', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="e.g., Video Upload Feature"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Feature Type
                    </label>
                    <select
                      value={feature.project_type}
                      onChange={(e) => updateFeature(feature.id, 'project_type', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select feature type</option>
                      <option value="Web Application">Web Application</option>
                      <option value="Mobile Application">Mobile Application</option>
                      <option value="API Development">API Development</option>
                      <option value="Data Processing">Data Processing</option>
                      <option value="AI/ML Solution">AI/ML Solution</option>
                      <option value="Infrastructure">Infrastructure</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>

                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Summary *
                    </label>
                    <textarea
                      value={feature.summary}
                      onChange={(e) => updateFeature(feature.id, 'summary', e.target.value)}
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Brief summary of the feature"
                    />
                  </div>

                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Feature Description *
                    </label>
                    <textarea
                      value={feature.project_description}
                      onChange={(e) => updateFeature(feature.id, 'project_description', e.target.value)}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Detailed description of feature functionality"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Priority
                    </label>
                    <select
                      value={feature.priority}
                      onChange={(e) => updateFeature(feature.id, 'priority', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select priority</option>
                      <option value="Low">Low</option>
                      <option value="Medium">Medium</option>
                      <option value="High">High</option>
                      <option value="Critical">Critical</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Due Date
                    </label>
                    <input
                      type="date"
                      value={feature.due_date}
                      onChange={(e) => updateFeature(feature.id, 'due_date', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6">
            <button
              onClick={handleBulkAnalysis}
              disabled={isAnalyzing || features.some(f => !f.summary || !f.project_name || !f.project_description)}
              className={`w-full py-3 px-4 rounded-md font-medium ${
                isAnalyzing || features.some(f => !f.summary || !f.project_name || !f.project_description)
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500'
              } text-white transition-colors`}
            >
              {isAnalyzing ? 'Analyzing Features...' : `Analyze ${features.length} Feature${features.length > 1 ? 's' : ''}`}
            </button>
          </div>
        </div>

        {/* Results */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Bulk Analysis Results</h2>
          
          {!results.length && !isAnalyzing && (
            <div className="text-center text-gray-500 py-8">
              <p>Submit features for bulk analysis to see results here.</p>
            </div>
          )}

          {isAnalyzing && (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Analyzing {features.length} features...</p>
            </div>
          )}

          {results.length > 0 && (
            <div className="space-y-6">
              {results.map((result, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  {result.error ? (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                      <p className="text-red-800">{result.error}</p>
                    </div>
                  ) : (
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-2">
                        {result.feature_analyzed}
                      </h3>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="font-medium">Analysis Type:</span>
                          <br />
                          <span className="text-gray-600">{result.analysis_type}</span>
                        </div>
                        <div>
                          <span className="font-medium">Regulatory Ready:</span>
                          <br />
                          <span className={result.regulatory_inquiry_ready ? 'text-green-600' : 'text-red-600'}>
                            {result.regulatory_inquiry_ready ? 'Yes' : 'No'}
                          </span>
                        </div>
                        <div>
                          <span className="font-medium">Analyzed At:</span>
                          <br />
                          <span className="text-gray-600">{new Date(result.timestamp).toLocaleString()}</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default BulkAnalysis;