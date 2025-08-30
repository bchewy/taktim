import React, { useState, useEffect } from 'react'
import { Activity, Cpu, Database, Wifi, Zap } from 'lucide-react'

const AgentStatusBar = ({ isActive, stage, analysisType }) => {
  const [systemStats, setSystemStats] = useState({
    cpu: 23,
    memory: 45,
    network: 98,
    database: 87,
    throughput: 0
  })

  useEffect(() => {
    if (!isActive) return

    const interval = setInterval(() => {
      setSystemStats(prev => ({
        cpu: Math.max(10, Math.min(90, prev.cpu + (Math.random() - 0.5) * 10)),
        memory: Math.max(20, Math.min(80, prev.memory + (Math.random() - 0.5) * 5)),
        network: Math.max(85, Math.min(100, prev.network + (Math.random() - 0.5) * 3)),
        database: Math.max(70, Math.min(95, prev.database + (Math.random() - 0.5) * 8)),
        throughput: Math.floor(Math.random() * 1000) + 500
      }))
    }, 1000)

    return () => clearInterval(interval)
  }, [isActive])

  const getStatusColor = (value, thresholds = { good: 80, warning: 60 }) => {
    if (value >= thresholds.good) return 'text-green-600 bg-green-100'
    if (value >= thresholds.warning) return 'text-yellow-600 bg-yellow-100'
    return 'text-red-600 bg-red-100'
  }

  const stageDescriptions = {
    initializing: 'Starting comprehensive compliance analysis...',
    legal_analysis: 'Running legal compliance analysis...',
    geo_mapping: 'Mapping geo-regulatory requirements...',
    audit_generation: 'Generating audit trail and evidence...',
    finalizing: 'Compiling comprehensive results...'
  }

  return (
    <div className="bg-gray-900 text-white rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Activity className={`w-5 h-5 ${isActive ? 'text-green-400 animate-pulse' : 'text-gray-400'}`} />
          <h4 className="font-semibold">System Monitor</h4>
          {analysisType === 'bulk' && (
            <span className="bg-blue-600 text-xs px-2 py-1 rounded-full">BULK MODE</span>
          )}
        </div>
        <div className="text-right">
          <div className={`text-xs ${isActive ? 'text-green-400' : 'text-gray-400'}`}>
            Status: {isActive ? 'ACTIVE' : 'IDLE'}
          </div>
          {isActive && (
            <div className="text-xs text-blue-400">
              {stageDescriptions[stage] || 'Processing...'}
            </div>
          )}
        </div>
      </div>

      {/* System Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="text-center">
          <div className="flex items-center justify-center mb-1">
            <Cpu className="w-4 h-4 mr-1" />
            <span className="text-xs font-medium">CPU</span>
          </div>
          <div className={`text-sm font-bold px-2 py-1 rounded ${getStatusColor(100 - systemStats.cpu)}`}>
            {Math.round(systemStats.cpu)}%
          </div>
        </div>

        <div className="text-center">
          <div className="flex items-center justify-center mb-1">
            <Database className="w-4 h-4 mr-1" />
            <span className="text-xs font-medium">MEM</span>
          </div>
          <div className={`text-sm font-bold px-2 py-1 rounded ${getStatusColor(100 - systemStats.memory)}`}>
            {Math.round(systemStats.memory)}%
          </div>
        </div>

        <div className="text-center">
          <div className="flex items-center justify-center mb-1">
            <Wifi className="w-4 h-4 mr-1" />
            <span className="text-xs font-medium">NET</span>
          </div>
          <div className={`text-sm font-bold px-2 py-1 rounded ${getStatusColor(systemStats.network)}`}>
            {Math.round(systemStats.network)}%
          </div>
        </div>

        <div className="text-center">
          <div className="flex items-center justify-center mb-1">
            <Database className="w-4 h-4 mr-1" />
            <span className="text-xs font-medium">DB</span>
          </div>
          <div className={`text-sm font-bold px-2 py-1 rounded ${getStatusColor(systemStats.database)}`}>
            {Math.round(systemStats.database)}%
          </div>
        </div>

        <div className="text-center">
          <div className="flex items-center justify-center mb-1">
            <Zap className="w-4 h-4 mr-1" />
            <span className="text-xs font-medium">OPS</span>
          </div>
          <div className="text-sm font-bold px-2 py-1 rounded bg-blue-100 text-blue-600">
            {systemStats.throughput}/s
          </div>
        </div>
      </div>

      {/* Processing Animation */}
      {isActive && (
        <div className="mt-4">
          <div className="flex items-center justify-between text-xs text-gray-400 mb-2">
            <span>Processing Pipeline</span>
            <span className="animate-pulse">●●●</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-blue-500 to-green-500 h-2 rounded-full transition-all duration-1000 animate-pulse"
              style={{ width: isActive ? '100%' : '0%' }}
            />
          </div>
        </div>
      )}

      {/* Fun Terminal-like Output */}
      {isActive && (
        <div className="mt-4 bg-black rounded p-2 font-mono text-xs">
          <div className="text-green-400">
            <span className="text-blue-400">$</span> analyzing_compliance --verbose
          </div>
          <div className="text-gray-300 animate-pulse">
            → {stageDescriptions[stage] || 'Processing request...'}
          </div>
          <div className="text-yellow-400">
            [INFO] Agents working at {Math.round(systemStats.throughput)} ops/sec
          </div>
        </div>
      )}
    </div>
  )
}

export default AgentStatusBar