'use client';

import { useState } from 'react';
import { searchAPI } from '@/lib/api-client';

interface SearchResult {
  id: number;
  entity_type: string;
  title: string;
  description?: string;
  relevance_score: number;
  url: string;
}

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [suggestions, setSuggestions] = useState<any[]>([]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      const response = await searchAPI.global(query);
      if (response.data) {
        setResults((response.data as any).results || []);
      }
      setSearched(true);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = async (value: string) => {
    setQuery(value);
    if (value.length > 2) {
      const response = await searchAPI.getSuggestions(value);
      if (response.data) {
        setSuggestions((response.data as any).suggestions || []);
      }
    } else {
      setSuggestions([]);
    }
  };

  const getEntityIcon = (type: string) => {
    switch (type) {
      case 'workflow':
        return '⚙️';
      case 'agent':
        return '🤖';
      case 'file':
        return '📁';
      case 'user':
        return '👤';
      case 'integration':
        return '🔗';
      default:
        return '📄';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Search</h1>
        <p className="text-gray-600 mt-1">Find workflows, agents, files and more</p>
      </div>

      {/* Search Box */}
      <form onSubmit={handleSearch} className="relative">
        <div className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => handleInputChange(e.target.value)}
            placeholder="Search across platform..."
            className="w-full px-6 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-lg"
            autoFocus
          />
          <button
            type="submit"
            className="absolute right-4 top-1/2 transform -translate-y-1/2 text-blue-600 hover:text-blue-700 text-2xl"
          >
            🔍
          </button>

          {/* Suggestions */}
          {suggestions.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-2 bg-white border border-gray-300 rounded-lg shadow-lg z-10">
              {suggestions.slice(0, 5).map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => {
                    setQuery(suggestion.suggestion);
                    setSuggestions([]);
                  }}
                  className="w-full text-left px-6 py-3 hover:bg-gray-50 border-b last:border-b-0"
                >
                  🔍 {suggestion.suggestion}
                </button>
              ))}
            </div>
          )}
        </div>
      </form>

      {/* Results */}
      {loading && (
        <div className="text-center py-12">
          <p className="text-gray-600">Searching...</p>
        </div>
      )}

      {searched && !loading && results.length === 0 && (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-600">No results found for "{query}"</p>
        </div>
      )}

      {results.length > 0 && (
        <div className="space-y-4">
          <p className="text-gray-600">
            Found {results.length} result{results.length !== 1 ? 's' : ''}
          </p>
          {results.map((result) => (
            <a
              key={result.id}
              href={result.url}
              className="block bg-white rounded-lg shadow hover:shadow-lg transition p-6"
            >
              <div className="flex items-start gap-4">
                <div className="text-3xl">{getEntityIcon(result.entity_type)}</div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">{result.title}</h3>
                  {result.description && (
                    <p className="text-gray-600 text-sm mt-1">{result.description}</p>
                  )}
                  <div className="mt-3 flex items-center gap-4">
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                      {result.entity_type}
                    </span>
                    <span className="text-xs text-gray-500">
                      Relevance: {(result.relevance_score * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>
            </a>
          ))}
        </div>
      )}

      {!searched && results.length === 0 && (
        <div className="bg-white rounded-lg shadow p-12">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Search Tips</h2>
          <ul className="space-y-2 text-gray-600">
            <li>💡 Use keywords to find workflows, agents, and files</li>
            <li>🏷️ Filter by entity type (workflow, agent, file, etc.)</li>
            <li>⏱️ View your search history</li>
            <li>⭐ Save frequently used searches</li>
          </ul>
        </div>
      )}
    </div>
  );
}
