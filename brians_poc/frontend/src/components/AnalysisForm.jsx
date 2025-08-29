import React, { useState } from 'react'
import { Loader2, Send } from 'lucide-react'

const AnalysisForm = ({ onAnalyze, loading }) => {
  const [formData, setFormData] = useState({
    feature_id: '',
    title: '',
    description: '',
    docs: '',
    code_hints: '',
    tags: ''
  })

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    
    // Convert string inputs to arrays
    const processedData = {
      ...formData,
      docs: formData.docs ? formData.docs.split(',').map(s => s.trim()).filter(s => s) : [],
      code_hints: formData.code_hints ? formData.code_hints.split(',').map(s => s.trim()).filter(s => s) : [],
      tags: formData.tags ? formData.tags.split(',').map(s => s.trim()).filter(s => s) : []
    }
    
    onAnalyze(processedData)
  }

  const loadExample = () => {
    setFormData({
      feature_id: 'personalized_recommendations',
      title: 'Personalized Content Recommendations',
      description: 'AI-driven system that analyzes user behavior to recommend personalized content feeds and ranking algorithms for social media posts',
      docs: 'User preferences API, Content ranking system, Privacy policy',
      code_hints: 'recommendation_engine.py, user_profiling.js, content_ranker.ts',
      tags: 'personalization, recommendations, AI, machine-learning'
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label htmlFor="feature_id" className="block text-sm font-medium text-gray-700 mb-1">
          Feature ID *
        </label>
        <input
          type="text"
          id="feature_id"
          name="feature_id"
          required
          value={formData.feature_id}
          onChange={handleInputChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="e.g., user_recommendations"
        />
      </div>

      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
          Feature Title *
        </label>
        <input
          type="text"
          id="title"
          name="title"
          required
          value={formData.title}
          onChange={handleInputChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="e.g., Personalized Content Recommendations"
        />
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
          Description *
        </label>
        <textarea
          id="description"
          name="description"
          required
          rows={3}
          value={formData.description}
          onChange={handleInputChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Detailed description of the feature functionality..."
        />
      </div>

      <div>
        <label htmlFor="docs" className="block text-sm font-medium text-gray-700 mb-1">
          Documentation (comma-separated)
        </label>
        <input
          type="text"
          id="docs"
          name="docs"
          value={formData.docs}
          onChange={handleInputChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="e.g., API docs, User guide, Technical specs"
        />
      </div>

      <div>
        <label htmlFor="code_hints" className="block text-sm font-medium text-gray-700 mb-1">
          Code Hints (comma-separated)
        </label>
        <input
          type="text"
          id="code_hints"
          name="code_hints"
          value={formData.code_hints}
          onChange={handleInputChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="e.g., recommend.py, user_profile.js"
        />
      </div>

      <div>
        <label htmlFor="tags" className="block text-sm font-medium text-gray-700 mb-1">
          Tags (comma-separated)
        </label>
        <input
          type="text"
          id="tags"
          name="tags"
          value={formData.tags}
          onChange={handleInputChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="e.g., personalization, AI, recommendations"
        />
      </div>

      <div className="flex space-x-3">
        <button
          type="submit"
          disabled={loading}
          className="flex-1 inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          {loading ? (
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
          ) : (
            <Send className="w-4 h-4 mr-2" />
          )}
          {loading ? 'Analyzing...' : 'Analyze Feature'}
        </button>

        <button
          type="button"
          onClick={loadExample}
          className="px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Load Example
        </button>
      </div>
    </form>
  )
}

export default AnalysisForm