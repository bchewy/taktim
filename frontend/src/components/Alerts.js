import React, { useState } from 'react';

const Alerts = () => {
  const [alerts] = useState([
    {
      id: 1,
      type: 'critical',
      title: 'High Risk Feature Detected',
      message: 'AI Teen Discovery Feed requires immediate compliance review',
      feature: 'AI Teen Discovery Feed',
      jurisdictions: ['US Federal', 'California', 'EU'],
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
      read: false
    },
    {
      id: 2,
      type: 'warning',
      title: 'New Regulation Update',
      message: 'California SB976 implementation deadline approaching',
      feature: null,
      jurisdictions: ['California'],
      timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(), // 6 hours ago
      read: false
    },
    {
      id: 3,
      type: 'info',
      title: 'Analysis Complete',
      message: 'Social Circle Suggestions analysis completed successfully',
      feature: 'Social Circle Suggestions',
      jurisdictions: ['US Federal'],
      timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(), // 1 day ago
      read: true
    }
  ]);

  const getAlertIcon = (type) => {
    switch (type) {
      case 'critical': return '🚨';
      case 'warning': return '⚠️';
      case 'info': return 'ℹ️';
      default: return '📋';
    }
  };

  const getAlertColor = (type) => {
    switch (type) {
      case 'critical': return 'border-red-200 bg-red-50';
      case 'warning': return 'border-yellow-200 bg-yellow-50';
      case 'info': return 'border-blue-200 bg-blue-50';
      default: return 'border-gray-200 bg-gray-50';
    }
  };

  const getAlertTextColor = (type) => {
    switch (type) {
      case 'critical': return 'text-red-800';
      case 'warning': return 'text-yellow-800';
      case 'info': return 'text-blue-800';
      default: return 'text-gray-800';
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = Math.floor((now - date) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours} hour${diffInHours > 1 ? 's' : ''} ago`;
    const diffInDays = Math.floor(diffInHours / 24);
    return `${diffInDays} day${diffInDays > 1 ? 's' : ''} ago`;
  };

  const unreadCount = alerts.filter(alert => !alert.read).length;
  const criticalCount = alerts.filter(alert => alert.type === 'critical').length;

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Compliance Alerts</h1>
        <p className="text-gray-600">Monitor regulatory compliance alerts and notifications</p>
      </div>

      {/* Alert Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Total Alerts</h3>
          <p className="text-3xl font-bold text-gray-600">{alerts.length}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Unread</h3>
          <p className="text-3xl font-bold text-orange-600">{unreadCount}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Critical</h3>
          <p className="text-3xl font-bold text-red-600">{criticalCount}</p>
        </div>
      </div>

      {/* Alert Filters */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="flex flex-wrap gap-2">
          <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
            All Alerts
          </button>
          <button className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors">
            Unread Only
          </button>
          <button className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors">
            Critical
          </button>
          <button className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors">
            Feature-Related
          </button>
        </div>
      </div>

      {/* Alerts List */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Recent Alerts</h2>
        </div>
        
        {alerts.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            <p>No alerts at this time.</p>
            <p className="text-sm mt-2">We'll notify you when compliance issues arise.</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {alerts.map((alert) => (
              <div
                key={alert.id}
                className={`p-4 border-l-4 ${getAlertColor(alert.type)} ${alert.read ? 'opacity-75' : ''}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3 flex-1">
                    <span className="text-2xl">{getAlertIcon(alert.type)}</span>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <h3 className={`font-semibold ${getAlertTextColor(alert.type)}`}>
                          {alert.title}
                        </h3>
                        {!alert.read && (
                          <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                        )}
                      </div>
                      
                      <p className={`mb-2 ${getAlertTextColor(alert.type)}`}>
                        {alert.message}
                      </p>
                      
                      <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
                        {alert.feature && (
                          <div className="flex items-center space-x-1">
                            <span className="font-medium">Feature:</span>
                            <span>{alert.feature}</span>
                          </div>
                        )}
                        
                        <div className="flex items-center space-x-1">
                          <span className="font-medium">Jurisdictions:</span>
                          <div className="flex space-x-1">
                            {alert.jurisdictions.map((jurisdiction, idx) => (
                              <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                                {jurisdiction}
                              </span>
                            ))}
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-1">
                          <span className="font-medium">Time:</span>
                          <span>{formatTime(alert.timestamp)}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2 ml-4">
                    <button className="text-blue-600 hover:text-blue-800 text-sm">
                      View Details
                    </button>
                    {!alert.read && (
                      <button className="text-gray-600 hover:text-gray-800 text-sm">
                        Mark Read
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Alert Configuration */}
      <div className="mt-8 bg-white p-6 rounded-lg shadow">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Alert Configuration</h2>
        <p className="text-gray-600 mb-4">Configure when and how you receive compliance alerts</p>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium text-gray-900">Critical Risk Features</h3>
              <p className="text-sm text-gray-600">Get immediate alerts for high and critical risk features</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" defaultChecked />
              <div className="w-11 h-6 bg-gray-200 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium text-gray-900">Regulation Updates</h3>
              <p className="text-sm text-gray-600">Receive notifications when regulations change</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" defaultChecked />
              <div className="w-11 h-6 bg-gray-200 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium text-gray-900">Analysis Completion</h3>
              <p className="text-sm text-gray-600">Get notified when feature analyses complete</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" />
              <div className="w-11 h-6 bg-gray-200 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Alerts;