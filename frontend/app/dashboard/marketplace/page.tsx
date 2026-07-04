'use client';

import React, { useState } from 'react';

interface Agent {
  id: string;
  name: string;
  description: string;
  category: string;
  enabled: boolean;
  icon?: string;
  tools: string[];
  version: string;
}


const CATEGORIES = ['All', 'Personal', 'Productivity', 'Communication', 'Research', 'Business', 'Finance', 'Education', 'Automation', 'Travel'];

export default function AgentMarketplace() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');

  // Fetch agents from the API
  React.useEffect(() => {
    const fetchAgents = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('/api/v1/agents', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        
        if (response.ok) {
          const data = await response.json();
          // Transform backend data to match frontend Agent interface
          const formattedAgents: Agent[] = data.agents.map((a: any) => ({
            id: a.id.toString(),
            name: a.name,
            description: a.description || '',
            category: a.config?.category || 'Business',
            enabled: a.status === 'active',
            icon: '🤖', // Default icon
            tools: a.capabilities ? a.capabilities : [],
            version: a.version || '1.0.0',
          }));
          setAgents(formattedAgents);
        }
      } catch (error) {
        console.error('Error fetching agents:', error);
      } finally {
        // isLoading state removed
      }
    };
    
    fetchAgents();
  }, []);

  const filteredAgents = agents.filter((agent) => {
    const matchesCategory = selectedCategory === 'All' || agent.category === selectedCategory;
    const matchesSearch =
      agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      agent.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const handleToggleAgent = async (agentId: string) => {
    const updatedAgents = agents.map((agent) =>
      agent.id === agentId ? { ...agent, enabled: !agent.enabled } : agent
    );
    setAgents(updatedAgents);

    try {
      const agent = agents.find((a) => a.id === agentId);
      if (agent) {
        await fetch(`/api/v1/agents/${agentId}/enable`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
          body: JSON.stringify({
            enabled: !agent.enabled,
          }),
        });
      }
    } catch (error) {
      console.error('Error toggling agent:', error);
    }
  };

  const enabledCount = agents.filter((a) => a.enabled).length;

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">🎯 Agent Marketplace</h1>
          <p className="text-lg text-slate-600">
            Discover and enable AI agents to extend Buddy's capabilities
          </p>
          <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-900">
              <strong>{enabledCount} agents</strong> enabled • Browse, enable, and customize agents to fit your workflow
            </p>
          </div>
        </div>

        {/* Search and Filter */}
        <div className="mb-8 space-y-4">
          <input
            type="text"
            placeholder="Search agents..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />

          <div className="flex gap-2 flex-wrap">
            {CATEGORIES.map((category) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  selectedCategory === category
                    ? 'bg-blue-500 text-white'
                    : 'bg-white text-slate-700 border border-slate-200 hover:bg-slate-50'
                }`}
              >
                {category}
              </button>
            ))}
          </div>
        </div>

        {/* Agent Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredAgents.map((agent) => (
            <div
              key={agent.id}
              className="bg-white rounded-lg shadow-md hover:shadow-lg transition border border-slate-200 overflow-hidden"
            >
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="text-4xl">{agent.icon}</div>
                  <button
                    onClick={() => handleToggleAgent(agent.id)}
                    className={`px-3 py-1 rounded-full text-xs font-semibold transition ${
                      agent.enabled
                        ? 'bg-green-100 text-green-700'
                        : 'bg-slate-100 text-slate-600'
                    }`}
                  >
                    {agent.enabled ? '✓ Enabled' : 'Disabled'}
                  </button>
                </div>

                <h3 className="text-xl font-bold text-slate-900 mb-2">{agent.name}</h3>
                <p className="text-slate-600 text-sm mb-4">{agent.description}</p>

                <div className="mb-4">
                  <p className="text-xs font-semibold text-slate-700 mb-2">Tools:</p>
                  <div className="flex flex-wrap gap-1">
                    {agent.tools.map((tool, idx) => (
                      <span key={idx} className="px-2 py-1 bg-slate-100 text-slate-700 text-xs rounded">
                        {tool}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-slate-100">
                  <span className="text-xs text-slate-500">v{agent.version}</span>
                  <button
                    onClick={() => handleToggleAgent(agent.id)}
                    className="px-4 py-2 bg-blue-500 text-white text-sm font-medium rounded hover:bg-blue-600 transition"
                  >
                    {agent.enabled ? 'Disable' : 'Enable'}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredAgents.length === 0 && (
          <div className="text-center py-12">
            <p className="text-slate-600">No agents found matching your criteria.</p>
          </div>
        )}
      </div>
    </div>
  );
}
