import React, { useState } from 'react'
import { Upload, Plus, Trash2, Play, Download, FileText, AlertCircle, CheckCircle, Loader2 } from 'lucide-react'
import { bulkAnalyze } from '../api/client'
import AgentVisualization from './AgentVisualization'

const BulkAnalyze = () => {
  const [features, setFeatures] = useState([])
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [progress, setProgress] = useState({ current: 0, total: 0 })
  const [currentStage, setCurrentStage] = useState('initializing')

  const addFeature = () => {
    const newFeature = {
      id: Date.now(),
      feature_id: '',
      title: '',
      description: '',
      docs: '',
      code_hints: '',
      tags: ''
    }
    setFeatures([...features, newFeature])
  }

  const removeFeature = (id) => {
    setFeatures(features.filter(f => f.id !== id))
  }

  const updateFeature = (id, field, value) => {
    setFeatures(features.map(f => 
      f.id === id ? { ...f, [field]: value } : f
    ))
  }

  const loadExampleFeatures = () => {
    const exampleFeatures = [
      {
        id: 1,
        feature_id: 'personalized_recommendations',
        title: 'Personalized Content Recommendations',
        description: 'AI-driven system that analyzes user behavior to recommend personalized content feeds',
        docs: 'User preferences API, Content ranking system',
        code_hints: 'recommendation_engine.py, user_profiling.js',
        tags: 'personalization, recommendations, AI'
      },
      {
        id: 2,
        feature_id: 'minors_content_filter',
        title: 'Content Filter for Minors',
        description: 'Age-appropriate content filtering system with parental controls',
        docs: 'Age verification API, Parental controls guide',
        code_hints: 'age_filter.py, parental_controls.js',
        tags: 'minors, content_filter, age_verification'
      },
      {
        id: 3,
        feature_id: 'user_authentication',
        title: 'User Authentication System',
        description: 'Standard login and registration functionality with OAuth integration',
        docs: 'Authentication API, OAuth integration guide',
        code_hints: 'auth.py, login.js, oauth_handler.py',
        tags: 'authentication, security, oauth'
      }
    ]
    setFeatures(exampleFeatures)
  }

  const importFromCSV = (event) => {
    const file = event.target.files[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
      const csv = e.target.result
      const lines = csv.split('\n')
      const headers = lines[0].split(',').map(h => h.trim())
      
      const importedFeatures = []
      for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(',').map(v => v.trim())
        if (values.length >= headers.length && values[0]) {
          const feature = { id: Date.now() + i }
          headers.forEach((header, index) => {
            feature[header] = values[index] || ''
          })
          importedFeatures.push(feature)
        }
      }
      
      setFeatures(importedFeatures)
    }
    reader.readAsText(file)
    event.target.value = '' // Reset file input
  }

  const runBulkAnalysis = async () => {
    if (features.length === 0) {
      alert('Please add at least one feature to analyze')
      return
    }

    setLoading(true)
    setProgress({ current: 0, total: features.length })
    
    // Simulate stage progression for bulk analysis
    const stages = ['initializing', 'ai_analysis', 'geo_regulatory', 'generating_response']
    let stageIndex = 0
    
    const stageInterval = setInterval(() => {
      if (stageIndex < stages.length - 1) {
        stageIndex++
        setCurrentStage(stages[stageIndex])
      }
    }, 2000)

    try {
      // Convert features to API format
      const apiFeatures = features.map(f => ({
        feature_id: f.feature_id,
        title: f.title,
        description: f.description,
        docs: f.docs ? f.docs.split(',').map(s => s.trim()).filter(s => s) : [],
        code_hints: f.code_hints ? f.code_hints.split(',').map(s => s.trim()).filter(s => s) : [],
        tags: f.tags ? f.tags.split(',').map(s => s.trim()).filter(s => s) : []
      }))

      const result = await bulkAnalyze(apiFeatures)
      setResults(result)
      clearInterval(stageInterval)
      
    } catch (error) {
      console.error('Bulk analysis failed:', error)
      alert('Bulk analysis failed: ' + error.message)
      clearInterval(stageInterval)
    } finally {
      setLoading(false)
      setProgress({ current: 0, total: 0 })
      setCurrentStage('initializing')
    }
  }

  const exportTemplate = () => {
    const headers = ['feature_id', 'title', 'description', 'docs', 'code_hints', 'tags']
    const csvContent = headers.join(',') + '\n'
    
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'bulk_analysis_template.csv'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-6">
      {/* Agent Visualization */}
      <AgentVisualization 
        isActive={loading} 
        stage={currentStage}
        analysisType="bulk"
      />
      
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Bulk Feature Analysis</h2>
          <p className="text-gray-600">Analyze multiple features for compliance simultaneously</p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={exportTemplate}
            className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            <Download className="w-4 h-4 mr-2" />
            Template
          </button>
          <label className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 cursor-pointer">
            <Upload className="w-4 h-4 mr-2" />
            Import CSV
            <input
              type="file"
              accept=".csv"
              onChange={importFromCSV}
              className="hidden"
            />
          </label>
        </div>
      </div>

      {/* Feature Management */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-medium text-gray-900">Features to Analyze</h3>
            <div className="flex space-x-2">
              <button
                onClick={loadExampleFeatures}
                className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                Load Examples
              </button>
              <button
                onClick={addFeature}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Feature
              </button>
            </div>
          </div>
        </div>

        <div className="p-6">
          {features.length === 0 ? (
            <div className="text-center py-8">
              <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No features added yet. Add features manually or import from CSV.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {features.map((feature, index) => (
                <div key={feature.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-4">
                    <h4 className="text-sm font-medium text-gray-900">Feature #{index + 1}</h4>
                    <button
                      onClick={() => removeFeature(feature.id)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Feature ID *</label>
                      <input
                        type="text"
                        value={feature.feature_id}
                        onChange={(e) => updateFeature(feature.id, 'feature_id', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="unique_feature_id"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
                      <input
                        type="text"
                        value={feature.title}
                        onChange={(e) => updateFeature(feature.id, 'title', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Feature Title"
                      />
                    </div>
                  </div>
                  
                  <div className="mt-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Description *</label>
                    <textarea
                      value={feature.description}
                      onChange={(e) => updateFeature(feature.id, 'description', e.target.value)}
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Detailed feature description..."
                    />
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Docs</label>
                      <input
                        type="text"
                        value={feature.docs}
                        onChange={(e) => updateFeature(feature.id, 'docs', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="doc1, doc2, doc3"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Code Hints</label>
                      <input
                        type="text"
                        value={feature.code_hints}
                        onChange={(e) => updateFeature(feature.id, 'code_hints', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="file1.py, file2.js"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Tags</label>
                      <input
                        type="text"
                        value={feature.tags}
                        onChange={(e) => updateFeature(feature.id, 'tags', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="tag1, tag2, tag3"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {features.length > 0 && (
          <div className="px-6 py-4 border-t border-gray-200">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">
                {features.length} feature{features.length !== 1 ? 's' : ''} ready for analysis
              </span>
              <button
                onClick={runBulkAnalysis}
                disabled={loading || features.length === 0}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 disabled:opacity-50"
              >
                {loading ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <Play className="w-4 h-4 mr-2" />
                )}
                {loading ? 'Analyzing...' : 'Run Bulk Analysis'}
              </button>
            </div>
            
            {loading && progress.total > 0 && (
              <div className="mt-4">
                <div className="flex justify-between text-sm text-gray-600 mb-1">
                  <span>Processing features...</span>
                  <span>{progress.current} of {progress.total}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${(progress.current / progress.total) * 100}%` }}
                  ></div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Results */}
      {results && (
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-medium text-gray-900">Bulk Analysis Results</h3>
              <div className="flex items-center space-x-4 text-sm">
                <span className="flex items-center">
                  <AlertCircle className="w-4 h-4 text-red-500 mr-1" />
                  Compliance Required: {results.compliance_required || 0}
                </span>
                <span className="flex items-center">
                  <CheckCircle className="w-4 h-4 text-green-500 mr-1" />
                  No Compliance: {results.no_compliance || 0}
                </span>
              </div>
            </div>
          </div>
          
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">{results.count || 0}</div>
                <div className="text-sm text-gray-600">Features Analyzed</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">{results.compliance_required || 0}</div>
                <div className="text-sm text-gray-600">Require Compliance</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{results.no_compliance || 0}</div>
                <div className="text-sm text-gray-600">No Compliance Needed</div>
              </div>
            </div>
            
            <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
              <div className="flex items-center">
                <FileText className="w-5 h-5 text-blue-600 mr-2" />
                <div>
                  <h4 className="text-sm font-medium text-blue-800">Results Exported</h4>
                  <p className="text-sm text-blue-700">
                    Results have been saved to: <code className="bg-blue-100 px-1 rounded">{results.csv_path}</code>
                  </p>
                  <p className="text-sm text-blue-700 mt-1">
                    Use the "Download Evidence" button to get the complete analysis package.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default BulkAnalyze