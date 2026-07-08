import { USER_COLOR } from '../theme/brand';
import { DEFAULT_MODELS } from '../core/llm/constants';

export const USER_ID = 'user';
export const USER_NAME = 'CEO (Surya)';
export const MAX_AGENTS = 20;
export { USER_COLOR };
export const DEFAULT_AGENTIC_SET_ID = 'omni-global';

export interface AgentNode {
  id: string;
  index: number;
  name: string;
  description: string;
  color: string;
  model: string;
  humanInTheLoop?: boolean;
  position?: { x: number; y: number };
  subagents?: AgentNode[];
}

export type OutputType = 'text' | 'image' | 'music' | 'video';

export interface AgenticSystem {
  id: string;
  teamName: string;
  teamType: string;
  teamDescription: string;
  color: string;
  outputType: OutputType;
  outputModel: string;
  outputAutoApprove?: boolean;
  user: {
    index: number;
    model: string;
    position?: { x: number; y: number };
  };
  leadAgent: AgentNode;
}

export const AGENTIC_SETS: AgenticSystem[] = [
  {
    id: 'omni-global',
    teamName: 'Omni-MNC Global HQ',
    teamType: 'Complete Enterprise',
    teamDescription: 'The full 20-agent workforce of Tecno Spark Solutions collaborating live in one unified space.',
    color: '#0EA5E9',
    outputType: 'text',
    outputModel: DEFAULT_MODELS.text,
    outputAutoApprove: true,
    user: { index: 0, model: 'CEO', position: { x: 0, y: 0 } },
    leadAgent: {
      id: 'super-brain',
      index: 1,
      name: 'Super Brain (CEO Router)',
      description: 'Supreme brain router. Directs tasks across the company.',
      color: '#0EA5E9',
      model: 'llama-3.3-70b',
      humanInTheLoop: true,
      position: { x: 0, y: 100 },
      subagents: [
        {
          id: 'campaign-manager',
          index: 2,
          name: 'Campaign Manager (COO)',
          description: 'Orchestrates operations, timelines, and sector coordination.',
          color: '#34A853',
          model: 'llama-3.3-70b',
          position: { x: -350, y: 220 }
        },
        {
          id: 'chief-architect',
          index: 3,
          name: 'Chief Architect (CTO)',
          description: 'System architect. Structures files and plans code features.',
          color: '#10B981',
          model: 'qwen-2.5-coder',
          position: { x: -150, y: 220 }
        },
        {
          id: 'security-agent',
          index: 4,
          name: 'Security Agent',
          description: 'Intruder detection, locking triggers, and visual checks.',
          color: '#EF4444',
          model: 'llama-3.1-8b',
          position: { x: 150, y: 220 }
        },
        {
          id: 'finance-agent',
          index: 5,
          name: 'Finance Agent',
          description: 'Parses token pricing, spend analytics, and budget tracking.',
          color: '#FBBF24',
          model: 'llama-3-8b',
          position: { x: 350, y: 220 }
        },
        {
          id: 'legal-agent',
          index: 6,
          name: 'Legal Agent',
          description: 'Checks copywriting compliance and legal clearance.',
          color: '#6366F1',
          model: 'llama-3.3-70b',
          position: { x: -450, y: 350 }
        },
        {
          id: 'coder-agent',
          index: 7,
          name: 'Coder Agent',
          description: 'Writes Python scripts, REST routes, and UI components.',
          color: '#3B82F6',
          model: 'qwen-2.5-coder',
          position: { x: -300, y: 350 }
        },
        {
          id: 'qa-agent',
          index: 8,
          name: 'QA Agent',
          description: 'Performs code lint checks, tests, and finds bugs.',
          color: '#EC4899',
          model: 'qwen-2.5-coder',
          position: { x: -150, y: 350 }
        },
        {
          id: 'devops-agent',
          index: 9,
          name: 'DevOps Agent',
          description: 'Sets up Docker layers, configs, and maintains server state.',
          color: '#06B6D4',
          model: 'llama-3-8b',
          position: { x: 0, y: 350 }
        },
        {
          id: 'research-agent',
          index: 10,
          name: 'Research Agent',
          description: 'Scrapes web sources and analyzes competitor products.',
          color: '#F59E0B',
          model: 'llama-3-8b',
          position: { x: 150, y: 350 }
        },
        {
          id: 'copywriter-agent',
          index: 11,
          name: 'Copywriter Agent',
          description: 'Writes creative copywriting scripts and social media briefs.',
          color: '#A855F7',
          model: 'gemma-4-31b',
          position: { x: 300, y: 350 }
        },
        {
          id: 'art-director',
          index: 12,
          name: 'Art Director',
          description: 'Writes visual prompts and directs visual styling.',
          color: '#14B8A6',
          model: 'gemma-4-31b',
          position: { x: 450, y: 350 }
        },
        {
          id: 'graphic-engine',
          index: 13,
          name: 'Graphic Engine',
          description: 'Compiles layout instructions and overlays copy on plates.',
          color: '#EAB308',
          model: 'llama-3.1-8b',
          position: { x: -450, y: 480 }
        },
        {
          id: 'social-media-agent',
          index: 14,
          name: 'Social Media Agent',
          description: 'Drafts social channel posts, scheduling, and metrics.',
          color: '#F43F5E',
          model: 'gemma-4-31b',
          position: { x: -300, y: 480 }
        },
        {
          id: 'email-agent',
          index: 15,
          name: 'Email Agent',
          description: 'Monitors professional mail queue and drafts replies.',
          color: '#10B981',
          model: 'llama-3-8b',
          position: { x: -150, y: 480 }
        },
        {
          id: 'calendar-agent',
          index: 16,
          name: 'Calendar Agent',
          description: 'Sets calendar events, timings, and schedules alerts.',
          color: '#84CC16',
          model: 'llama-3-8b',
          position: { x: 0, y: 480 }
        },
        {
          id: 'comms-agent',
          index: 17,
          name: 'Comms Agent',
          description: 'Sends alerts, connects SMS channels, and controls shims.',
          color: '#D946EF',
          model: 'llama-3.1-8b',
          position: { x: 150, y: 480 }
        },
        {
          id: 'memory-agent',
          index: 18,
          name: 'Memory Agent',
          description: 'Maintains long-term SQLite memory indexes.',
          color: '#6366F1',
          model: 'llama-3-8b',
          position: { x: 300, y: 480 }
        },
        {
          id: 'retrieval-agent',
          index: 19,
          name: 'Retrieval Agent',
          description: 'Finds past conversation contexts in Vector indexes.',
          color: '#A855F7',
          model: 'llama-3-8b',
          position: { x: 450, y: 480 }
        },
        {
          id: 'analytics-agent',
          index: 20,
          name: 'Analytics Agent',
          description: 'Tracks performance reports and writes corporate stats.',
          color: '#06B6D4',
          model: 'llama-3-8b',
          position: { x: 0, y: 600 }
        }
      ]
    }
  }
];

export function getAgentSet(id: string, customSystems: AgenticSystem[] = []): AgenticSystem {
  return (
    customSystems.find((s) => s.id === id) ||
    AGENTIC_SETS.find((s) => s.id === id) ||
    AGENTIC_SETS[0]
  );
}

export function getAllAgents(system: AgenticSystem): AgentNode[] {
  const agents: AgentNode[] = [];
  const traverse = (node: AgentNode) => {
    agents.push(node);
    if (node.subagents) {
      node.subagents.forEach(traverse);
    }
  };
  traverse(system.leadAgent);
  return agents;
}

export function getAllCharacters(system: AgenticSystem): AgentNode[] {
  const userNode: AgentNode = {
    id: USER_ID,
    index: system.user.index,
    name: USER_NAME,
    color: USER_COLOR,
    model: system.user.model,
    description: 'Human user issuing commands.',
  };
  return [userNode, ...getAllAgents(system)];
}
