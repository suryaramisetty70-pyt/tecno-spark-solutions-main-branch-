'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Mock user data - no authentication required
  const user = {
    username: 'Admin',
    email: 'admin@technospark.com',
    full_name: 'Administrator'
  };

  const menuItems = [
    { name: 'Dashboard', href: '/dashboard', icon: '📊' },
    { name: 'Buddy Chat', href: '/dashboard/chat', icon: '💬' },
    { name: 'Agent Marketplace', href: '/dashboard/marketplace', icon: '🎯' },
    { name: 'Workflows', href: '/dashboard/workflows', icon: '⚙️' },
    { name: 'Agents', href: '/dashboard/agents', icon: '🤖' },
    { name: 'Notifications', href: '/dashboard/notifications', icon: '🔔' },
    { name: 'Search', href: '/dashboard/search', icon: '🔍' },
  ];

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? 'w-64' : 'w-20'
        } bg-gray-900 text-white transition-all duration-300 flex flex-col`}
      >
        <div className="p-4 border-b border-gray-700">
          <h1 className={`font-bold text-xl ${!sidebarOpen && 'text-center'}`}>
            {sidebarOpen ? 'Buddy AI' : 'BA'}
          </h1>
        </div>

        <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
          {menuItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-800 transition"
              title={!sidebarOpen ? item.name : ''}
            >
              <span className="text-xl">{item.icon}</span>
              {sidebarOpen && <span>{item.name}</span>}
            </Link>
          ))}
        </nav>

        <div className="p-4 border-t border-gray-700">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold">
              {user?.username?.charAt(0).toUpperCase()}
            </div>
            {sidebarOpen && (
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-sm truncate">{user?.username}</p>
                <p className="text-gray-400 text-xs truncate">{user?.email}</p>
              </div>
            )}
          </div>
          <button
            onClick={() => alert('Logout disabled - Demo mode')}
            className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-2 rounded transition"
          >
            {sidebarOpen ? 'Logout' : '🚪'}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="text-gray-600 hover:text-gray-900"
          >
            ☰
          </button>
          <div className="text-gray-600">
            Welcome, <span className="font-semibold">{user?.full_name}</span>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>
    </div>
  );
}
