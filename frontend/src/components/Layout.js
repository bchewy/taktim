import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Layout = ({ children }) => {
  const location = useLocation();

  const menuItems = [
    { path: '/', label: 'Dashboard', icon: '🏠' },
    { path: '/single-analysis', label: 'Single Analysis', icon: '🔍' },
    { path: '/bulk-analysis', label: 'Bulk Analysis', icon: '📊' },
    { path: '/results', label: 'Results', icon: '📋' },
    { path: '/alerts', label: 'Alerts', icon: '⚠️' },
    { path: '/settings', label: 'Settings', icon: '⚙️' }
  ];

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-blue-600 text-white p-4 shadow-lg">
        <div className="container mx-auto">
          <h1 className="text-2xl font-bold">TikTok Geo-Compliance Detection System</h1>
          <p className="text-blue-100">AI-powered regulatory compliance analysis</p>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <nav className="w-64 bg-white shadow-lg min-h-screen">
          <div className="p-4">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Navigation</h2>
            <ul className="space-y-2">
              {menuItems.map((item) => (
                <li key={item.path}>
                  <Link
                    to={item.path}
                    className={`flex items-center space-x-3 p-3 rounded-lg transition-colors ${
                      location.pathname === item.path
                        ? 'bg-blue-100 text-blue-600 font-medium'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <span className="text-lg">{item.icon}</span>
                    <span>{item.label}</span>
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </nav>

        {/* Main Content */}
        <main className="flex-1 p-6">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;