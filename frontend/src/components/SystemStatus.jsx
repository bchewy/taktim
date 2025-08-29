import React, { useState, useEffect } from 'react'
import { CheckCircle, AlertCircle, Database, Brain, Zap } from 'lucide-react'
import { getRagStatus, toggleRag } from '../api/client'

const SystemStatus = ({ health }) => {
  const [ragEnabled, setRagEnabled] = useState(true)
  const [toggling, setToggling] = useState(false)

  useEffect(() => {
    fetchRagStatus()
  }, [])

  const fetchRagStatus = async () => {
    try {
      const status = await getRagStatus()
      setRagEnabled(status.use_rag)
    } catch (error) {
      console.error('Failed to fetch RAG status:', error)
    }
  }

  const handleToggleRag = async () => {
    setToggling(true)
    try {
      const result = await toggleRag(!ragEnabled)
      setRagEnabled(result.use_rag)
    } catch (error) {
      console.error('Failed to toggle RAG:', error)
    } finally {
      setToggling(false)
    }
  }

  if (!health) {
    return null
  }

  const { ok, mem0_docs, policy_version, rules_hash } = health

  return (
    <div className="bg-white border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-6">
            <div className="flex items-center">
              {ok ? (
                <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
              ) : (
                <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
              )}
              <span className={`text-sm font-medium ${
                ok ? 'text-green-800' : 'text-red-800'
              }`}>
                System {ok ? 'Healthy' : 'Error'}
              </span>
            </div>

            <div className="flex items-center">
              <Database className="w-4 h-4 text-blue-500 mr-2" />
              <span className="text-sm text-gray-600">
                {mem0_docs} documents indexed
              </span>
            </div>

            <div className="flex items-center">
              <button
                onClick={handleToggleRag}
                disabled={toggling}
                className={`flex items-center px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                  ragEnabled 
                    ? 'bg-purple-100 text-purple-800 hover:bg-purple-200' 
                    : 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200'
                } ${toggling ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                {ragEnabled ? (
                  <Brain className="w-3 h-3 mr-1" />
                ) : (
                  <Zap className="w-3 h-3 mr-1" />
                )}
                {ragEnabled ? 'RAG Mode' : 'Direct Mode'}
                <span className="ml-1 text-xs">
                  {ragEnabled ? '(Comprehensive)' : '(Fast)'}
                </span>
              </button>
            </div>
          </div>

          <div className="flex items-center space-x-4 text-xs text-gray-500">
            <span>Policy: {policy_version}</span>
            <span>Rules: {rules_hash?.slice(0, 8)}...</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SystemStatus