import React from 'react'
import { X, Bot, Search, Globe, FileText, Users, Zap } from 'lucide-react'

const AgentPersonalityModal = ({ agent, isOpen, onClose }) => {
  if (!isOpen || !agent) return null

  const agentProfiles = {
    legal_researcher: {
      name: 'Legal Research Agent',
      nickname: 'Lex the Legal Eagle',
      personality: 'Detail-oriented and thorough. Never misses a regulation!',
      expertise: ['Congress.gov API Integration', 'Federal Law Database', 'Government Citations'],
      quirks: ['Always double-checks sources', 'Speaks in legal jargon', 'Loves finding precedents'],
      funFact: 'Can process 1000+ legal documents per minute!',
      catchphrase: '"Let me dig deeper into the legal archives..."',
      icon: Search,
      color: 'blue'
    },
    geo_regulatory: {
      name: 'Geo-Regulatory Agent',
      nickname: 'Geo the Globe Trotter',
      personality: 'Worldly and comprehensive. Knows every jurisdiction!',
      expertise: ['Multi-Jurisdiction Analysis', 'GDPR Compliance', 'State-by-State Mapping'],
      quirks: ['Thinks in terms of geographic boundaries', 'Always considers international implications'],
      funFact: 'Knows compliance rules for 150+ countries!',
      catchphrase: '"From California to Canada, I\'ve got you covered!"',
      icon: Globe,
      color: 'green'
    },
    multimodal_crew: {
      name: 'Multimodal Crew Lead',
      nickname: 'Commander Crew',
      personality: 'Natural leader and coordinator. Brings everyone together!',
      expertise: ['Agent Orchestration', 'Workflow Management', 'Team Coordination'],
      quirks: ['Always thinking about the big picture', 'Great at delegation'],
      funFact: 'Can manage up to 50 agents simultaneously!',
      catchphrase: '"Alright team, let\'s make this happen!"',
      icon: Users,
      color: 'purple'
    },
    audit_trail: {
      name: 'Audit Trail Generator',
      nickname: 'Audit Andy',
      personality: 'Meticulous documentarian. Every detail matters!',
      expertise: ['Evidence Documentation', 'Regulatory Reports', 'Citation Management'],
      quirks: ['Obsessed with proper formatting', 'Never forgets a timestamp'],
      funFact: 'Has created over 10,000 audit trails with zero errors!',
      catchphrase: '"Documentation is the key to regulatory success!"',
      icon: FileText,
      color: 'orange'
    }
  }

  const profile = agentProfiles[agent.id] || {}
  const Icon = profile.icon || Bot
  
  const getColorClasses = (color) => {
    const colorMap = {
      blue: 'bg-blue-500 border-blue-600 text-white',
      green: 'bg-green-500 border-green-600 text-white',
      purple: 'bg-purple-500 border-purple-600 text-white',
      orange: 'bg-orange-500 border-orange-600 text-white'
    }
    return colorMap[color] || 'bg-gray-500 border-gray-600 text-white'
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
          <h2 className="text-xl font-bold text-gray-900">Agent Profile</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-500"
          >
            <X className="w-6 h-6" />
          </button>
        </div>
        
        <div className="p-6">
          {/* Agent Header */}
          <div className="flex items-center space-x-4 mb-6">
            <div className={`w-20 h-20 rounded-full border-4 flex items-center justify-center ${getColorClasses(profile.color)}`}>
              <Icon className="w-10 h-10" />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-gray-900">{profile.name}</h3>
              <p className="text-lg text-gray-600 italic">"{profile.nickname}"</p>
              <p className="text-sm text-gray-500 mt-1">{profile.personality}</p>
            </div>
          </div>

          {/* Catchphrase */}
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4 mb-6">
            <div className="flex items-center space-x-2 mb-2">
              <Zap className="w-5 h-5 text-purple-600" />
              <span className="font-semibold text-purple-800">Signature Catchphrase</span>
            </div>
            <p className="text-purple-700 italic text-lg">"{profile.catchphrase}"</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Expertise */}
            <div>
              <h4 className="font-semibold text-gray-900 mb-3">Core Expertise</h4>
              <div className="space-y-2">
                {profile.expertise?.map((skill, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-sm text-gray-700">{skill}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Quirks */}
            <div>
              <h4 className="font-semibold text-gray-900 mb-3">Agent Quirks</h4>
              <div className="space-y-2">
                {profile.quirks?.map((quirk, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                    <span className="text-sm text-gray-700">{quirk}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Fun Fact */}
          <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <span className="text-lg">🎉</span>
              <span className="font-semibold text-yellow-800">Fun Fact</span>
            </div>
            <p className="text-yellow-700">{profile.funFact}</p>
          </div>

          {/* Performance Stats (Mock) */}
          <div className="mt-6 grid grid-cols-3 gap-4">
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">99.8%</div>
              <div className="text-xs text-gray-600">Accuracy Rate</div>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">2.3s</div>
              <div className="text-xs text-gray-600">Avg Response</div>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">5,847</div>
              <div className="text-xs text-gray-600">Tasks Completed</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AgentPersonalityModal