import React, { useState, useCallback } from 'react'
import { FileText, AlertCircle, CheckCircle, Loader2 } from 'lucide-react'
import { bulkAnalyze } from '../api/client'
import api from '../api/client'
import AgentVisualization from './AgentVisualization'

const BulkAnalyze = () => {
  const [isDragOver, setIsDragOver] = useState(false)
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [currentStage, setCurrentStage] = useState('initializing')

  const handleDragOver = useCallback((e) => {
    e.preventDefault()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e) => {
    e.preventDefault()
    setIsDragOver(false)
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setIsDragOver(false)
    
    const files = Array.from(e.dataTransfer.files)
    const csvFile = files.find(file => file.name.endsWith('.csv'))
    
    if (csvFile) {
      handleFileUpload(csvFile)
    } else {
      alert('Please drop a CSV file')
    }
  }, [])

  const parseCSV = (text) => {
    const lines = text.split('\n').filter(line => line.trim())
    if (lines.length < 2) return []
    
    const headers = lines[0].split(',').map(h => h.trim())
    const features = []
    
    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',').map(v => v.trim())
      const feature = {}
      headers.forEach((header, index) => {
        feature[header] = values[index] || ''
      })
      features.push(feature)
    }
    
    return features
  }

  const pollForResults = async (taskId, stageInterval) => {
    const maxAttempts = 30 // 5 minutes max
    let attempts = 0
    
    while (attempts < maxAttempts) {
      try {
        const response = await api.get(`/api/results/${taskId}`)
        const task = response.data
        
        if (task.status === 'completed') {
          setResults(task)
          clearInterval(stageInterval)
          return
        } else if (task.status === 'failed') {
          throw new Error(task.error || 'Analysis failed')
        }
        
        // Wait 10 seconds before next poll
        await new Promise(resolve => setTimeout(resolve, 10000))
        attempts++
      } catch (error) {
        clearInterval(stageInterval)
        throw error
      }
    }
    
    clearInterval(stageInterval)
    throw new Error('Analysis timed out')
  }

  const handleFileInputChange = (e) => {
    const file = e.target.files[0]
    if (file && file.name.endsWith('.csv')) {
      handleFileUpload(file)
    } else {
      alert('Please select a CSV file')
    }
  }

  const handleFileUpload = async (file) => {
    setLoading(true)
    setResults(null)
    
    try {
      // Read the CSV file
      const text = await file.text()
      const features = parseCSV(text)
      
      if (features.length === 0) {
        throw new Error('No valid data found in CSV file')
      }
      
      // Start stage progression
      const stages = ['initializing', 'ai_analysis', 'geo_regulatory', 'generating_response']
      let stageIndex = 0
      
      const stageInterval = setInterval(() => {
        if (stageIndex < stages.length - 1) {
          stageIndex++
          setCurrentStage(stages[stageIndex])
        }
      }, 2000)
      
      // Call the bulk analyze API
      const taskResponse = await bulkAnalyze(features)
      const taskId = taskResponse.task_id
      
      // Poll for results
      await pollForResults(taskId, stageInterval)
      
    } catch (error) {
      console.error('CSV analysis failed:', error)
      alert('Analysis failed: ' + error.message)
    } finally {
      setLoading(false)
      setCurrentStage('initializing')
    }
  }


  return (
    <div className="h-full flex items-center justify-center">
      <div className="w-full max-w-2xl">
        {/* Agent Visualization */}
        {loading && (
          <div className="mb-8">
            <AgentVisualization 
              isActive={loading} 
              stage={currentStage}
              analysisType="bulk"
            />
          </div>
        )}
        
        {/* CSV Upload Area - Only drag and drop */}
        <div
          className={`border-3 border-dashed rounded-xl p-12 text-center transition-all duration-300 ${
            isDragOver
              ? "border-slate-600 bg-slate-50 dark:bg-slate-800/30 scale-105 shadow-xl"
              : "border-gray-400 dark:border-gray-600 hover:border-slate-500 dark:hover:border-slate-500 bg-white dark:bg-slate-900/50"
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <div className="mb-6">
            <svg
              className={`mx-auto h-16 w-16 transition-colors ${
                isDragOver ? "text-slate-600 dark:text-slate-400" : "text-gray-400 dark:text-gray-500"
              }`}
              stroke="currentColor"
              fill="none"
              viewBox="0 0 48 48"
            >
              <path
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
          
          <div className="mb-6">
            <p className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
              {loading ? "Processing CSV..." : isDragOver ? "Release to upload" : "Drop CSV file here"}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              CSV format with feature data for bulk compliance analysis
            </p>
          </div>

          {!loading && (
            <>
              <div className="mb-6">
                <span className="text-gray-400 dark:text-gray-500">or</span>
              </div>

              <label className="inline-flex items-center px-6 py-3 border-2 border-slate-600 dark:border-slate-400 text-sm font-medium rounded-lg text-slate-700 dark:text-slate-300 bg-transparent hover:bg-slate-50 dark:hover:bg-slate-800 cursor-pointer transition-all duration-200">
                Browse Files
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleFileInputChange}
                  className="sr-only"
                />
              </label>
            </>
          )}
          
          {loading && (
            <div className="flex items-center justify-center mt-6">
              <Loader2 className="w-8 h-8 animate-spin text-slate-600 dark:text-slate-400" />
            </div>
          )}
        </div>

        
        {/* Results */}
        {results && (
          <div className="mt-8 bg-white dark:bg-slate-900/50 p-6 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">Bulk Analysis Results</h3>
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
                  <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">{results.count || 0}</div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Features Analyzed</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-600">{results.compliance_required || 0}</div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Require Compliance</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{results.no_compliance || 0}</div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">No Compliance Needed</div>
                </div>
              </div>
              
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md p-4">
                <div className="flex items-center">
                  <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400 mr-2" />
                  <div>
                    <h4 className="text-sm font-medium text-blue-800 dark:text-blue-200">Results Exported</h4>
                    <p className="text-sm text-blue-700 dark:text-blue-300">
                      Results have been saved to: <code className="bg-blue-100 dark:bg-blue-800 px-1 rounded">{results.csv_path}</code>
                    </p>
                    <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
                      Use the "Download Evidence" button to get the complete analysis package.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default BulkAnalyze