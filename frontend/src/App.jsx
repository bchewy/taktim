import React, { useState, useEffect } from 'react'
import { Zap, Brain, FileText, Download, RefreshCw, History, Upload, Home } from 'lucide-react'
import AnalysisForm from './components/AnalysisForm'
import ResultDisplay from './components/ResultDisplay'
import SystemStatus from './components/SystemStatus'
import AuditTrail from './components/AuditTrail'
import BulkAnalyze from './components/BulkAnalyze'
import AgentVisualization from './components/AgentVisualization'
import { analyzeFeature, getSystemHealth, refreshCorpus, downloadEvidence, getRagStatus } from './api/client'

function App() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [loadingStage, setLoadingStage] = useState('initializing')
  const [systemHealth, setSystemHealth] = useState(null)
  const [refreshing, setRefreshing] = useState(false)
  const [currentPage, setCurrentPage] = useState('analysis') // 'analysis', 'bulk', 'audit'

  useEffect(() => {
    checkSystemHealth()
  }, [])

  const checkSystemHealth = async () => {
    try {
      const health = await getSystemHealth()
      setSystemHealth(health)
    } catch (error) {
      console.error('Failed to check system health:', error)
    }
  }

  const handleAnalyze = async (featureData) => {
    setLoading(true)
    setLoadingStage('initializing')
    
    try {
      // Check which mode is being used
      const ragStatus = await getRagStatus()
      const isRagMode = ragStatus.use_rag
      
      // Different stages based on mode
      let stageTimeouts
      if (isRagMode) {
        // RAG mode stages
        stageTimeouts = [
          () => setLoadingStage('vector_search'),
          () => setLoadingStage('rag_retrieval'), 
          () => setLoadingStage('ai_analysis'),
          () => setLoadingStage('generating_response')
        ]
      } else {
        // Direct mode stages (simpler, faster)
        stageTimeouts = [
          () => setLoadingStage('ai_analysis'),
          () => setLoadingStage('generating_response')
        ]
      }
      
      // Set stage progression timers
      const timers = stageTimeouts.map((stageFn, index) => 
        setTimeout(stageFn, (index + 1) * (isRagMode ? 3000 : 1500)) // Faster for Direct mode
      )
      
      const analysisResult = await analyzeFeature(featureData)
      
      // Clear all pending timers
      timers.forEach(timer => clearTimeout(timer))
      
      setResult(analysisResult)
    } catch (error) {
      console.error('Analysis failed:', error)
      setResult({ error: 'Analysis failed: ' + error.message })
    } finally {
      setLoading(false)
      setLoadingStage('initializing')
    }
  }

  const handleRefreshCorpus = async () => {
    setRefreshing(true)
    try {
      const refreshResult = await refreshCorpus()
      console.log('Corpus refresh result:', refreshResult)
      await checkSystemHealth() // Refresh system status
      alert(`Corpus refreshed successfully! Indexed ${refreshResult.ingested} documents.`)
    } catch (error) {
      console.error('Corpus refresh failed:', error)
      alert('Corpus refresh failed: ' + error.message)
    } finally {
      setRefreshing(false)
    }
  }

  const handleDownloadEvidence = async () => {
    try {
      await downloadEvidence()
    } catch (error) {
      console.error('Evidence download failed:', error)
      alert('Evidence download failed: ' + error.message)
    }
  }

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'analysis':
        return (
          <div className="space-y-8">
            {/* Agent Visualization */}
            <AgentVisualization 
              isActive={loading} 
              stage={loadingStage}
              analysisType="single"
            />
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Analysis Form */}
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center mb-6">
                  <Brain className="h-6 w-6 text-blue-600 mr-2" />
                  <h2 className="text-xl font-semibold text-gray-900">Feature Analysis</h2>
                </div>
                <AnalysisForm onAnalyze={handleAnalyze} loading={loading} />
              </div>

              {/* Results */}
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center mb-6">
                  <FileText className="h-6 w-6 text-green-600 mr-2" />
                  <h2 className="text-xl font-semibold text-gray-900">Analysis Results</h2>
                </div>
                <ResultDisplay result={result} loading={loading} loadingStage={loadingStage} />
              </div>
            </div>
          </div>
        )
      case 'bulk':
        return <BulkAnalyze />
      case 'audit':
        return <AuditTrail onDownloadEvidence={handleDownloadEvidence} />
      default:
        return null
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Zap className="h-8 w-8 text-blue-600 mr-3" />
              <div>
                <h1 className="text-3xl font-bold text-gray-900">GeoGov Lite</h1>
                <p className="text-sm text-gray-600">LangChain RAG-powered Compliance Analysis</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={handleRefreshCorpus}
                disabled={refreshing}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50"
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                {refreshing ? 'Refreshing...' : 'Refresh Corpus'}
              </button>
              
              <button
                onClick={handleDownloadEvidence}
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                <Download className="w-4 h-4 mr-2" />
                Download Evidence
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            <button
              onClick={() => setCurrentPage('analysis')}
              className={`py-4 px-2 border-b-2 font-medium text-sm ${
                currentPage === 'analysis'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Home className="w-4 h-4 inline-block mr-2" />
              Single Analysis
            </button>
            <button
              onClick={() => setCurrentPage('bulk')}
              className={`py-4 px-2 border-b-2 font-medium text-sm ${
                currentPage === 'bulk'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Upload className="w-4 h-4 inline-block mr-2" />
              Bulk Analysis
            </button>
            <button
              onClick={() => setCurrentPage('audit')}
              className={`py-4 px-2 border-b-2 font-medium text-sm ${
                currentPage === 'audit'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <History className="w-4 h-4 inline-block mr-2" />
              Audit Trail
            </button>
          </div>
        </div>
      </div>

      {/* System Status */}
      <SystemStatus health={systemHealth} />

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderCurrentPage()}

        {/* How it Works - Show only on analysis page */}
        {currentPage === 'analysis' && (
          <div className="mt-12 bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">How LangChain RAG Analysis Works</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Brain className="w-6 h-6 text-blue-600" />
                </div>
                <h4 className="font-medium text-gray-900 mb-2">1. Smart Retrieval</h4>
                <p className="text-sm text-gray-600">
                  LangChain RAG searches the legal knowledge base using vector similarity to find relevant regulations and compliance documents.
                </p>
              </div>
              
              <div className="text-center">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Zap className="w-6 h-6 text-green-600" />
                </div>
                <h4 className="font-medium text-gray-900 mb-2">2. AI Analysis</h4>
                <p className="text-sm text-gray-600">
                  GPT-5 analyzes your feature against retrieved legal context using finder, counter, and judge methodologies.
                </p>
              </div>
              
              <div className="text-center">
                <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <FileText className="w-6 h-6 text-purple-600" />
                </div>
                <h4 className="font-medium text-gray-900 mb-2">3. Compliance Decision</h4>
                <p className="text-sm text-gray-600">
                  Provides clear compliance recommendations with confidence scores, relevant regulations, and legal citations.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App