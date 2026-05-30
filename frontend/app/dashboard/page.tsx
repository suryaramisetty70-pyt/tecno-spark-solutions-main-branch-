'use client';

import { useEffect, useState } from 'react';
import { analyticsAPI } from '@/lib/api-client';

interface DashboardStats {
  total_users?: number;
  total_workflows?: number;
  total_agents?: number;
  api_calls_today?: number;
  system_health?: number;
}

interface Metric {
  name: string;
  value: string | number;
  change?: number;
  icon: string;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const response = await analyticsAPI.getDashboard();
        if (response.data) {
          setStats(response.data);
        }
      } catch (error) {
        console.error('Failed to load dashboard:', error);
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, []);

  const metrics: Metric[] = [
    {
      name: 'Total Workflows',
      value: stats.total_workflows || 0,
      icon: '⚙️',
      change: 12,
    },
    {
      name: 'Active Agents',
      value: stats.total_agents || 0,
      icon: '🤖',
      change: 8,
    },
    {
      name: 'API Calls (Today)',
      value: stats.api_calls_today || 0,
      icon: '📡',
      change: 24,
    },
    {
      name: 'System Health',
      value: `${stats.system_health || 99}%`,
      icon: '❤️',
      change: 2,
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
        <p className="text-gray-600">Welcome to Buddy AI Operating System</p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric, index) => (
          <div key={index} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-gray-600 font-medium">{metric.name}</h3>
              <span className="text-2xl">{metric.icon}</span>
            </div>
            <div className="flex items-end justify-between">
              <div className="text-3xl font-bold text-gray-900">{metric.value}</div>
              {metric.change !== undefined && (
                <span className="text-green-600 text-sm font-semibold">
                  +{metric.change}%
                </span>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded transition">
              Create Workflow
            </button>
            <button className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-2 rounded transition">
              Add Agent
            </button>
            <button className="w-full bg-purple-600 hover:bg-purple-700 text-white font-semibold py-2 rounded transition">
              Upload File
            </button>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Activity</h2>
          <div className="space-y-3 text-gray-600 text-sm">
            <p>📊 Dashboard viewed - 2 minutes ago</p>
            <p>🤖 Agent execution completed - 15 minutes ago</p>
            <p>⚙️ Workflow paused - 1 hour ago</p>
            <p>📁 File uploaded - 2 hours ago</p>
          </div>
        </div>
      </div>

      {/* Features Overview */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Platform Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { icon: '⚙️', title: 'Workflow Automation', desc: 'Automate complex processes' },
            { icon: '🤖', title: 'AI Agents', desc: 'Orchestrate intelligent agents' },
            { icon: '📁', title: 'File Management', desc: 'Store and organize files' },
            { icon: '🔍', title: 'Advanced Search', desc: 'Find anything instantly' },
            { icon: '📈', title: 'Analytics', desc: 'Track performance metrics' },
            { icon: '🔔', title: 'Notifications', desc: 'Stay informed in real-time' },
          ].map((feature, index) => (
            <div key={index} className="p-4 bg-gray-50 rounded-lg">
              <div className="text-3xl mb-2">{feature.icon}</div>
              <h3 className="font-semibold text-gray-900">{feature.title}</h3>
              <p className="text-sm text-gray-600">{feature.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
