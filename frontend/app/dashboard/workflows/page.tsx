'use client';

import { useEffect, useState } from 'react';
import { workflowAPI } from '@/lib/api-client';
import Link from 'next/link';

interface Workflow {
  id: number;
  name: string;
  description?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadWorkflows = async () => {
      try {
        setLoading(true);
        const response = await workflowAPI.list();
        if (response.data) {
          setWorkflows(response.data as any);
        }
        if (response.error) {
          setError(response.error);
        }
      } catch (err) {
        setError('Failed to load workflows');
      } finally {
        setLoading(false);
      }
    };

    loadWorkflows();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'paused':
        return 'bg-yellow-100 text-yellow-800';
      case 'draft':
        return 'bg-blue-100 text-blue-800';
      case 'archived':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Workflows</h1>
          <p className="text-gray-600 mt-1">Manage your automation workflows</p>
        </div>
        <button className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded transition">
          + Create Workflow
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded text-red-700">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center py-12">
          <p className="text-gray-600">Loading workflows...</p>
        </div>
      ) : workflows.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-600 mb-4">No workflows yet</p>
          <button className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded transition">
            Create Your First Workflow
          </button>
        </div>
      ) : (
        <div className="grid gap-4">
          {workflows.map((workflow) => (
            <Link
              key={workflow.id}
              href={`/workflows/${workflow.id}`}
              className="bg-white rounded-lg shadow hover:shadow-lg transition p-6 block"
            >
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h3 className="text-lg font-bold text-gray-900">{workflow.name}</h3>
                  {workflow.description && (
                    <p className="text-gray-600 text-sm mt-1">{workflow.description}</p>
                  )}
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getStatusColor(workflow.status)}`}>
                  {workflow.status}
                </span>
              </div>
              <div className="flex justify-between text-sm text-gray-500">
                <span>Created: {new Date(workflow.created_at).toLocaleDateString()}</span>
                <span>Updated: {new Date(workflow.updated_at).toLocaleDateString()}</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
