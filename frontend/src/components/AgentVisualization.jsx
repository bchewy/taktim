import React, { useState, useEffect } from 'react'
import { Bot, Search, Globe, FileText, Zap, CheckCircle, AlertTriangle, ArrowRight, Users, Database, Brain } from 'lucide-react'
import AgentPersonalityModal from './AgentPersonalityModal'
import AgentStatusBar from './AgentStatusBar'

const AgentVisualization = ({ isActive, stage, analysisType = 'single', validationData = null }) => {
  const [activeAgent, setActiveAgent] = useState(null)
  const [connections, setConnections] = useState([])
  const [messages, setMessages] = useState([])
  const [selectedAgent, setSelectedAgent] = useState(null)
  const [showPersonality, setShowPersonality] = useState(false)
  const [apiStatus, setApiStatus] = useState({})

  // Define our agents based on your multimodal backend
  const agents = {
    legal_researcher: {
      id: 'legal_researcher',
      name: 'Legal Research Agent',
      icon: Search,
      color: 'blue',
      position: { x: 15, y: 15 },
      personality: '🕵️ "Time to dig into Congress.gov!"',
      role: 'Government API Integration'
    },
    geo_regulatory: {
      id: 'geo_regulatory',
      name: 'Geo-Regulatory Agent',
      icon: Globe,
      color: 'green',
      position: { x: 50, y: 60 },
      personality: '🌍 "Let me check jurisdictions..."',
      role: 'Multi-jurisdiction Mapping'
    },
    multimodal_crew: {
      id: 'multimodal_crew',
      name: 'Multimodal Crew Lead',
      icon: Users,
      color: 'purple',
      position: { x: 50, y: 15 },
      personality: '🎯 "Coordinating the team!"',
      role: 'Agent Orchestration'
    },
    chat_agent: {
      id: 'chat_agent',
      name: 'Chat Agent',
      icon: Bot,
      color: 'indigo',
      position: { x: 85, y: 35 },
      personality: '💬 "Ready to chat with users!"',
      role: 'User Interaction'
    },
    audit_trail: {
      id: 'audit_trail',
      name: 'Audit Trail Generator',
      icon: FileText,
      color: 'orange',
      position: { x: 15, y: 60 },
      personality: '📋 "Creating evidence trail..."',
      role: 'Regulatory Documentation'
    }
  }

  // Stage to agent mapping - Based on actual backend flow
  const stageAgentMap = {
    'initializing': ['multimodal_crew'],
    'legal_analysis': ['legal_researcher'], // analyze_legal_compliance() 
    'geo_mapping': ['geo_regulatory'], // geo_compliance_mapping_tool()
    'audit_generation': ['audit_trail'], // _determine_overall_compliance_status()
    'finalizing': ['multimodal_crew', 'audit_trail'] // Return comprehensive result
  }

  // Enhanced agent messages with API validation status
  const agentMessages = {
    legal_researcher: [
      "🔍 Starting legal compliance analysis...",
      "📡 Calling GovInfo API...",
      "📡 Accessing Congress.gov...", 
      "⚖️ Assessing regulatory concerns...",
      "📊 Generating risk level assessment...",
      "✅ Legal analysis completed!"
    ],
    geo_regulatory: [
      "🌍 Initializing geo-compliance mapping...",
      "🗺️ Parsing target markets and features...",
      "📍 Mapping jurisdiction requirements...",
      "⚠️ Assessing compliance risk levels...",
      "🎯 Generating compliance requirements..."
    ],
    multimodal_crew: [
      "🎯 Starting comprehensive analysis...",
      "🔧 Initializing CrewAI agents...",
      "🤖 Orchestrating multimodal workflow...",
      "📊 Combining analysis results...",
      "✅ Analysis coordination complete!"
    ],
    audit_trail: [
      "📝 Determining overall compliance status...",
      "🔍 Extracting risk indicators...",
      "⚖️ Evaluating legal and geo concerns...",
      "📋 Generating audit-ready documentation...",
      "✅ Evidence trail completed!"
    ]
  }

  // API status tracking
  const getAPIStatusMessage = (apiName, status) => {
    const icons = {
      calling: '⏳',
      success: '✅', 
      failed: '❌',
      timeout: '⏱️'
    }
    
    const messages = {
      calling: `${icons.calling} Calling ${apiName}...`,
      success: `${icons.success} ${apiName}: Retrieved successfully`,
      failed: `${icons.failed} ${apiName}: Connection failed`,
      timeout: `${icons.timeout} ${apiName}: Request timed out`
    }
    
    return messages[status] || `📡 ${apiName}: ${status}`
  }

  // Update API status when validation data changes
  useEffect(() => {
    if (validationData && validationData.api_calls_summary) {
      const newStatus = {}
      validationData.api_details?.forEach(call => {
        newStatus[call.api_name] = {
          status: call.status,
          result_count: call.result_count,
          response_time: call.response_time_ms,
          error: call.error_message
        }
      })
      setApiStatus(newStatus)
    }
  }, [validationData])

  useEffect(() => {
    if (!isActive) return

    const activeAgents = stageAgentMap[stage] || []
    if (activeAgents.length > 0) {
      setActiveAgent(activeAgents[0])
      
      // Create connections between active agents
      const newConnections = []
      for (let i = 0; i < activeAgents.length - 1; i++) {
        newConnections.push({
          from: activeAgents[i],
          to: activeAgents[i + 1]
        })
      }
      setConnections(newConnections)

      // Add agent message with API status integration
      const agent = activeAgents[0]
      
      // Check if this is a legal research stage and we have API status
      if (agent === 'legal_researcher' && Object.keys(apiStatus).length > 0) {
        // Show API-specific status messages
        Object.entries(apiStatus).forEach(([apiName, status]) => {
          const statusMessage = getAPIStatusMessage(apiName, status.status)
          const detailMessage = status.status === 'success' && status.result_count !== undefined
            ? `${statusMessage} (${status.result_count} results in ${status.response_time?.toFixed(0)}ms)`
            : statusMessage

          setMessages(prev => [...prev.slice(-3), {
            id: `${Date.now()}-${apiName}-${Math.random()}`,
            agent: agent,
            message: detailMessage,
            timestamp: new Date(),
            apiCall: true,
            apiStatus: status.status
          }])
        })
      } else {
        // Default message behavior
        const agentMsgs = agentMessages[agent] || []
        const randomMsg = agentMsgs[Math.floor(Math.random() * agentMsgs.length)]
        
        setMessages(prev => [...prev.slice(-2), {
          id: `${Date.now()}-${Math.random()}`,
          agent: agent,
          message: randomMsg,
          timestamp: new Date()
        }])
      }
    }
  }, [stage, isActive, apiStatus])

  const getAgentColorClasses = (color) => {
    const colorMap = {
      blue: 'bg-blue-100 border-blue-300 text-blue-800',
      green: 'bg-green-100 border-green-300 text-green-800',
      purple: 'bg-purple-100 border-purple-300 text-purple-800',
      indigo: 'bg-indigo-100 border-indigo-300 text-indigo-800',
      orange: 'bg-orange-100 border-orange-300 text-orange-800'
    }
    return colorMap[color] || 'bg-gray-100 border-gray-300 text-gray-800'
  }

  const getActiveAgentClasses = (agentId) => {
    const isCurrentlyActive = stageAgentMap[stage]?.includes(agentId)
    if (isCurrentlyActive) {
      return 'ring-4 ring-yellow-300 scale-110 animate-pulse'
    }
    return ''
  }

  const handleAgentClick = (agent) => {
    setSelectedAgent(agent)
    setShowPersonality(true)
  }

  return (
    <div className="space-y-4">
      <div className="bg-gradient-to-br from-slate-50 to-blue-50 rounded-lg p-6 border border-gray-200">
        <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Brain className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">
            Agent Collaboration {analysisType === 'bulk' ? '(Bulk Mode)' : ''}
          </h3>
        </div>
        {isActive && (
          <div className="flex items-center space-x-2 text-sm text-green-600">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span>Agents Active</span>
          </div>
        )}
      </div>

      {/* Agent Network Visualization */}
      <div className="relative h-[500px] bg-white rounded-lg border border-gray-200 mb-4 overflow-hidden">
        {/* Connection Lines */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none">
          {connections.map((conn, index) => {
            const fromAgent = agents[conn.from]
            const toAgent = agents[conn.to]
            return (
              <line
                key={index}
                x1={`${fromAgent.position.x}%`}
                y1={`${fromAgent.position.y}%`}
                x2={`${toAgent.position.x}%`}
                y2={`${toAgent.position.y}%`}
                stroke="#3B82F6"
                strokeWidth="2"
                strokeDasharray="5,5"
                className="animate-pulse"
              />
            )
          })}
        </svg>

        {/* Agent Nodes */}
        {Object.values(agents).map((agent) => {
          const Icon = agent.icon
          return (
            <div
              key={agent.id}
              className={`absolute transform -translate-x-1/2 -translate-y-1/2 transition-all duration-300 ${getActiveAgentClasses(agent.id)}`}
              style={{ left: `${agent.position.x}%`, top: `${agent.position.y}%` }}
            >
              <div 
                className={`w-16 h-16 rounded-full border-2 flex items-center justify-center cursor-pointer transition-all duration-200 hover:scale-105 ${getAgentColorClasses(agent.color)}`}
                onClick={() => handleAgentClick(agent)}
                title={`Click to learn more about ${agent.name}`}
              >
                <Icon className="w-8 h-8" />
              </div>
              <div className="absolute top-full left-1/2 transform -translate-x-1/2 mt-6 text-center min-w-36 max-w-40">
                <div className="text-xs font-medium text-gray-900 whitespace-nowrap">
                  {agent.name}
                </div>
                <div className="text-xs text-gray-500 whitespace-nowrap mb-1">
                  {agent.role}
                </div>
                {stageAgentMap[stage]?.includes(agent.id) && (
                  <div className="text-xs font-medium text-blue-600 mt-3 animate-bounce bg-blue-50 px-2 py-1 rounded-md border border-blue-200 shadow-sm">
                    {agent.personality}
                  </div>
                )}
              </div>
            </div>
          )
        })}

        {/* Data Flow Animation */}
        {isActive && connections.length > 0 && (
          <div className="absolute inset-0 pointer-events-none">
            {connections.map((conn, index) => {
              const fromAgent = agents[conn.from]
              const toAgent = agents[conn.to]
              return (
                <div
                  key={`flow-${index}`}
                  className="absolute w-3 h-3 bg-blue-500 rounded-full animate-ping"
                  style={{
                    left: `${(fromAgent.position.x + toAgent.position.x) / 2}%`,
                    top: `${(fromAgent.position.y + toAgent.position.y) / 2}%`,
                    animationDelay: `${index * 0.5}s`
                  }}
                />
              )
            })}
          </div>
        )}
      </div>

      {/* Agent Chat Feed */}
      <div className="space-y-3">
        <div className="flex items-center space-x-2">
          <Database className="w-4 h-4 text-gray-500" />
          <h4 className="text-sm font-medium text-gray-700">Agent Communication</h4>
        </div>
        
        <div className="bg-gray-50 rounded-lg p-3 h-24 overflow-y-auto">
          {messages.length === 0 ? (
            <p className="text-xs text-gray-500 italic">
              {isActive ? 'Agents are starting up...' : 'Click "Analyze" to see agents in action!'}
            </p>
          ) : (
            <div className="space-y-2">
              {messages.map((msg) => {
                const agent = agents[msg.agent]
                return (
                  <div key={msg.id} className="flex items-start space-x-2">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${getAgentColorClasses(agent.color)}`}>
                      <agent.icon className="w-3 h-3" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        <span className="text-xs font-medium text-gray-900 truncate">
                          {agent.name}
                        </span>
                        <span className="text-xs text-gray-500">
                          {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                        {msg.apiCall && (
                          <span className={`text-xs px-1.5 py-0.5 rounded-full text-white font-medium ${
                            msg.apiStatus === 'success' ? 'bg-green-500' : 
                            msg.apiStatus === 'failed' ? 'bg-red-500' : 
                            'bg-yellow-500'
                          }`}>
                            API
                          </span>
                        )}
                      </div>
                      <p className={`text-xs mt-1 ${
                        msg.apiCall && msg.apiStatus === 'success' ? 'text-green-700' :
                        msg.apiCall && msg.apiStatus === 'failed' ? 'text-red-700' :
                        'text-gray-600'
                      }`}>
                        {msg.message}
                      </p>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>

      {/* Stage Progress */}
      {isActive && (
        <div className="mt-4 pt-3 border-t border-gray-200">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Current Stage: <strong>{stage?.replace('_', ' ').toUpperCase()}</strong></span>
            <div className="flex items-center space-x-1">
              {stageAgentMap[stage]?.map((agentId, index) => {
                const agent = agents[agentId]
                const Icon = agent.icon
                return (
                  <div key={agentId} className={`w-6 h-6 rounded-full flex items-center justify-center ${getAgentColorClasses(agent.color)} animate-pulse`}>
                    <Icon className="w-3 h-3" />
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      )}
      </div>

      {/* System Status Bar */}
      <AgentStatusBar 
        isActive={isActive} 
        stage={stage} 
        analysisType={analysisType} 
      />

      {/* Agent Personality Modal */}
      <AgentPersonalityModal 
        agent={selectedAgent} 
        isOpen={showPersonality} 
        onClose={() => setShowPersonality(false)} 
      />
    </div>
  )
}

export default AgentVisualization