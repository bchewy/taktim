import React, { useState, useEffect } from 'react';

const Results = () => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedResult, setSelectedResult] = useState(null);

  useEffect(() => {
    // In a real app, this would fetch from your backend
    // For now, we'll simulate with localStorage or mock data
    const mockResults = [
      {
        id: 1,
        feature_name: "AI Teen Discovery Feed",
        analysis_type: "comprehensive_geo_compliance",
        timestamp: new Date().toISOString(),
        regulatory_inquiry_ready: true,
        result: {
          compliance_status: {
            overall_status: "REQUIRES_IMMEDIATE_REVIEW",
            risk_level: "HIGH"
          },
          geo_regulatory_mapping: {
            US_FEDERAL: {
              regulations: ["COPPA"],
              requirements: ["Parental consent for under 13", "Age verification"],
              penalties: "Up to $43,792 per violation"
            },
            US_CALIFORNIA: {
              regulations: ["SB976"],
              requirements: ["No targeted ads to minors", "Default privacy settings"],
              penalties: "Up to $25,000 per affected child"
            }
          }
        }
      }
    ];

    // Simulate loading
    setTimeout(() => {
      setResults(mockResults);
      setLoading(false);
    }, 1000);
  }, []);

  const getRiskColor = (risk) => {
    switch (risk?.toUpperCase()) {
      case 'LOW': return 'text-green-600';
      case 'MEDIUM': return 'text-yellow-600';
      case 'HIGH': return 'text-orange-600';
      case 'CRITICAL': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getRiskBgColor = (risk) => {
    switch (risk?.toUpperCase()) {
      case 'LOW': return 'bg-green-100';
      case 'MEDIUM': return 'bg-yellow-100';
      case 'HIGH': return 'bg-orange-100';
      case 'CRITICAL': return 'bg-red-100';
      default: return 'bg-gray-100';
    }
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Analysis Results</h1>
        <p className="text-gray-600">Review compliance analysis results and generate audit trails</p>
      </div>

      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading results...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Results List */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow">
              <div className="p-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Recent Analyses</h2>
              </div>
              
              {results.length === 0 ? (
                <div className="p-6 text-center text-gray-500">
                  <p>No analysis results found.</p>
                  <p className="text-sm mt-2">Run some feature analyses to see results here.</p>
                </div>
              ) : (
                <div className="divide-y divide-gray-200">
                  {results.map((result) => (
                    <div
                      key={result.id}
                      className={`p-4 cursor-pointer hover:bg-gray-50 ${
                        selectedResult?.id === result.id ? 'bg-blue-50 border-r-4 border-blue-500' : ''
                      }`}
                      onClick={() => setSelectedResult(result)}
                    >
                      <h3 className="font-medium text-gray-900 mb-1">{result.feature_name}</h3>
                      <div className="flex items-center space-x-2 mb-2">
                        <span className={`px-2 py-1 text-xs rounded-full ${getRiskBgColor(result.result?.compliance_status?.risk_level)} ${getRiskColor(result.result?.compliance_status?.risk_level)}`}>
                          {result.result?.compliance_status?.risk_level || 'Unknown'}
                        </span>
                        <span className={`px-2 py-1 text-xs rounded-full ${result.regulatory_inquiry_ready ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-600'}`}>
                          {result.regulatory_inquiry_ready ? 'Audit Ready' : 'Pending'}
                        </span>
                      </div>
                      <p className="text-sm text-gray-500">
                        {new Date(result.timestamp).toLocaleDateString()}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Result Details */}
          <div className="lg:col-span-2">
            {!selectedResult ? (
              <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500">
                <p>Select a result from the list to view details</p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Header */}
                <div className="bg-white rounded-lg shadow p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-semibold text-gray-900">{selectedResult.feature_name}</h2>
                    <div className="flex space-x-2">
                      <span className={`px-3 py-1 text-sm rounded-full ${getRiskBgColor(selectedResult.result?.compliance_status?.risk_level)} ${getRiskColor(selectedResult.result?.compliance_status?.risk_level)}`}>
                        {selectedResult.result?.compliance_status?.risk_level || 'Unknown'} Risk
                      </span>
                      <span className={`px-3 py-1 text-sm rounded-full ${selectedResult.regulatory_inquiry_ready ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-600'}`}>
                        {selectedResult.regulatory_inquiry_ready ? 'Audit Trail Ready' : 'Audit Pending'}
                      </span>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="font-medium text-gray-700">Analysis Type:</span>
                      <p className="text-gray-600">{selectedResult.analysis_type}</p>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Overall Status:</span>
                      <p className="text-gray-600">{selectedResult.result?.compliance_status?.overall_status || 'N/A'}</p>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Analyzed:</span>
                      <p className="text-gray-600">{new Date(selectedResult.timestamp).toLocaleString()}</p>
                    </div>
                  </div>
                </div>

                {/* Geo-Regulatory Mapping */}
                {selectedResult.result?.geo_regulatory_mapping && (
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Jurisdiction Analysis</h3>
                    <div className="space-y-4">
                      {Object.entries(selectedResult.result.geo_regulatory_mapping).map(([jurisdiction, data]) => (
                        <div key={jurisdiction} className="border border-gray-200 rounded-lg p-4">
                          <h4 className="font-medium text-gray-900 mb-2">{jurisdiction.replace(/_/g, ' ')}</h4>
                          
                          {data.regulations && (
                            <div className="mb-3">
                              <span className="text-sm font-medium text-gray-700">Applicable Regulations:</span>
                              <div className="flex flex-wrap gap-2 mt-1">
                                {data.regulations.map((reg, idx) => (
                                  <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                                    {reg}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                          
                          {data.requirements && (
                            <div className="mb-3">
                              <span className="text-sm font-medium text-gray-700">Requirements:</span>
                              <ul className="list-disc list-inside text-sm text-gray-600 mt-1">
                                {data.requirements.map((req, idx) => (
                                  <li key={idx}>{req}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          
                          {data.penalties && (
                            <div>
                              <span className="text-sm font-medium text-gray-700">Potential Penalties:</span>
                              <p className="text-sm text-red-600 mt-1">{data.penalties}</p>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Actions</h3>
                  <div className="flex space-x-4">
                    <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors">
                      Download Report
                    </button>
                    <button className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors">
                      Generate Audit Trail
                    </button>
                    <button className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 transition-colors">
                      Export to PDF
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Results;