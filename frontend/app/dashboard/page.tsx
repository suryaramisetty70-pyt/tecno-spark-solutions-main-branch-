'use client';

import { useEffect, useState } from 'react';
import { agentAPI, workflowAPI } from '@/lib/api-client';
import Link from 'next/link';

interface DashboardData {
  totalWorkflows: number;
  activeAgents: number;
  apiCalls: number;
  systemHealth: string;
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData>({
    totalWorkflows: 0,
    activeAgents: 0,
    apiCalls: 0,
    systemHealth: '...',
  });
  const [loading, setLoading] = useState(true);
  const [backendOnline, setBackendOnline] = useState(false);

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        // Check backend health
        const healthRes = await fetch('http://localhost:8000/health');
        if (healthRes.ok) {
          setBackendOnline(true);
          const healthData = await healthRes.json();
          
          // Try loading real data
          const [agentsRes, workflowsRes] = await Promise.allSettled([
            agentAPI.list(0, 100),
            workflowAPI.list(0, 100),
          ]);

          const agentCount = agentsRes.status === 'fulfilled' && agentsRes.value.data
            ? (agentsRes.value.data as any).total || (agentsRes.value.data as any).length || 0
            : 0;

          const workflowCount = workflowsRes.status === 'fulfilled' && workflowsRes.value.data
            ? (workflowsRes.value.data as any).total || (workflowsRes.value.data as any).length || 0
            : 0;

          setData({
            totalWorkflows: workflowCount,
            activeAgents: agentCount,
            apiCalls: 0,
            systemHealth: healthData.status === 'healthy' ? '✅ Online' : '⚠️ Degraded',
          });
        }
      } catch (err) {
        setBackendOnline(false);
        setData({
          totalWorkflows: 0,
          activeAgents: 0,
          apiCalls: 0,
          systemHealth: '❌ Offline',
        });
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
    // Refresh every 30s
    const interval = setInterval(loadDashboard, 30000);
    return () => clearInterval(interval);
  }, []);

  const metrics = [
    {
      name: 'Total Workflows',
      value: loading ? '...' : data.totalWorkflows,
      icon: '⚙️',
      color: 'from-blue-500 to-blue-600',
    },
    {
      name: 'Active Agents',
      value: loading ? '...' : data.activeAgents,
      icon: '🤖',
      color: 'from-emerald-500 to-emerald-600',
    },
    {
      name: 'Backend Status',
      value: loading ? '...' : data.systemHealth,
      icon: '❤️',
      color: 'from-rose-500 to-rose-600',
    },
    {
      name: 'API Server',
      value: loading ? '...' : backendOnline ? 'Port 8000' : 'Offline',
      icon: '📡',
      color: 'from-purple-500 to-purple-600',
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
        <p className="text-gray-600">Welcome to Buddy AI Operating System</p>
      </div>

      {/* Backend Status Banner */}
      {!loading && !backendOnline && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
          <p className="text-amber-800 font-medium">
            ⚠️ Backend server is offline. Start it with:{' '}
            <code className="bg-amber-100 px-2 py-1 rounded text-sm">
              cd backend && python -m api.main
            </code>
          </p>
        </div>
      )}

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric, index) => (
          <div key={index} className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-gray-500 font-medium text-sm">{metric.name}</h3>
              <span className="text-2xl">{metric.icon}</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {loading ? (
                <div className="h-8 w-20 bg-gray-200 rounded animate-pulse" />
              ) : (
                metric.value
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <Link
              href="/dashboard/workflows"
              className="block w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition text-center"
            >
              ⚙️ View Workflows
            </Link>
            <Link
              href="/dashboard/agents"
              className="block w-full bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-3 rounded-lg transition text-center"
            >
              🤖 Manage Agents
            </Link>
            <Link
              href="/dashboard/chat"
              className="block w-full bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 rounded-lg transition text-center"
            >
              💬 Open Chat
            </Link>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Platform Features</h2>
          <div className="space-y-3">
            {[
              { icon: '💬', title: 'Buddy Chat', desc: 'Chat with AI agents', href: '/dashboard/chat' },
              { icon: '🎯', title: 'Marketplace', desc: 'Browse & enable agents', href: '/dashboard/marketplace' },
              { icon: '🔍', title: 'Search', desc: 'Find anything instantly', href: '/dashboard/search' },
              { icon: '🔔', title: 'Notifications', desc: 'Stay informed', href: '/dashboard/notifications' },
            ].map((feature, index) => (
              <Link
                key={index}
                href={feature.href}
                className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
              >
                <span className="text-2xl">{feature.icon}</span>
                <div>
                  <h3 className="font-semibold text-gray-900 text-sm">{feature.title}</h3>
                  <p className="text-xs text-gray-500">{feature.desc}</p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>

      {/* System Info */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">System Status</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-gray-50 rounded-lg">
            <p className="text-gray-500 text-sm mb-1">Backend Server</p>
            <p className={`font-semibold ${backendOnline ? 'text-green-600' : 'text-red-600'}`}>
              {backendOnline ? '● Running on http://localhost:8000' : '● Offline'}
            </p>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <p className="text-gray-500 text-sm mb-1">Frontend Server</p>
            <p className="text-green-600 font-semibold">● Running on http://localhost:3000</p>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <p className="text-gray-500 text-sm mb-1">API Documentation</p>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 font-semibold hover:underline"
            >
              Open Swagger UI →
            </a>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <p className="text-gray-500 text-sm mb-1">Database</p>
            <p className="text-green-600 font-semibold">SQLite (buddy_ai.db)</p>
          </div>
        </div>
      </div>
    </div>
  );
}
