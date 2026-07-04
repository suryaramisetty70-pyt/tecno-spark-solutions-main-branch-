'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import { apiClient } from '@/lib/api-client';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'agent';
  content: string;
  agent?: string;
  timestamp: Date;
}

export default function BuddyChat() {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<string>('personal_assistant');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Welcome message
    setMessages([
      {
        id: '1',
        role: 'assistant',
        content: `👋 Welcome to Buddy AI OS! I'm your personal AI assistant. You can chat with me about anything, and I'll coordinate with specialized agents to help you. What can I do for you today?`,
        timestamp: new Date(),
      },
    ]);
  }, []);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Send to Buddy Core API
      const response = await apiClient.post('/api/v1/agents/chat', {
        user_id: user?.id || 'guest',
        intent: input,
        agent_id: selectedAgent,
        context: {
          conversation_history: messages.slice(-5).map(m => m.content),
        },
      });

      if (response.data) {
        const data = response.data as any;

        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'agent',
          agent: data.agent_id || selectedAgent,
          content:
            typeof data.response === 'string'
              ? data.response
              : data.message || JSON.stringify(data.response || data),
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, assistantMessage]);
      } else {
        const error: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: response.error || 'Sorry, I encountered an error processing your request.',
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, error]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const error_msg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content:
          'Sorry, I encountered a network error. Please try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, error_msg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-b from-slate-50 to-slate-100">
      {/* Header */}
      <div className="bg-white border-b border-slate-200 p-4 shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">🤖 Buddy Chat</h1>
            <p className="text-sm text-slate-500">AI-powered assistance with agent coordination</p>
          </div>
          <div className="flex items-center gap-2">
            <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
              ● Online
            </span>
          </div>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
                message.role === 'user'
                  ? 'bg-blue-500 text-white rounded-br-none'
                  : 'bg-white text-slate-900 border border-slate-200 rounded-bl-none shadow-sm'
              }`}
            >
              {message.agent && message.role !== 'user' && (
                <p className="text-xs font-semibold mb-1 opacity-70">
                  {message.agent === 'personal_assistant'
                    ? '🤖 Personal Assistant'
                    : `🔷 ${message.agent}`}
                </p>
              )}
              <p className="text-sm break-words">{message.content}</p>
              <p
                className={`text-xs mt-1 ${
                  message.role === 'user' ? 'text-blue-100' : 'text-slate-500'
                }`}
              >
                {message.timestamp.toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </p>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-slate-200 px-4 py-3 rounded-lg rounded-bl-none shadow-sm">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-100"></div>
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-200"></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Agent Selector */}
      <div className="bg-white border-t border-slate-200 px-4 py-3">
        <p className="text-xs font-semibold text-slate-700 mb-2">Route to Agent:</p>
        <div className="flex gap-2 overflow-x-auto pb-2">
          <button
            onClick={() => setSelectedAgent('personal_assistant')}
            className={`px-3 py-1 rounded-full text-sm font-medium whitespace-nowrap transition ${
              selectedAgent === 'personal_assistant'
                ? 'bg-blue-500 text-white'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            🤖 General
          </button>
          <button
            onClick={() => setSelectedAgent('memory_agent')}
            className={`px-3 py-1 rounded-full text-sm font-medium whitespace-nowrap transition ${
              selectedAgent === 'memory_agent'
                ? 'bg-blue-500 text-white'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            💾 Memory
          </button>
          <button
            onClick={() => setSelectedAgent('productivity_agent')}
            className={`px-3 py-1 rounded-full text-sm font-medium whitespace-nowrap transition ${
              selectedAgent === 'productivity_agent'
                ? 'bg-blue-500 text-white'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            ✓ Tasks
          </button>
          <button
            onClick={() => setSelectedAgent('email_agent')}
            className={`px-3 py-1 rounded-full text-sm font-medium whitespace-nowrap transition ${
              selectedAgent === 'email_agent'
                ? 'bg-blue-500 text-white'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            📧 Email
          </button>
          <button
            onClick={() => setSelectedAgent('researcher_agent')}
            className={`px-3 py-1 rounded-full text-sm font-medium whitespace-nowrap transition ${
              selectedAgent === 'researcher_agent'
                ? 'bg-blue-500 text-white'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            🔍 Research
          </button>
        </div>
      </div>

      {/* Input Area */}
      <form
        onSubmit={handleSendMessage}
        className="bg-white border-t border-slate-200 p-4 shadow-lg"
      >
        <div className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message... Ask me anything!"
            disabled={loading}
            className="flex-1 px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-slate-100"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-6 py-3 bg-blue-500 text-white font-medium rounded-lg hover:bg-blue-600 disabled:bg-slate-300 disabled:cursor-not-allowed transition"
          >
            {loading ? '...' : 'Send'}
          </button>
        </div>
        <p className="text-xs text-slate-500 mt-2">
          💡 Tip: You can ask me anything and I'll coordinate the right agents to help!
        </p>
      </form>
    </div>
  );
}
