"use client";

import { useState } from 'react';

export default function OmniCommandCenter() {
  const [directive, setDirective] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [terminalOutput, setTerminalOutput] = useState<string[]>([]);
  const [brainUsed, setBrainUsed] = useState('Standby');

  const handleCommandSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!directive.trim()) return;

    setIsProcessing(true);
    setTerminalOutput(prev => [...prev, `[CEO]: ${directive}`]);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
      const response = await fetch(`${apiUrl}/api/command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ directive }),
      });

      const data = await response.json();
      setBrainUsed(data.brain_used);
      
      setTerminalOutput(prev => [
        ...prev,
        `⚡ [ROUTING] Super Brain selected: ${data.brain_used}`,
        `[SUPER PA] Response: ${data.super_pa_response.substring(0, 200)}...`,
        `[SYSTEM] Task delegated to sectors: ${data.active_sectors.join(', ')}`
      ]);

    } catch (error) {
      setTerminalOutput(prev => [...prev, `[ERROR]: Failed to connect to Omni-MNC Backend on port 8001.`]);
    }

    setIsProcessing(false);
    setDirective('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-black text-white p-8 font-sans">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-700 pb-6">
          <div>
            <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-cyan-300">
              Omni-MNC Command Center
            </h1>
            <p className="text-slate-400 mt-2">Active AI Employees: 1,040 | Database: Synchronized</p>
          </div>
          <div className="text-right">
            <div className="text-sm text-slate-500 uppercase tracking-widest">Active Brain</div>
            <div className="text-xl font-mono text-cyan-400 animate-pulse">{brainUsed}</div>
          </div>
        </div>

        {/* Main Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Sectors Overview (Left) */}
          <div className="col-span-1 space-y-6">
            <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700 backdrop-blur-md">
              <h2 className="text-xl font-semibold mb-4 text-blue-300">Macro-Sectors</h2>
              <ul className="space-y-4">
                {['Banking & Finance', 'Tech & Software', 'Manufacturing', 'Legal & Govt'].map((sector) => (
                  <li key={sector} className="flex justify-between items-center bg-slate-900/50 p-3 rounded-lg border border-slate-700">
                    <span className="font-medium text-slate-200">{sector}</span>
                    <span className="flex h-3 w-3 relative">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Terminal & Command Input (Right) */}
          <div className="col-span-2 flex flex-col space-y-6">
            
            {/* Terminal Window */}
            <div className="bg-black p-6 rounded-2xl border border-slate-700 font-mono text-sm h-96 overflow-y-auto shadow-[0_0_15px_rgba(34,211,238,0.1)]">
              {terminalOutput.length === 0 ? (
                <div className="text-slate-500">Awaiting CEO Directive...</div>
              ) : (
                terminalOutput.map((line, i) => (
                  <div key={i} className={`mb-2 ${line.startsWith('[CEO]') ? 'text-blue-400' : line.startsWith('[ERROR]') ? 'text-red-500' : 'text-green-400'}`}>
                    {line}
                  </div>
                ))
              )}
              {isProcessing && <div className="text-yellow-400 mt-2 animate-pulse">Processing directive through Super Brain...</div>}
            </div>

            {/* Input Form */}
            <form onSubmit={handleCommandSubmit} className="relative">
              <input 
                type="text" 
                value={directive}
                onChange={(e) => setDirective(e.target.value)}
                placeholder="Enter global CEO directive..."
                className="w-full bg-slate-800/50 border border-slate-700 text-white rounded-xl py-4 px-6 pr-32 focus:outline-none focus:ring-2 focus:ring-blue-500 backdrop-blur-md"
                disabled={isProcessing}
              />
              <button 
                type="submit" 
                disabled={isProcessing || !directive.trim()}
                className="absolute right-2 top-2 bottom-2 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-bold py-2 px-6 rounded-lg transition-all shadow-[0_0_10px_rgba(34,211,238,0.5)] disabled:opacity-50"
              >
                EXECUTE
              </button>
            </form>
            
          </div>
        </div>

      </div>
    </div>
  );
}
