import React from 'react';
import { ReactFlow, Background, Controls } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

const initialNodes = [
  {
    id: '1',
    position: { x: 50, y: 100 },
    data: { label: 'DB: analytics_prod.user_transactions' },
    style: { background: '#ffffff', border: '2px solid #3b82f6', borderRadius: '8px', padding: '12px', fontWeight: 'bold' },
  },
  {
    id: '2',
    position: { x: 400, y: 100 },
    data: { label: 'MCP Guardrail Engine' },
    style: { background: '#eff6ff', border: '2px solid #2563eb', borderRadius: '8px', padding: '12px', fontWeight: 'bold', color: '#1d4ed8' },
  },
  {
    id: '3',
    position: { x: 750, y: 100 },
    data: { label: 'LLM Agent Execution' },
    style: { background: '#f0fdf4', border: '2px solid #16a34a', borderRadius: '8px', padding: '12px', fontWeight: 'bold', color: '#15803d' },
  },
];

const initialEdges = [
  { id: 'e1-2', source: '1', target: '2', animated: true, label: 'Metadata Sync' },
  { id: 'e2-3', source: '2', target: '3', animated: true, label: 'Enriched Prompt Context' },
];

export default function LineageGraph() {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm space-y-4">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Data Lineage & Context Flow</h2>
        <p className="text-sm text-gray-500">Visual mapping of schema dependencies and tool execution paths</p>
      </div>

      <div className="h-[450px] border rounded-lg bg-gray-50">
        <ReactFlow nodes={initialNodes} edges={initialEdges} fitView>
          <Background />
          <Controls />
        </ReactFlow>
      </div>
    </div>
  );
}