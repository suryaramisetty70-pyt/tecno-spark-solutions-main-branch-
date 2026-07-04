'use client';

import { useEffect, useState } from 'react';
import { agentAPI } from '@/lib/api-client';

interface Agent {
  id: number;
  name: string;
  description?: string;
  status: string;
  version?: string;
  last_used?: string;
}

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadAgents = async () => {
      try {
        const response = await agentAPI.list();
        if (response.data && (response.data as any).agents) {
          setAgents((response.data as any).agents);
        }
      } catch (error) {
        console.error('Failed to load agents:', error);
      } finally {
        setLoading(false);
      }
    };

    loadAgents();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Agents</h1>
          <p className="text-gray-600 mt-1">Manage AI agents</p>
        </div>
        <button className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded transition">
          + Add Agent
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <p className="text-gray-600">Loading agents...</p>
        </div>
      ) : agents.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-600">No agents available</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {agents.map((agent) => (
            <div key={agent.id} className="bg-white rounded-lg shadow hover:shadow-lg transition p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-bold text-gray-900">🤖 {agent.name}</h3>
                  {agent.description && (
                    <p className="text-gray-600 text-sm mt-1">{agent.description}</p>
                  )}
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                  agent.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                }`}>
                  {agent.status}
                </span>
              </div>
              <button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded transition">
                View Details
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
