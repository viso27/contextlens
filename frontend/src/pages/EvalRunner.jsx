import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Play, CheckCircle2, XCircle, Filter, Database, RefreshCw } from 'lucide-react';

export default function EvalRunner() {
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState('all');
  const [loading, setLoading] = useState(false);
  const [evalResults, setEvalResults] = useState(null);

  useEffect(() => {
    // Fetch registered tables for dropdown selection
    axios.get('http://localhost:8000/api/metadata/')
      .then(res => setTables(res.data))
      .catch(err => console.error(err));
  }, []);

  const handleRunEvaluation = async () => {
    setLoading(true);
    try {
      const url = selectedTable === 'all'
        ? 'http://localhost:8000/api/evals/run'
        : `http://localhost:8000/api/evals/run?table_name=${encodeURIComponent(selectedTable)}`;
      
      const res = await axios.post(url);
      setEvalResults(res.data);
    } catch (err) {
      alert("Error executing evaluation harness.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Target Table Control Bar */}
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Drift & Governance Evaluation Suite</h2>
          <p className="text-sm text-gray-500">Benchmark MCP dynamic schema enforcement against raw LLM output</p>
        </div>

        <div className="flex items-center gap-3 w-full md:w-auto">
          {/* Dynamic Table Selector Dropdown */}
          <div className="flex items-center gap-2 bg-gray-50 border border-gray-300 rounded-lg px-3 py-2 text-sm">
            <Filter size={16} className="text-gray-500" />
            <select
              value={selectedTable}
              onChange={(e) => setSelectedTable(e.target.value)}
              className="bg-transparent text-gray-800 font-semibold focus:outline-none cursor-pointer"
            >
              <option value="all">🌐 All Registered Tables</option>
              {tables.map((t, idx) => (
                <option key={idx} value={t.table_name}>
                  📊 {t.table_name} ({t.database})
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={handleRunEvaluation}
            disabled={loading}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-5 py-2.5 rounded-lg transition-all shadow-sm text-sm disabled:opacity-50"
          >
            {loading ? <RefreshCw className="animate-spin" size={16} /> : <Play size={16} />}
            {loading ? 'Evaluating...' : 'Run Targeted Drift Suite'}
          </button>
        </div>
      </div>

      {/* Metrics Header */}
      {evalResults && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
            <p className="text-xs font-bold text-gray-400 uppercase">Target Scope</p>
            <p className="text-xl font-bold text-gray-800 mt-1 flex items-center gap-2">
              <Database size={18} className="text-blue-500" />
              {selectedTable === 'all' ? 'All Tables' : selectedTable}
            </p>
          </div>

          <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
            <p className="text-xs font-bold text-gray-400 uppercase">Schema Precision</p>
            <p className="text-2xl font-extrabold text-green-600 mt-1">
              {(evalResults.schema_precision * 100).toFixed(0)}%
            </p>
          </div>

          <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
            <p className="text-xs font-bold text-gray-400 uppercase">Drift Recovery Rate</p>
            <p className="text-2xl font-extrabold text-blue-600 mt-1">
              {(evalResults.drift_recovery_rate * 100).toFixed(0)}%
            </p>
          </div>
        </div>
      )}

      {/* Test Result Logs */}
      {evalResults && (
        <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
          <div className="p-4 border-b bg-gray-50 flex justify-between items-center">
            <h3 className="font-bold text-gray-800 text-sm">Evaluation Benchmark Logs</h3>
            <span className="text-xs font-semibold bg-gray-200 px-2 py-0.5 rounded text-gray-700">
              {evalResults.total_questions} Tests Executed
            </span>
          </div>

          <div className="divide-y divide-gray-100">
            {evalResults.logs.map((log, idx) => (
              <div key={idx} className="p-5 space-y-3">
                <div className="flex justify-between items-start">
                  <div className="flex items-center gap-2">
                    {log.passed ? (
                      <CheckCircle2 size={18} className="text-green-500" />
                    ) : (
                      <XCircle size={18} className="text-red-500" />
                    )}
                    <span className="font-semibold text-gray-900 text-sm">{log.question}</span>
                  </div>
                  <span className="text-xs font-mono bg-blue-50 text-blue-700 px-2 py-0.5 rounded border border-blue-100">
                    {log.table_name}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs font-mono pt-1">
                  <div className="bg-red-50/60 p-3 rounded-lg border border-red-100">
                    <p className="font-bold text-red-700 mb-1 font-sans">❌ Without ContextLens (Raw LLM):</p>
                    <p className="text-red-900 break-words">{log.without_mcp_query}</p>
                  </div>

                  <div className="bg-green-50/60 p-3 rounded-lg border border-green-100">
                    <p className="font-bold text-green-700 mb-1 font-sans">✅ With ContextLens (MCP Guarded):</p>
                    <p className="text-green-900 break-words">{log.with_mcp_query}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}