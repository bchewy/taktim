import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import SingleAnalysis from './components/SingleAnalysis';
import BulkAnalysis from './components/BulkAnalysis';
import Results from './components/Results';
import Alerts from './components/Alerts';
import Settings from './components/Settings';
import './App.css';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/single-analysis" element={<SingleAnalysis />} />
          <Route path="/bulk-analysis" element={<BulkAnalysis />} />
          <Route path="/results" element={<Results />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;