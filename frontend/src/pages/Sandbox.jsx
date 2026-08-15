import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Send, Terminal, AlertTriangle, ShieldCheck, Filter, Database, Code2 } from 'lucide-react';

export default function Sandbox() {
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState('all');
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => {
    // Fetch available tables for dropdown targeting
    axios.get('https://contextlens-abus.onrender.com/api/metadata/')
      .then(res => setTables(res.data))
      .catch(err => console.error(err));
  }, []);

  const handleExecuteQuery = async (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setLoading(true);
    try {
      const res = await axios.post('https://contextlens-abus.onrender.com/api/sandbox/query', {
        prompt: prompt,
        table_name: selectedTable
      });
      setResult(res.data);
    } catch (err) {
      alert("Error executing query sandbox.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Target Table Control & Query Input */}
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-4">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b pb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Interactive Query Sandbox</h2>
            <p className="text-sm text-gray-500">Test prompt context resolution against standard vs. MCP-governed LLM outputs</p>
          </div>

          {/* Dynamic Scope Selector */}
          <div className="flex items-center gap-2 bg-gray-50 border border-gray-300 rounded-lg px-3 py-2 text-sm">
            <Filter size={16} className="text-gray-500" />
            <select
              value={selectedTable}
              onChange={(e) => setSelectedTable(e.target.value)}
              className="bg-transparent text-gray-800 font-semibold focus:outline-none cursor-pointer"
            >
              <option value="all">🌐 All Database Schemas</option>
              {tables.map((t, idx) => (
                <option key={idx} value={t.table_name}>
                  📊 {t.table_name} ({t.database})
                </option>
              ))}
            </select>
          </div>
        </div>

        <form onSubmit={handleExecuteQuery} className="flex gap-3">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Ask a question in plain text (e.g., Get revenue for customer billing)..."
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-2.5 rounded-lg flex items-center gap-2 transition-all shadow-sm text-sm disabled:opacity-50"
          >
            <Send size={16} />
            {loading ? 'Interpreting...' : 'Run Query'}
          </button>
        </form>
      </div>

      {/* Output Display */}
      {result && (
        <div className="space-y-6">
          {/* Active Warnings */}
          {result.warnings && result.warnings.length > 0 && (
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 space-y-2">
              <div className="flex items-center gap-2 text-amber-800 font-bold text-sm">
                <AlertTriangle size={18} />
                <span>ContextLens Governance Interceptions</span>
              </div>
              <ul className="list-disc list-inside text-xs text-amber-700 space-y-1">
                {result.warnings.map((warn, wIdx) => (
                  <li key={wIdx}>{warn}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Dual Query Comparison */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Raw SQL */}
            <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden flex flex-col">
              <div className="bg-red-50 border-b border-red-100 p-4 flex items-center justify-between">
                <span className="font-bold text-red-800 text-sm flex items-center gap-2">
                  <Terminal size={16} /> Raw Un-governed LLM Output
                </span>
                <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded font-mono">No MCP Context</span>
              </div>
              <div className="p-4 bg-gray-900 flex-1 overflow-x-auto">
                <pre className="text-xs font-mono text-red-300 whitespace-pre-wrap">{result.raw_sql}</pre>
              </div>
            </div>

            {/* MCP-Guarded SQL */}
            <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden flex flex-col">
              <div className="bg-green-50 border-b border-green-100 p-4 flex items-center justify-between">
                <span className="font-bold text-green-800 text-sm flex items-center gap-2">
                  <ShieldCheck size={16} /> ContextLens MCP-Enriched Output
                </span>
                <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded font-mono">Governance Enforced</span>
              </div>
              <div className="p-4 bg-gray-900 flex-1 overflow-x-auto">
                <pre className="text-xs font-mono text-green-300 whitespace-pre-wrap">{result.mcp_sql}</pre>
              </div>
            </div>
          </div>

          {/* Injected Context Preview */}
          <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-4 space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 flex items-center gap-2">
              <Code2 size={14} /> Dynamically Injected MCP Prompt Context ({result.target_table})
            </h4>
            <pre className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-xs font-mono text-gray-700 overflow-x-auto max-h-48">
              {result.mcp_prompt_context}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
