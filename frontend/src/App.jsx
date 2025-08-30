import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  ShieldCheckIcon, 
  Cog6ToothIcon,
  BellIcon,
  MoonIcon,
  SunIcon,
  MagnifyingGlassIcon,
  ArrowRightIcon,
  Square3Stack3DIcon,
  BeakerIcon,
  PlusCircleIcon,
  ChevronRightIcon,
  HomeIcon,
  CpuChipIcon,
  DocumentTextIcon,
  ArrowPathIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline'
import SingleAnalysis from './components/SingleAnalysis'
import BulkAnalyze from './components/BulkAnalyze'
import Dashboard from './components/Dashboard'
import clsx from 'clsx'

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard')
  const [darkMode, setDarkMode] = useState(false)
  const [searchOpen, setSearchOpen] = useState(false)
  const [notifications] = useState(3)

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [darkMode])

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setSearchOpen(true)
      }
      if (e.key === 'Escape') {
        setSearchOpen(false)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  const navigation = [
    { 
      name: 'Dashboard', 
      icon: HomeIcon, 
      page: 'dashboard',
      description: 'Overview & Analytics'
    },
    { 
      name: 'Feature Analysis', 
      icon: CpuChipIcon, 
      page: 'analysis',
      description: 'Single Feature Compliance'
    },
    { 
      name: 'Bulk Processing', 
      icon: Square3Stack3DIcon, 
      page: 'bulk',
      description: 'Batch Analysis'
    },
    { 
      name: 'Audit Trail', 
      icon: DocumentTextIcon, 
      page: 'audit',
      description: 'Compliance Records'
    },
  ]

  const renderPage = () => {
    switch(currentPage) {
      case 'dashboard':
        return <Dashboard darkMode={darkMode} onNavigate={setCurrentPage} />
      case 'analysis':
        return <SingleAnalysis darkMode={darkMode} />
      case 'bulk':
        return <BulkAnalyze darkMode={darkMode} />
      case 'audit':
        return (
          <div className="flex items-center justify-center min-h-[60vh]">
            <div className="text-center max-w-2xl mx-auto">
              <div className={clsx(
                'w-24 h-24 rounded-2xl mx-auto mb-6 flex items-center justify-center',
                darkMode 
                  ? 'bg-slate-800' 
                  : 'bg-slate-100'
              )}>
                <DocumentTextIcon className={clsx(
                  'w-12 h-12',
                  darkMode ? 'text-slate-400' : 'text-slate-600'
                )} />
              </div>
              <h2 className={clsx(
                'text-3xl font-semibold mb-3',
                darkMode ? 'text-white' : 'text-gray-900'
              )}>
                Audit Trail System
              </h2>
              <p className={clsx(
                'text-base mb-8',
                darkMode ? 'text-gray-400' : 'text-gray-600'
              )}>
                Complete regulatory compliance documentation with timestamped audit logs, 
                evidence trails, and regulatory inquiry response systems.
              </p>
              <div className="flex items-center justify-center space-x-4">
                <button className={clsx(
                  'px-6 py-2.5 rounded-lg font-medium transition-all border',
                  darkMode 
                    ? 'border-slate-700 text-slate-300 hover:bg-slate-800' 
                    : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                )}>
                  View Documentation
                </button>
                <button className={clsx(
                  'px-6 py-2.5 rounded-lg font-medium transition-all',
                  'bg-blue-600 text-white hover:bg-blue-700'
                )}>
                  Generate Report
                </button>
              </div>
            </div>
          </div>
        )
      default:
        return null
    }
  }

  return (
    <div className={clsx(
      'min-h-screen transition-colors duration-200',
      darkMode 
        ? 'bg-slate-900' 
        : 'bg-white'
    )}>
      {/* Main Navigation Header */}
      <header className={clsx(
        'fixed top-0 left-0 right-0 z-50 border-b',
        darkMode 
          ? 'bg-slate-900/95 border-slate-800 backdrop-blur-sm' 
          : 'bg-white/95 border-gray-200 backdrop-blur-sm'
      )}>
        <div className="px-4 lg:px-6 h-16 flex items-center justify-between">
          {/* Left Section */}
          <div className="flex items-center space-x-8">
            {/* Logo */}
            <div className="flex items-center space-x-3">
              <div className={clsx(
                'w-9 h-9 rounded-lg flex items-center justify-center',
                'bg-blue-600'
              )}>
                <ShieldCheckIcon className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className={clsx(
                  'text-base font-semibold leading-tight',
                  darkMode ? 'text-white' : 'text-gray-900'
                )}>
                  Compliance Suite
                </h1>
                <p className={clsx(
                  'text-xs',
                  darkMode ? 'text-slate-500' : 'text-gray-500'
                )}>
                  TikTok Enterprise
                </p>
              </div>
            </div>

            {/* Main Navigation */}
            <nav className="hidden lg:flex items-center space-x-1">
              {navigation.map((item) => {
                const isActive = currentPage === item.page
                return (
                  <button
                    key={item.name}
                    onClick={() => setCurrentPage(item.page)}
                    className={clsx(
                      'px-3 py-2 rounded-lg text-sm font-medium transition-all duration-150',
                      isActive 
                        ? darkMode 
                          ? 'bg-slate-800 text-white' 
                          : 'bg-gray-100 text-gray-900'
                        : darkMode
                          ? 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                          : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    )}
                  >
                    {item.name}
                  </button>
                )
              })}
            </nav>
          </div>

          {/* Right Section */}
          <div className="flex items-center space-x-4">
            {/* Search */}
            <button
              onClick={() => setSearchOpen(true)}
              className={clsx(
                'hidden lg:flex items-center space-x-2 px-3 py-1.5 rounded-lg text-sm transition-all',
                darkMode 
                  ? 'bg-slate-800 text-slate-400 hover:text-slate-300' 
                  : 'bg-gray-100 text-gray-500 hover:text-gray-700'
              )}
            >
              <MagnifyingGlassIcon className="w-4 h-4" />
              <span>Search</span>
              <kbd className={clsx(
                'px-1.5 py-0.5 text-xs rounded border',
                darkMode 
                  ? 'bg-slate-700 border-slate-600 text-slate-400' 
                  : 'bg-white border-gray-300 text-gray-500'
              )}>
                ⌘K
              </kbd>
            </button>

            {/* Status Indicator */}
            <div className={clsx(
              'hidden lg:flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium',
              darkMode 
                ? 'bg-emerald-900/20 text-emerald-400' 
                : 'bg-emerald-50 text-emerald-600'
            )}>
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <span>All Systems Operational</span>
            </div>

            {/* Actions */}
            <div className="flex items-center space-x-2">
              <button className={clsx(
                'relative p-2 rounded-lg transition-colors',
                darkMode 
                  ? 'hover:bg-slate-800 text-slate-400' 
                  : 'hover:bg-gray-100 text-gray-600'
              )}>
                <BellIcon className="w-5 h-5" />
                {notifications > 0 && (
                  <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />
                )}
              </button>

              <button className={clsx(
                'p-2 rounded-lg transition-colors',
                darkMode 
                  ? 'hover:bg-slate-800 text-slate-400' 
                  : 'hover:bg-gray-100 text-gray-600'
              )}>
                <Cog6ToothIcon className="w-5 h-5" />
              </button>

              <button
                onClick={() => setDarkMode(!darkMode)}
                className={clsx(
                  'p-2 rounded-lg transition-colors',
                  darkMode 
                    ? 'hover:bg-slate-800 text-slate-400' 
                    : 'hover:bg-gray-100 text-gray-600'
                )}
              >
                {darkMode ? (
                  <SunIcon className="w-5 h-5" />
                ) : (
                  <MoonIcon className="w-5 h-5" />
                )}
              </button>

              {/* User Profile */}
              <div className={clsx(
                'flex items-center space-x-3 pl-3 ml-3 border-l',
                darkMode ? 'border-slate-800' : 'border-gray-200'
              )}>
                <div className="hidden lg:block text-right">
                  <p className={clsx(
                    'text-sm font-medium',
                    darkMode ? 'text-slate-200' : 'text-gray-900'
                  )}>
                    Admin User
                  </p>
                  <p className={clsx(
                    'text-xs',
                    darkMode ? 'text-slate-500' : 'text-gray-500'
                  )}>
                    admin@tiktok.com
                  </p>
                </div>
                <div className={clsx(
                  'w-9 h-9 rounded-lg flex items-center justify-center text-sm font-medium',
                  darkMode 
                    ? 'bg-slate-700 text-slate-300' 
                    : 'bg-gray-200 text-gray-700'
                )}>
                  AU
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Secondary Navigation Bar */}
        <div className={clsx(
          'px-4 lg:px-6 h-12 flex items-center justify-between border-t',
          darkMode 
            ? 'bg-slate-800/50 border-slate-800' 
            : 'bg-gray-50 border-gray-200'
        )}>
          <div className="flex items-center space-x-6">
            {/* Breadcrumb */}
            <div className="flex items-center space-x-2 text-sm">
              <span className={clsx(
                darkMode ? 'text-slate-500' : 'text-gray-500'
              )}>
                Home
              </span>
              <ChevronRightIcon className={clsx(
                'w-3 h-3',
                darkMode ? 'text-slate-600' : 'text-gray-400'
              )} />
              <span className={clsx(
                'font-medium',
                darkMode ? 'text-slate-300' : 'text-gray-700'
              )}>
                {navigation.find(item => item.page === currentPage)?.name}
              </span>
            </div>

            {/* Quick Stats */}
            <div className="hidden lg:flex items-center space-x-4 text-xs">
              <div className="flex items-center space-x-1.5">
                <span className={clsx(
                  darkMode ? 'text-slate-500' : 'text-gray-500'
                )}>
                  Total Analyses:
                </span>
                <span className={clsx(
                  'font-semibold',
                  darkMode ? 'text-slate-300' : 'text-gray-700'
                )}>
                  1,247
                </span>
              </div>
              <div className="flex items-center space-x-1.5">
                <span className={clsx(
                  darkMode ? 'text-slate-500' : 'text-gray-500'
                )}>
                  Compliance Rate:
                </span>
                <span className={clsx(
                  'font-semibold',
                  darkMode ? 'text-emerald-400' : 'text-emerald-600'
                )}>
                  94.7%
                </span>
              </div>
              <div className="flex items-center space-x-1.5">
                <span className={clsx(
                  darkMode ? 'text-slate-500' : 'text-gray-500'
                )}>
                  Active Jurisdictions:
                </span>
                <span className={clsx(
                  'font-semibold',
                  darkMode ? 'text-slate-300' : 'text-gray-700'
                )}>
                  42
                </span>
              </div>
            </div>
          </div>

          {/* Page Actions */}
          <div className="flex items-center space-x-3">
            {currentPage === 'dashboard' && (
              <>
                <button className={clsx(
                  'flex items-center space-x-1.5 px-3 py-1.5 text-sm rounded-lg transition-all',
                  darkMode 
                    ? 'text-slate-400 hover:text-slate-300' 
                    : 'text-gray-600 hover:text-gray-900'
                )}>
                  <ArrowPathIcon className="w-4 h-4" />
                  <span>Refresh</span>
                </button>
                <button className={clsx(
                  'flex items-center space-x-1.5 px-3 py-1.5 text-sm rounded-lg transition-all',
                  'bg-blue-600 text-white hover:bg-blue-700'
                )}>
                  <PlusCircleIcon className="w-4 h-4" />
                  <span>New Analysis</span>
                </button>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Sidebar Navigation - Desktop */}
      <aside className={clsx(
        'fixed left-0 top-28 bottom-0 w-64 border-r overflow-y-auto hidden lg:block',
        darkMode 
          ? 'bg-slate-900 border-slate-800' 
          : 'bg-white border-gray-200'
      )}>
        <div className="p-4">
          {/* Navigation Items with Descriptions */}
          <div className="space-y-1">
            {navigation.map((item) => {
              const isActive = currentPage === item.page
              return (
                <button
                  key={item.name}
                  onClick={() => setCurrentPage(item.page)}
                  className={clsx(
                    'w-full flex items-start space-x-3 px-3 py-2.5 rounded-lg transition-all',
                    isActive 
                      ? darkMode 
                        ? 'bg-blue-600/10 text-blue-400 border border-blue-600/20' 
                        : 'bg-blue-50 text-blue-600 border border-blue-200'
                      : darkMode
                        ? 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-300'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  )}
                >
                  <item.icon className={clsx(
                    'w-5 h-5 mt-0.5 flex-shrink-0',
                    isActive 
                      ? darkMode ? 'text-blue-400' : 'text-blue-600'
                      : ''
                  )} />
                  <div className="text-left">
                    <p className="text-sm font-medium">
                      {item.name}
                    </p>
                    <p className={clsx(
                      'text-xs mt-0.5',
                      isActive
                        ? darkMode ? 'text-blue-400/70' : 'text-blue-600/70'
                        : darkMode 
                          ? 'text-slate-600' 
                          : 'text-gray-500'
                    )}>
                      {item.description}
                    </p>
                  </div>
                </button>
              )
            })}
          </div>

          {/* Divider */}
          <div className={clsx(
            'my-4 border-t',
            darkMode ? 'border-slate-800' : 'border-gray-200'
          )} />

          {/* Quick Links */}
          <div className="space-y-1">
            <p className={clsx(
              'px-3 py-2 text-xs font-semibold uppercase tracking-wider',
              darkMode ? 'text-slate-600' : 'text-gray-400'
            )}>
              Quick Links
            </p>
            <button className={clsx(
              'w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-sm transition-all text-left',
              darkMode
                ? 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-300'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            )}>
              <DocumentTextIcon className="w-4 h-4" />
              <span>Documentation</span>
            </button>
            <button className={clsx(
              'w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-sm transition-all text-left',
              darkMode
                ? 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-300'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            )}>
              <BeakerIcon className="w-4 h-4" />
              <span>API Reference</span>
            </button>
          </div>

          {/* System Info */}
          <div className={clsx(
            'mt-6 p-3 rounded-lg',
            darkMode 
              ? 'bg-slate-800/50' 
              : 'bg-gray-50'
          )}>
            <div className="flex items-center justify-between mb-2">
              <span className={clsx(
                'text-xs font-semibold',
                darkMode ? 'text-slate-400' : 'text-gray-600'
              )}>
                System Status
              </span>
              <CheckCircleIcon className="w-4 h-4 text-emerald-500" />
            </div>
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className={clsx(
                  darkMode ? 'text-slate-500' : 'text-gray-500'
                )}>
                  API Response
                </span>
                <span className={clsx(
                  'font-medium',
                  darkMode ? 'text-slate-300' : 'text-gray-700'
                )}>
                  124ms
                </span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className={clsx(
                  darkMode ? 'text-slate-500' : 'text-gray-500'
                )}>
                  Uptime
                </span>
                <span className={clsx(
                  'font-medium',
                  darkMode ? 'text-slate-300' : 'text-gray-700'
                )}>
                  99.9%
                </span>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className={clsx(
        'pt-28 min-h-screen',
        'lg:pl-64'
      )}>
        <div className="px-4 lg:px-6 py-6">
          {/* Page Header */}
          <div className="mb-6">
            <h1 className={clsx(
              'text-2xl font-bold mb-1',
              darkMode ? 'text-white' : 'text-gray-900'
            )}>
              {navigation.find(item => item.page === currentPage)?.name}
            </h1>
            <p className={clsx(
              'text-sm',
              darkMode ? 'text-slate-400' : 'text-gray-600'
            )}>
              {currentPage === 'dashboard' && 'Monitor compliance metrics and system performance across all jurisdictions'}
              {currentPage === 'analysis' && 'Analyze individual features for regulatory compliance requirements'}
              {currentPage === 'bulk' && 'Process multiple features simultaneously for batch compliance analysis'}
              {currentPage === 'audit' && 'Access comprehensive audit trails and compliance documentation'}
            </p>
          </div>

          {/* Page Content */}
          <AnimatePresence mode="wait">
            <motion.div
              key={currentPage}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.15 }}
            >
              {renderPage()}
            </motion.div>
          </AnimatePresence>
        </div>
      </main>

      {/* Search Modal */}
      <AnimatePresence>
        {searchOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSearchOpen(false)}
              className="fixed inset-0 bg-black/50 z-50"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="fixed top-20 left-1/2 transform -translate-x-1/2 z-50 w-full max-w-2xl"
            >
              <div className={clsx(
                'rounded-lg shadow-xl border',
                darkMode 
                  ? 'bg-slate-900 border-slate-700' 
                  : 'bg-white border-gray-200'
              )}>
                <div className="p-4">
                  <div className="flex items-center space-x-3">
                    <MagnifyingGlassIcon className={clsx(
                      'w-5 h-5',
                      darkMode ? 'text-slate-500' : 'text-gray-400'
                    )} />
                    <input
                      type="text"
                      placeholder="Search features, settings, or documentation..."
                      className={clsx(
                        'flex-1 bg-transparent outline-none',
                        darkMode ? 'text-white placeholder-slate-500' : 'text-gray-900 placeholder-gray-400'
                      )}
                      autoFocus
                    />
                    <kbd className={clsx(
                      'px-2 py-1 text-xs rounded border',
                      darkMode 
                        ? 'bg-slate-800 border-slate-700 text-slate-400' 
                        : 'bg-gray-100 border-gray-300 text-gray-500'
                    )}>
                      ESC
                    </kbd>
                  </div>
                </div>
                <div className={clsx(
                  'border-t p-2',
                  darkMode ? 'border-slate-800' : 'border-gray-200'
                )}>
                  <div className="space-y-1">
                    {navigation.map((item) => (
                      <button
                        key={item.name}
                        onClick={() => {
                          setCurrentPage(item.page)
                          setSearchOpen(false)
                        }}
                        className={clsx(
                          'w-full flex items-center justify-between px-3 py-2 rounded-lg transition-all',
                          darkMode 
                            ? 'hover:bg-slate-800 text-slate-300' 
                            : 'hover:bg-gray-100 text-gray-700'
                        )}
                      >
                        <div className="flex items-center space-x-3">
                          <item.icon className="w-5 h-5" />
                          <div className="text-left">
                            <p className="text-sm font-medium">{item.name}</p>
                            <p className={clsx(
                              'text-xs',
                              darkMode ? 'text-slate-500' : 'text-gray-500'
                            )}>
                              {item.description}
                            </p>
                          </div>
                        </div>
                        <ArrowRightIcon className={clsx(
                          'w-4 h-4',
                          darkMode ? 'text-slate-600' : 'text-gray-400'
                        )} />
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Mobile Navigation */}
      <nav className={clsx(
        'fixed bottom-0 left-0 right-0 lg:hidden border-t',
        darkMode 
          ? 'bg-slate-900 border-slate-800' 
          : 'bg-white border-gray-200'
      )}>
        <div className="grid grid-cols-4 gap-1 p-2">
          {navigation.map((item) => {
            const isActive = currentPage === item.page
            return (
              <button
                key={item.name}
                onClick={() => setCurrentPage(item.page)}
                className={clsx(
                  'flex flex-col items-center justify-center py-2 rounded-lg transition-all',
                  isActive 
                    ? darkMode 
                      ? 'bg-blue-600/10 text-blue-400' 
                      : 'bg-blue-50 text-blue-600'
                    : darkMode
                      ? 'text-slate-400'
                      : 'text-gray-600'
                )}
              >
                <item.icon className="w-5 h-5 mb-1" />
                <span className="text-xs">{item.name.split(' ')[0]}</span>
              </button>
            )
          })}
        </div>
      </nav>
    </div>
  )
}

export default App