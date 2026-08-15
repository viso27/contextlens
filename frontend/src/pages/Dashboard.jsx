import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Database, AlertTriangle, CheckCircle2, Shield, Plus, Trash2, Table } from 'lucide-react';
import AddSchemaModal from '../components/AddSchemaModal';

export default function Dashboard() {
  const [tables, setTables] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchMetadata = () => {
    setLoading(true);
    axios.get('https://contextlens-abus.onrender.com/api/metadata/')
      .then(res => {
        setTables(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error("API error:", err);
        setLoading(false);
      });
  };

  const handleDeleteTable = async (tableName) => {
    if (!window.confirm(`Are you sure you want to delete table '${tableName}'?`)) return;
    try {
      await axios.delete(`https://contextlens-abus.onrender.com/api/metadata/${tableName}`);
      fetchMetadata();
    } catch (err) {
      alert("Failed to delete table.");
    }
  };

  useEffect(() => {
    fetchMetadata();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Registered Schemas & Context Guardrails</h2>
          <p className="text-sm text-gray-500">Managed database structures active in the ContextLens MCP server</p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-4 py-2.5 rounded-lg transition-all shadow-sm text-sm"
        >
          <Plus size={16} /> Create Custom Schema
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-500 font-medium">Loading Database Metadata...</div>
      ) : tables.length === 0 ? (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-yellow-800 flex justify-between items-center">
          <div>
            <p className="font-semibold">No Dynamic Tables Registered</p>
            <p className="text-sm mt-1">Click 'Create Custom Schema' above to register a new database schema and seed data.</p>
          </div>
          <button
            onClick={() => setIsModalOpen(true)}
            className="bg-yellow-600 text-white font-semibold px-4 py-2 rounded-lg text-sm"
          >
            Create First Schema
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6">
          {tables.map((table, idx) => (
            <div key={idx} className="bg-white border border-gray-200 rounded-xl shadow-sm p-6 space-y-5">
              <div className="flex justify-between items-start border-b pb-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
                      {table.database}
                    </span>
                    <span className="flex items-center gap-1 bg-green-50 text-green-700 px-2.5 py-0.5 rounded-full text-xs font-semibold border border-green-200">
                      <Shield size={13} /> Trust: {(table.trust_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mt-1">{table.table_name}</h3>
                  <p className="text-sm text-gray-500 mt-0.5">{table.description}</p>
                </div>

                <button
                  onClick={() => handleDeleteTable(table.table_name)}
                  className="text-gray-400 hover:text-red-600 p-1.5 rounded-lg hover:bg-red-50 transition-colors"
                  title="Delete Schema"
                >
                  <Trash2 size={18} />
                </button>
              </div>

              {/* Column Governance Section */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-gray-400">Column Governance Rules</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {table.columns.map((col, cIdx) => (
                    <div key={cIdx} className="flex items-start justify-between bg-gray-50 p-3 rounded-lg border border-gray-100">
                      <div className="flex items-start gap-2.5">
                        {col.status === 'deprecated' ? (
                          <AlertTriangle size={18} className="text-red-500 mt-0.5 flex-shrink-0" />
                        ) : (
                          <CheckCircle2 size={18} className="text-green-500 mt-0.5 flex-shrink-0" />
                        )}
                        <div>
                          <div className="flex items-center gap-2">
                            <span className={`font-mono text-sm font-semibold ${col.status === 'deprecated' ? 'line-through text-red-600' : 'text-gray-800'}`}>
                              {col.name}
                            </span>
                            <span className="text-xs text-gray-400 font-mono">({col.data_type})</span>
                          </div>
                          <p className="text-xs text-gray-500 mt-0.5">{col.description}</p>
                          {col.status === 'deprecated' && (
                            <p className="text-xs font-medium text-red-600 mt-1 bg-red-50 px-2 py-0.5 rounded border border-red-100 inline-block">
                              ⚠️ Replace with: <span className="font-mono font-bold">{col.replacement_column}</span>
                            </p>
                          )}
                        </div>
                      </div>
                      <span className={`text-xs px-2 py-0.5 rounded font-semibold ${col.status === 'deprecated' ? 'bg-red-100 text-red-700' : 'bg-gray-200 text-gray-700'}`}>
                        {col.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Sample Data Preview */}
              {table.sample_data && table.sample_data.length > 0 && (
                <div className="space-y-2 pt-2 border-t">
                  <div className="flex items-center gap-2 text-gray-700">
                    <Table size={14} />
                    <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500">Seeded Table Records Preview</h4>
                  </div>
                  <div className="overflow-x-auto bg-gray-900 rounded-lg p-3">
                    <pre className="text-xs font-mono text-green-400">
                      {JSON.stringify(table.sample_data, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <AddSchemaModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={fetchMetadata}
      />
    </div>
  );
}
