import React from 'react'
import { AlertTriangle, CheckCircle, Info, ExternalLink, Loader2 } from 'lucide-react'

const ResultDisplay = ({ result, loading }) => {
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-64">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin mb-4" />
        <p className="text-gray-600">Running LangChain RAG analysis...</p>
        <p className="text-sm text-gray-500 mt-2">
          Searching legal documents and analyzing compliance requirements
        </p>
      </div>
    )
  }

  if (!result) {
    return (
      <div className="text-center py-12">
        <Info className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600">
          Enter feature details and click "Analyze Feature" to get started
        </p>
      </div>
    )
  }

  if (result.error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex items-center">
          <AlertTriangle className="w-5 h-5 text-red-500 mr-2" />
          <h3 className="text-sm font-medium text-red-800">Analysis Error</h3>
        </div>
        <p className="mt-2 text-sm text-red-700">{result.error}</p>
      </div>
    )
  }

  const {
    feature_id,
    needs_geo_compliance,
    confidence,
    reasoning,
    regulations,
    signals,
    citations,
    matched_rules,
    policy_version,
    ts
  } = result

  return (
    <div className="space-y-6">
      {/* Main Result */}
      <div className={`border rounded-lg p-4 ${
        needs_geo_compliance 
          ? 'bg-red-50 border-red-200' 
          : 'bg-green-50 border-green-200'
      }`}>
        <div className="flex items-center mb-2">
          {needs_geo_compliance ? (
            <AlertTriangle className="w-5 h-5 text-red-500 mr-2" />
          ) : (
            <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
          )}
          <h3 className={`font-semibold ${
            needs_geo_compliance ? 'text-red-800' : 'text-green-800'
          }`}>
            {needs_geo_compliance ? 'Compliance Required' : 'No Compliance Needed'}
          </h3>
        </div>
        <div className="text-sm">
          <span className={`font-medium ${
            needs_geo_compliance ? 'text-red-700' : 'text-green-700'
          }`}>
            Confidence: {Math.round(confidence * 100)}%
          </span>
        </div>
      </div>

      {/* Feature Info */}
      <div>
        <h4 className="font-medium text-gray-900 mb-2">Feature Analysis</h4>
        <div className="bg-gray-50 rounded-md p-3">
          <div className="text-sm">
            <strong>ID:</strong> {feature_id}
          </div>
          <div className="text-sm mt-1">
            <strong>Analysis Method:</strong> {matched_rules?.join(', ') || 'LangChain RAG'}
          </div>
        </div>
      </div>

      {/* Reasoning */}
      <div>
        <h4 className="font-medium text-gray-900 mb-2">AI Reasoning</h4>
        <div className="bg-gray-50 rounded-md p-3">
          <p className="text-sm text-gray-700">{reasoning}</p>
        </div>
      </div>

      {/* Regulations */}
      {regulations && regulations.length > 0 && (
        <div>
          <h4 className="font-medium text-gray-900 mb-2">Applicable Regulations</h4>
          <div className="space-y-2">
            {regulations.map((regulation, index) => (
              <div key={index} className="bg-yellow-50 border border-yellow-200 rounded-md p-3">
                <div className="flex items-center">
                  <AlertTriangle className="w-4 h-4 text-yellow-600 mr-2" />
                  <span className="text-sm font-medium text-yellow-800">{regulation}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Signals */}
      {signals && signals.length > 0 && (
        <div>
          <h4 className="font-medium text-gray-900 mb-2">Compliance Signals Detected</h4>
          <div className="flex flex-wrap gap-2">
            {signals.map((signal, index) => (
              <span
                key={index}
                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
              >
                {signal}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Citations */}
      {citations && citations.length > 0 && (
        <div>
          <h4 className="font-medium text-gray-900 mb-2">Legal Citations</h4>
          <div className="space-y-2">
            {citations.map((citation, index) => (
              <div key={index} className="border border-gray-200 rounded-md p-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="text-sm font-medium text-gray-900 mb-1">
                      {citation.source}
                    </div>
                    <p className="text-sm text-gray-600">{citation.snippet}</p>
                  </div>
                  {citation.source.startsWith('http') && (
                    <ExternalLink className="w-4 h-4 text-gray-400 ml-2 flex-shrink-0" />
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Metadata */}
      <div className="text-xs text-gray-500 pt-4 border-t">
        <div>Policy Version: {policy_version}</div>
        <div>Analysis Time: {new Date(ts).toLocaleString()}</div>
      </div>
    </div>
  )
}

export default ResultDisplay