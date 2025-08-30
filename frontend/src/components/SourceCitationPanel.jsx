import React, { useState } from 'react'
import { 
  BookOpen, 
  Calendar, 
  Clock, 
  AlertTriangle, 
  CheckCircle, 
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Database,
  Wifi,
  WifiOff
} from 'lucide-react'

const SourceCitationPanel = ({ validationData, analysisResult }) => {
  const [isExpanded, setIsExpanded] = useState(false)

  if (!validationData) {
    return null
  }

  const { api_calls_summary, sources_consulted = [], data_freshness_analysis = {} } = validationData
  const analysisDate = new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })

  const formatSourceDate = (dateString) => {
    if (!dateString) return 'Date not available'
    
    try {
      const date = new Date(dateString)
      const now = new Date()
      const ageInDays = Math.floor((now - date) / (1000 * 60 * 60 * 24))
      const ageInYears = Math.floor(ageInDays / 365.25)
      
      const formattedDate = date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
      
      if (ageInYears >= 1) {
        return `${formattedDate} (${ageInYears} year${ageInYears > 1 ? 's' : ''} old)`
      } else if (ageInDays >= 30) {
        const months = Math.floor(ageInDays / 30)
        return `${formattedDate} (${months} month${months > 1 ? 's' : ''} old)`
      } else if (ageInDays > 0) {
        return `${formattedDate} (${ageInDays} day${ageInDays > 1 ? 's' : ''} old)`
      } else {
        return `${formattedDate} (Current)`
      }
    } catch (error) {
      return dateString
    }
  }

  const getSourceFreshnessColor = (ageYears) => {
    if (ageYears < 1) return 'text-green-600 bg-green-50 border-green-200'
    if (ageYears < 3) return 'text-blue-600 bg-blue-50 border-blue-200'  
    if (ageYears < 10) return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    return 'text-red-600 bg-red-50 border-red-200'
  }

  const getAPIStatusColor = (status) => {
    switch (status) {
      case 'success': return 'text-green-600 bg-green-50'
      case 'failed': return 'text-red-600 bg-red-50'
      case 'calling': return 'text-yellow-600 bg-yellow-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const getAPIStatusIcon = (status) => {
    switch (status) {
      case 'success': return <CheckCircle className="w-4 h-4" />
      case 'failed': return <WifiOff className="w-4 h-4" />
      case 'calling': return <Clock className="w-4 h-4 animate-spin" />
      default: return <Wifi className="w-4 h-4" />
    }
  }

  const getFreshnessWarning = () => {
    const { overall_status, stale = 0, total_sources = 0 } = data_freshness_analysis
    
    if (overall_status === 'concerning') {
      return {
        type: 'error',
        message: `${stale} of ${total_sources} legal sources are over 10 years old. Consider verifying current applicability.`,
        icon: <AlertTriangle className="w-4 h-4" />
      }
    } else if (overall_status === 'moderate') {
      return {
        type: 'warning', 
        message: `Some legal sources may be outdated. ${stale} sources are over 10 years old.`,
        icon: <AlertTriangle className="w-4 h-4" />
      }
    } else {
      return {
        type: 'success',
        message: 'Legal sources are reasonably current.',
        icon: <CheckCircle className="w-4 h-4" />
      }
    }
  }

  const warning = getFreshnessWarning()
  const successRate = api_calls_summary?.success_rate || 0
  const avgResponseTime = api_calls_summary?.avg_response_time_ms || 0

  return (
    <div className="mt-6 bg-white border border-gray-200 rounded-lg shadow-sm">
      {/* Header */}
      <div 
        className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center space-x-3">
          <BookOpen className="w-5 h-5 text-blue-600" />
          <div>
            <h3 className="text-sm font-medium text-gray-900">Source Citations & Data Validation</h3>
            <p className="text-xs text-gray-600">
              Analysis completed: {analysisDate} | {sources_consulted.length} sources consulted | {successRate.toFixed(1)}% API success rate
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          {/* Data freshness indicator */}
          <div className={`px-2 py-1 rounded-full text-xs font-medium border ${
            warning.type === 'success' ? 'text-green-700 bg-green-50 border-green-200' :
            warning.type === 'warning' ? 'text-yellow-700 bg-yellow-50 border-yellow-200' :
            'text-red-700 bg-red-50 border-red-200'
          }`}>
            {data_freshness_analysis.overall_status || 'Unknown'}
          </div>
          
          {isExpanded ? (
            <ChevronUp className="w-4 h-4 text-gray-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-gray-400" />
          )}
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="border-t border-gray-200">
          {/* API Performance Summary */}
          <div className="p-4 bg-gray-50">
            <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center">
              <Database className="w-4 h-4 mr-2" />
              API Performance Summary
            </h4>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-3 bg-white rounded-lg border">
                <div className="text-lg font-semibold text-gray-900">{api_calls_summary?.successful_calls || 0}</div>
                <div className="text-xs text-gray-600">Successful Calls</div>
              </div>
              <div className="text-center p-3 bg-white rounded-lg border">
                <div className="text-lg font-semibold text-gray-900">{successRate.toFixed(1)}%</div>
                <div className="text-xs text-gray-600">Success Rate</div>
              </div>
              <div className="text-center p-3 bg-white rounded-lg border">
                <div className="text-lg font-semibold text-gray-900">{avgResponseTime.toFixed(0)}ms</div>
                <div className="text-xs text-gray-600">Avg Response Time</div>
              </div>
            </div>

            {/* API Status Details */}
            {validationData.api_details && (
              <div className="mt-4">
                <h5 className="text-xs font-medium text-gray-700 mb-2">API Call Details</h5>
                <div className="space-y-2">
                  {validationData.api_details.map((call, index) => (
                    <div key={index} className="flex items-center justify-between text-xs">
                      <div className="flex items-center space-x-2">
                        {getAPIStatusIcon(call.status)}
                        <span className="font-medium">{call.api_name}</span>
                      </div>
                      <div className={`px-2 py-1 rounded-full ${getAPIStatusColor(call.status)}`}>
                        {call.status === 'success' 
                          ? `${call.result_count || 0} results in ${call.response_time_ms?.toFixed(0) || 0}ms`
                          : call.status === 'failed' 
                          ? 'Failed'
                          : call.status
                        }
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Data Freshness Warning */}
          <div className={`p-4 border-b border-gray-200 ${
            warning.type === 'success' ? 'bg-green-50' :
            warning.type === 'warning' ? 'bg-yellow-50' : 
            'bg-red-50'
          }`}>
            <div className="flex items-start space-x-2">
              <div className={`${
                warning.type === 'success' ? 'text-green-600' :
                warning.type === 'warning' ? 'text-yellow-600' :
                'text-red-600'
              }`}>
                {warning.icon}
              </div>
              <div>
                <h4 className={`text-sm font-medium ${
                  warning.type === 'success' ? 'text-green-800' :
                  warning.type === 'warning' ? 'text-yellow-800' :
                  'text-red-800'
                }`}>
                  Data Freshness Assessment
                </h4>
                <p className={`text-sm ${
                  warning.type === 'success' ? 'text-green-700' :
                  warning.type === 'warning' ? 'text-yellow-700' :
                  'text-red-700'
                }`}>
                  {warning.message}
                </p>
              </div>
            </div>
          </div>

          {/* Sources List */}
          <div className="p-4">
            <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center">
              <Calendar className="w-4 h-4 mr-2" />
              Legal Sources Consulted ({sources_consulted.length})
            </h4>
            
            {sources_consulted.length === 0 ? (
              <p className="text-sm text-gray-600 italic">No specific source citations available</p>
            ) : (
              <div className="space-y-3">
                {sources_consulted.slice(0, 10).map((source, index) => {
                  const ageInYears = source.age_years || 0
                  
                  return (
                    <div key={index} className="flex items-start justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex-1 min-w-0">
                        <h5 className="text-sm font-medium text-gray-900 truncate">
                          {source.title || 'Untitled Source'}
                        </h5>
                        <div className="mt-1 space-y-1">
                          <div className="flex items-center space-x-4 text-xs text-gray-600">
                            <span className="flex items-center">
                              <Calendar className="w-3 h-3 mr-1" />
                              Published: {formatSourceDate(source.publication_date)}
                            </span>
                            <span className="flex items-center">
                              <Database className="w-3 h-3 mr-1" />
                              {source.source || 'Unknown Source'}
                            </span>
                          </div>
                          {source.jurisdiction && (
                            <div className="text-xs text-gray-600">
                              Jurisdiction: {source.jurisdiction}
                            </div>
                          )}
                        </div>
                      </div>
                      
                      <div className="ml-4 flex flex-col items-end space-y-1">
                        {ageInYears > 0 && (
                          <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getSourceFreshnessColor(ageInYears)}`}>
                            {ageInYears < 1 ? 'Current' :
                             ageInYears < 3 ? 'Fresh' :
                             ageInYears < 10 ? 'Aging' : 'Stale'
                            }
                          </span>
                        )}
                      </div>
                    </div>
                  )
                })}
                
                {sources_consulted.length > 10 && (
                  <p className="text-xs text-gray-600 italic text-center">
                    ... and {sources_consulted.length - 10} more sources
                  </p>
                )}
              </div>
            )}
          </div>

          {/* Citation Note */}
          <div className="p-4 bg-blue-50 border-t border-blue-200">
            <div className="flex items-start space-x-2">
              <ExternalLink className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
              <div className="text-xs text-blue-700">
                <p className="font-medium mb-1">Citation Information</p>
                <p>
                  This analysis was conducted on {analysisDate} using data retrieved from government APIs. 
                  Source publication dates reflect when the legal documents were originally issued or last updated. 
                  For the most current information, consult the official sources directly.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default SourceCitationPanel