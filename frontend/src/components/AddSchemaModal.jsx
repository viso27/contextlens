import React, { useState } from 'react';
import axios from 'axios';
import { X, Plus, Trash2, Database, AlertCircle } from 'lucide-react';

export default function AddSchemaModal({ isOpen, onClose, onSuccess }) {
  const [database, setDatabase] = useState('analytics_prod');
  const [tableName, setTableName] = useState('');
  const [description, setDescription] = useState('');
  const [columns, setColumns] = useState([
    { name: 'id', data_type: 'UUID', description: 'Primary Key', status: 'active', replacement_column: '', deprecation_notice: '' },
    { name: 'old_amount', data_type: 'DECIMAL(10,2)', description: 'Legacy billing amount', status: 'deprecated', replacement_column: 'new_amount', deprecation_notice: 'Use new_amount instead.' }
  ]);
  const [sampleDataJson, setSampleDataJson] = useState('[\n  { "id": "usr_001", "old_amount": 100.0, "new_amount": 105.0 }\n]');

  if (!isOpen) return null;

  const handleAddColumn = () => {
    setColumns([
      ...columns,
      { name: '', data_type: 'VARCHAR(255)', description: '', status: 'active', replacement_column: '', deprecation_notice: '' }
    ]);
  };

  const handleRemoveColumn = (index) => {
    setColumns(columns.filter((_, idx) => idx !== index));
  };

  const handleColumnChange = (index, field, value) => {
    const updated = [...columns];
    updated[index][field] = value;
    setColumns(updated);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    let parsedSampleData = [];
    try {
      if (sampleDataJson.trim()) {
        parsedSampleData = JSON.parse(sampleDataJson);
      }
    } catch (err) {
      alert("Invalid JSON format in Sample Data field.");
      return;
    }

    const payload = {
      database,
      table_name: tableName,
      description,
      trust_score: 0.95,
      columns,
      sample_data: parsedSampleData
    };

    try {
      await axios.post('http://localhost:8000/api/metadata/', payload);
      onSuccess();
      onClose();
    } catch (err) {
      alert("Failed to create database schema.");
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-white rounded-xl max-w-2xl w-full p-6 shadow-2xl relative space-y-5 my-8">
        <button onClick={onClose} className="absolute top-4 right-4 text-gray-400 hover:text-gray-600">
          <X size={20} />
        </button>

        <div className="flex items-center gap-2 text-blue-600 font-bold border-b pb-3">
          <Database size={22} />
          <h3 className="text-xl text-gray-900">Create Database Schema & Seed Data</h3>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-gray-600 uppercase mb-1">Database</label>
              <input
                type="text"
                value={database}
                onChange={e => setDatabase(e.target.value)}
                className="w-full border rounded-lg p-2 text-sm"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-600 uppercase mb-1">Table Name</label>
              <input
                type="text"
                placeholder="e.g., subscription_billing"
                value={tableName}
                onChange={e => setTableName(e.target.value)}
                className="w-full border rounded-lg p-2 text-sm"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-gray-600 uppercase mb-1">Table Description</label>
            <input
              type="text"
              placeholder="e.g., Manages monthly customer subscription payouts"
              value={description}
              onChange={e => setDescription(e.target.value)}
              className="w-full border rounded-lg p-2 text-sm"
              required
            />
          </div>

          {/* Dynamic Column Builder */}
          <div className="space-y-3 pt-2">
            <div className="flex justify-between items-center border-b pb-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-gray-700">Define Schema Columns</h4>
              <button
                type="button"
                onClick={handleAddColumn}
                className="text-xs bg-blue-50 text-blue-600 hover:bg-blue-100 px-3 py-1 rounded-md font-semibold flex items-center gap-1"
              >
                <Plus size={14} /> Add Column
              </button>
            </div>

            <div className="space-y-3 max-h-60 overflow-y-auto pr-1">
              {columns.map((col, idx) => (
                <div key={idx} className="bg-gray-50 p-3 rounded-lg border border-gray-200 space-y-2">
                  <div className="grid grid-cols-12 gap-2 items-center">
                    <input
                      type="text"
                      placeholder="Column Name"
                      value={col.name}
                      onChange={e => handleColumnChange(idx, 'name', e.target.value)}
                      className="col-span-4 border rounded p-1.5 text-xs font-mono"
                      required
                    />
                    <input
                      type="text"
                      placeholder="Data Type"
                      value={col.data_type}
                      onChange={e => handleColumnChange(idx, 'data_type', e.target.value)}
                      className="col-span-3 border rounded p-1.5 text-xs font-mono"
                      required
                    />
                    <select
                      value={col.status}
                      onChange={e => handleColumnChange(idx, 'status', e.target.value)}
                      className="col-span-4 border rounded p-1.5 text-xs font-semibold"
                    >
                      <option value="active">Active</option>
                      <option value="deprecated">Deprecated</option>
                    </select>
                    <button
                      type="button"
                      onClick={() => handleRemoveColumn(idx)}
                      className="col-span-1 text-red-500 hover:text-red-700 flex justify-center"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>

                  {col.status === 'deprecated' && (
                    <div className="grid grid-cols-2 gap-2 pt-1 bg-red-50/50 p-2 rounded border border-red-100">
                      <input
                        type="text"
                        placeholder="Replacement Column Name"
                        value={col.replacement_column}
                        onChange={e => handleColumnChange(idx, 'replacement_column', e.target.value)}
                        className="border rounded p-1.5 text-xs font-mono bg-white"
                        required
                      />
                      <input
                        type="text"
                        placeholder="Deprecation Warning Notice"
                        value={col.deprecation_notice}
                        onChange={e => handleColumnChange(idx, 'deprecation_notice', e.target.value)}
                        className="border rounded p-1.5 text-xs bg-white"
                      />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Seed Data JSON Input */}
          <div className="space-y-1 pt-2">
            <label className="block text-xs font-bold text-gray-700 uppercase">Seed Sample Records (JSON Array)</label>
            <textarea
              rows={3}
              value={sampleDataJson}
              onChange={e => setSampleDataJson(e.target.value)}
              className="w-full border rounded-lg p-2 text-xs font-mono bg-gray-900 text-green-400 focus:outline-none"
              placeholder='[{"id": 1, "status": "active"}]'
            />
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t">
            <button type="button" onClick={onClose} className="px-4 py-2 text-sm text-gray-600">Cancel</button>
            <button type="submit" className="px-5 py-2 text-sm bg-blue-600 text-white font-semibold rounded-lg flex items-center gap-1 hover:bg-blue-700 shadow-sm">
              <Plus size={16} /> Create Schema & Seed Data
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}