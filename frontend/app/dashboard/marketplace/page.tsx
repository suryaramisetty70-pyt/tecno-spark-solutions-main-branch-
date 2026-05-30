'use client';

import React, { useState, useEffect } from 'react';

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

const FEATURED_AGENTS: Agent[] = [
  {
    id: 'personal_assistant',
    name: 'Personal Assistant',
    description: 'Your AI assistant for general tasks and coordination',
    category: 'Personal',
    enabled: true,
    icon: '🤖',
    tools: ['coordination', 'task routing', 'general assistance'],
    version: '0.1.0',
  },
  {
    id: 'memory_agent',
    name: 'Memory Agent',
    description: 'Saves and retrieves your memories with semantic search',
    category: 'Personal',
    enabled: true,
    icon: '💾',
    tools: ['memory save', 'memory retrieve', 'semantic search'],
    version: '0.1.0',
  },
  {
    id: 'productivity_agent',
    name: 'Productivity Agent',
    description: 'Manages tasks, goals, and time blocking',
    category: 'Productivity',
    enabled: true,
    icon: '✓',
    tools: ['task management', 'time blocking', 'goal tracking'],
    version: '0.1.0',
  },
  {
    id: 'email_agent',
    name: 'Email Agent',
    description: 'Handles email send/receive and thread management',
    category: 'Communication',
    enabled: true,
    icon: '📧',
    tools: ['email send', 'email receive', 'thread management'],
    version: '0.1.0',
  },
  {
    id: 'researcher_agent',
    name: 'Researcher Agent',
    description: 'Conducts web research and information gathering',
    category: 'Research',
    enabled: true,
    icon: '🔍',
    tools: ['web research', 'info aggregation', 'source verification'],
    version: '0.1.0',
  },
  {
    id: 'automation_agent',
    name: 'Automation Agent',
    description: 'Creates and manages automated workflows',
    category: 'Automation',
    enabled: true,
    icon: '⚙️',
    tools: ['workflow creation', 'trigger definition', 'action execution'],
    version: '0.1.0',
  },
  {
    id: 'student_agent',
    name: 'Student Agent',
    description: 'Manages coursework, assignments, and exam preparation',
    category: 'Education',
    enabled: false,
    icon: '📚',
    tools: ['course tracking', 'assignment tracking', 'exam prep'],
    version: '0.1.0',
  },
  {
    id: 'sales_agent',
    name: 'Sales Agent',
    description: 'Manages leads, deals, and sales pipeline',
    category: 'Business',
    enabled: false,
    icon: '📊',
    tools: ['lead management', 'deal tracking', 'forecasting'],
    version: '0.1.0',
  },
  {
    id: 'accountant_agent',
    name: 'Accountant Agent',
    description: 'Tracks expenses, invoices, and financial records',
    category: 'Finance',
    enabled: false,
    icon: '💰',
    tools: ['expense tracking', 'invoicing', 'financial reporting'],
    version: '0.1.0',
  },
  {
    id: 'whatsapp_agent',
    name: 'WhatsApp Agent',
    description: 'Manages WhatsApp messaging and communications',
    category: 'Communication',
    enabled: false,
    icon: '💬',
    tools: ['message send', 'message receive', 'group management'],
    version: '0.1.0',
  },
  {
    id: 'booking_agent',
    name: 'Booking Agent',
    description: 'Books flights, hotels, and restaurants',
    category: 'Travel',
    enabled: false,
    icon: '✈️',
    tools: ['flight booking', 'hotel booking', 'restaurant booking'],
    version: '0.1.0',
  },
  {
    id: 'ceo_agent',
    name: 'CEO Agent',
    description: 'Executive dashboard and business intelligence',
    category: 'Business',
    enabled: false,
    icon: '👔',
    tools: ['KPI tracking', 'business intelligence', 'strategic reporting'],
    version: '0.1.0',
  },
];

const CATEGORIES = ['All', 'Personal', 'Productivity', 'Communication', 'Research', 'Business', 'Finance', 'Education', 'Automation', 'Travel'];

export default function AgentMarketplace() {
  const [agents, setAgents] = useState<Agent[]>(FEATURED_AGENTS);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');

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
