import React from 'react'
import { CheckCircle, AlertCircle, Database, Brain } from 'lucide-react'

const SystemStatus = ({ health }) => {
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
              <Brain className="w-4 h-4 text-purple-500 mr-2" />
              <span className="text-sm text-gray-600">
                LangChain RAG Active
              </span>
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