import React, { useState } from 'react';
import Dashboard from './pages/Dashboard';
import EvalRunner from './pages/EvalRunner';
import LineageGraph from './flow/LineageGraph';
import Sandbox from './pages/Sandbox'; 
import { Database, PlayCircle, GitFork, ShieldCheck, Terminal } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-3">
          <div className="bg-blue-600 text-white p-2 rounded-lg">
            <ShieldCheck size={24} />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-gray-900">ContextLens</h1>
            <p className="text-xs text-gray-500">MCP Context Engine & Schema Drift Eval Suite</p>
          </div>
        </div>

        <nav className="flex bg-gray-100 p-1 rounded-lg">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-all ${
              activeTab === 'dashboard' ? 'bg-white shadow-sm text-blue-600' : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Database size={16} /> Schema Registry
          </button>

          <button
            onClick={() => setActiveTab('sandbox')}
            className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-all ${
              activeTab === 'sandbox' ? 'bg-white shadow-sm text-blue-600' : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Terminal size={16} /> Query Sandbox
          </button>
          
          <button
            onClick={() => setActiveTab('evals')}
            className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-all ${
              activeTab === 'evals' ? 'bg-white shadow-sm text-blue-600' : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <PlayCircle size={16} /> Eval Harness
          </button>

          <button
            onClick={() => setActiveTab('lineage')}
            className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-all ${
              activeTab === 'lineage' ? 'bg-white shadow-sm text-blue-600' : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <GitFork size={16} /> Data Lineage
          </button>
        </nav>
      </header>

      <main className="flex-1 p-8 max-w-7xl mx-auto w-full">
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'sandbox' && <Sandbox />}
        {activeTab === 'evals' && <EvalRunner />}
        {activeTab === 'lineage' && <LineageGraph />}
      </main>
    </div>
  );
}