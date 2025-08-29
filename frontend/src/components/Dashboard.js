import React from 'react';
import { Link } from 'react-router-dom';

const Dashboard = () => {
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
        <p className="text-gray-600">Overview of geo-compliance detection system</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Total Features Analyzed</h3>
          <p className="text-3xl font-bold text-blue-600">0</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">High Risk Detected</h3>
          <p className="text-3xl font-bold text-red-600">0</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Jurisdictions Covered</h3>
          <p className="text-3xl font-bold text-green-600">5</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Audit Trails Generated</h3>
          <p className="text-3xl font-bold text-purple-600">0</p>
        </div>
      </div>

      {/* System Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">System Capabilities</h2>
          <ul className="space-y-3">
            <li className="flex items-center space-x-3">
              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              <span>Legal Knowledge Agent (Government APIs)</span>
            </li>
            <li className="flex items-center space-x-3">
              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              <span>Geo-Regulatory Mapping (Multi-jurisdiction)</span>
            </li>
            <li className="flex items-center space-x-3">
              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              <span>Audit Trail Generation</span>
            </li>
            <li className="flex items-center space-x-3">
              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              <span>Real-time Government Data Integration</span>
            </li>
          </ul>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="space-y-4">
            <Link 
              to="/single-analysis" 
              className="block w-full bg-blue-600 text-white text-center py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Start Single Feature Analysis
            </Link>
            <Link 
              to="/bulk-analysis" 
              className="block w-full bg-green-600 text-white text-center py-3 px-4 rounded-lg hover:bg-green-700 transition-colors"
            >
              Bulk Feature Analysis
            </Link>
            <Link 
              to="/results" 
              className="block w-full bg-purple-600 text-white text-center py-3 px-4 rounded-lg hover:bg-purple-700 transition-colors"
            >
              View Analysis Results
            </Link>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="mt-8 bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Activity</h2>
        <div className="text-center text-gray-500 py-8">
          <p>No recent activity. Start by analyzing a TikTok feature for compliance.</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;