import React, { useState, useEffect } from 'react'
import { History, Search, Filter, Download, AlertTriangle, CheckCircle, Calendar, User, FileText } from 'lucide-react'

const AuditTrail = ({ onDownloadEvidence }) => {
  const [auditData, setAuditData] = useState([])
  const [filteredData, setFilteredData] = useState([])
  const [loading, setLoading] = useState(false)
  const [filters, setFilters] = useState({
    search: '',
    compliance: 'all', // all, required, not_required
    dateRange: '7d', // 1d, 7d, 30d, all
    confidence: 'all' // all, high, medium, low
  })

  // Mock data - In real app, this would come from an API endpoint to fetch receipts.jsonl
  const mockAuditData = [
    {
      hash: 'sha256-abc123',
      feature_id: 'personalized_recommendations',
      needs_geo_compliance: true,
      confidence: 0.85,
      reasoning: 'Feature involves personalized content ranking which requires compliance under EU DSA Article 38',
      regulations: ['EU Digital Services Act Article 38', 'GDPR Article 22'],
      signals: ['personalization', 'recommendations', 'profiling'],
      matched_rules: ['LANGCHAIN_RAG_DECISION'],
      ts: '2024-01-15T10:30:00Z',
      policy_version: 'v0.1.0'
    },
    {
      hash: 'sha256-def456',
      feature_id: 'user_authentication',
      needs_geo_compliance: false,
      confidence: 0.92,
      reasoning: 'Standard authentication feature with no personalization or data processing concerns',
      regulations: [],
      signals: ['authentication', 'security'],
      matched_rules: ['LANGCHAIN_RAG_DECISION'],
      ts: '2024-01-15T09:15:00Z',
      policy_version: 'v0.1.0'
    },
    {
      hash: 'sha256-ghi789',
      feature_id: 'minors_content_filter',
      needs_geo_compliance: true,
      confidence: 0.95,
      reasoning: 'Content filtering for minors requires compliance with California SB976 and COPPA',
      regulations: ['California SB976', 'COPPA'],
      signals: ['minors', 'content_filter', 'age_verification'],
      matched_rules: ['LANGCHAIN_RAG_DECISION'],
      ts: '2024-01-14T16:45:00Z',
      policy_version: 'v0.1.0'
    }
  ]

  useEffect(() => {
    loadAuditData()
  }, [])

  useEffect(() => {
    applyFilters()
  }, [filters, auditData])

  const loadAuditData = async () => {
    setLoading(true)
    try {
      // In real app, fetch from /api/audit_trail or similar endpoint
      // For now, use mock data
      setTimeout(() => {
        setAuditData(mockAuditData)
        setLoading(false)
      }, 500)
    } catch (error) {
      console.error('Failed to load audit data:', error)
      setLoading(false)
    }
  }

  const applyFilters = () => {
    let filtered = [...auditData]

    // Search filter
    if (filters.search) {
      const searchLower = filters.search.toLowerCase()
      filtered = filtered.filter(item =>
        item.feature_id.toLowerCase().includes(searchLower) ||
        item.reasoning.toLowerCase().includes(searchLower) ||
        item.regulations.some(reg => reg.toLowerCase().includes(searchLower))
      )
    }

    // Compliance filter
    if (filters.compliance !== 'all') {
      filtered = filtered.filter(item =>
        filters.compliance === 'required' ? item.needs_geo_compliance : !item.needs_geo_compliance
      )
    }

    // Date range filter
    if (filters.dateRange !== 'all') {
      const now = new Date()
      const daysAgo = {
        '1d': 1,
        '7d': 7,
        '30d': 30
      }[filters.dateRange]

      if (daysAgo) {
        const cutoff = new Date(now.getTime() - daysAgo * 24 * 60 * 60 * 1000)
        filtered = filtered.filter(item => new Date(item.ts) >= cutoff)
      }
    }

    // Confidence filter
    if (filters.confidence !== 'all') {
      const confidenceRanges = {
        'high': [0.8, 1.0],
        'medium': [0.5, 0.8],
        'low': [0.0, 0.5]
      }
      const [min, max] = confidenceRanges[filters.confidence]
      filtered = filtered.filter(item => item.confidence >= min && item.confidence <= max)
    }

    setFilteredData(filtered)
  }

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleString()
  }

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-green-600 bg-green-50'
    if (confidence >= 0.5) return 'text-yellow-600 bg-yellow-50'
    return 'text-red-600 bg-red-50'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Analysis Audit Trail</h2>
          <p className="text-gray-600">Historical compliance analysis records and decisions</p>
        </div>
        <button
          onClick={onDownloadEvidence}
          className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
        >
          <Download className="w-4 h-4 mr-2" />
          Download Evidence
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                className="pl-10 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Search features, regulations..."
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Compliance Status</label>
            <select
              value={filters.compliance}
              onChange={(e) => handleFilterChange('compliance', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All</option>
              <option value="required">Compliance Required</option>
              <option value="not_required">No Compliance</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Date Range</label>
            <select
              value={filters.dateRange}
              onChange={(e) => handleFilterChange('dateRange', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="1d">Last 24 hours</option>
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="all">All time</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Confidence</label>
            <select
              value={filters.confidence}
              onChange={(e) => handleFilterChange('confidence', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All</option>
              <option value="high">High (80%+)</option>
              <option value="medium">Medium (50-80%)</option>
              <option value="low">Low (&lt;50%)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results Summary */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">
            Showing {filteredData.length} of {auditData.length} analyses
          </span>
          <div className="flex items-center space-x-4 text-sm">
            <span className="flex items-center">
              <div className="w-2 h-2 bg-red-500 rounded-full mr-1"></div>
              Compliance Required: {filteredData.filter(d => d.needs_geo_compliance).length}
            </span>
            <span className="flex items-center">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-1"></div>
              No Compliance: {filteredData.filter(d => !d.needs_geo_compliance).length}
            </span>
          </div>
        </div>
      </div>

      {/* Audit Trail List */}
      <div className="space-y-4">
        {loading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-gray-600">Loading audit trail...</p>
          </div>
        ) : filteredData.length === 0 ? (
          <div className="text-center py-8">
            <History className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No analyses found matching your filters</p>
          </div>
        ) : (
          filteredData.map((analysis, index) => (
            <div key={analysis.hash} className="bg-white rounded-lg shadow border">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      {analysis.needs_geo_compliance ? (
                        <AlertTriangle className="w-5 h-5 text-red-500 mr-2" />
                      ) : (
                        <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                      )}
                      <h3 className="text-lg font-semibold text-gray-900">
                        {analysis.feature_id}
                      </h3>
                      <span className={`ml-3 px-2 py-1 text-xs font-medium rounded-full ${getConfidenceColor(analysis.confidence)}`}>
                        {Math.round(analysis.confidence * 100)}% confidence
                      </span>
                    </div>
                    
                    <div className="flex items-center text-sm text-gray-500 space-x-4">
                      <span className="flex items-center">
                        <Calendar className="w-4 h-4 mr-1" />
                        {formatDate(analysis.ts)}
                      </span>
                      <span className="flex items-center">
                        <FileText className="w-4 h-4 mr-1" />
                        {analysis.hash.slice(-8)}
                      </span>
                    </div>
                  </div>

                  <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                    analysis.needs_geo_compliance
                      ? 'bg-red-100 text-red-800'
                      : 'bg-green-100 text-green-800'
                  }`}>
                    {analysis.needs_geo_compliance ? 'Compliance Required' : 'No Compliance'}
                  </div>
                </div>

                <div className="mb-4">
                  <p className="text-gray-700">{analysis.reasoning}</p>
                </div>

                {analysis.regulations.length > 0 && (
                  <div className="mb-4">
                    <h4 className="text-sm font-medium text-gray-900 mb-2">Applicable Regulations:</h4>
                    <div className="flex flex-wrap gap-2">
                      {analysis.regulations.map((reg, idx) => (
                        <span key={idx} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                          {reg}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">Signals Detected:</h4>
                  <div className="flex flex-wrap gap-2">
                    {analysis.signals.map((signal, idx) => (
                      <span key={idx} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {signal}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>Analysis Method: {analysis.matched_rules.join(', ')}</span>
                  <span>Policy: {analysis.policy_version}</span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default AuditTrail