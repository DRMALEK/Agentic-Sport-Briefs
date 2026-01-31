import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface AgentRequest {
  goal: string;
  session_id?: string;
  use_knowledge?: boolean;
}

export interface AgentResponse {
  success: boolean;
  plan: {
    plan: string;
    steps: string[];
    total_steps: number;
  };
  response: string;
  tool_calls: Array<{
    tool: string;
    arguments: any;
    result: any;
    requires_approval?: boolean;
  }>;
  activity_log: Array<{
    step: string;
    action: string;
    status: string;
    result?: any;
    requires_approval?: boolean;
  }>;
  knowledge_used: Array<{
    source: string;
    category?: string;
    relevance?: string;
    influence?: string;
  }>;
  session_id: string;
}

export interface Brief {
  id: number;
  title: string;
  content: string;
  category: string;
  created_at: string;
}

export interface Knowledge {
  id: number;
  title: string;
  content: string;
  category: string;
  created_at: string;
}

export const agentAPI = {
  executeAgent: (request: AgentRequest): Promise<AgentResponse> =>
    api.post('/api/agent/execute', request).then(res => res.data),
  
  approveAction: (sessionId: string, toolCallIndex: number, approved: boolean) =>
    api.post('/api/agent/approve', { session_id: sessionId, tool_call_index: toolCallIndex, approved }).then(res => res.data),
};

export const briefsAPI = {
  getBriefs: (): Promise<{ briefs: Brief[] }> =>
    api.get('/api/briefs').then(res => res.data),
  
  getBrief: (id: number): Promise<Brief> =>
    api.get(`/api/briefs/${id}`).then(res => res.data),
  
  createBrief: (brief: { title: string; content: string; category: string }) =>
    api.post('/api/briefs', brief).then(res => res.data),
  
  deleteBrief: (id: number) =>
    api.delete(`/api/briefs/${id}`).then(res => res.data),
  
  deleteAllBriefs: () =>
    api.delete('/api/briefs').then(res => res.data),
};

export const knowledgeAPI = {
  getKnowledge: (category?: string): Promise<{ knowledge: Knowledge[] }> =>
    api.get('/api/knowledge', { params: { category } }).then(res => res.data),
  
  createKnowledge: (knowledge: { title: string; content: string; category: string }) =>
    api.post('/api/knowledge', knowledge).then(res => res.data),
  
  uploadKnowledge: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/knowledge/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(res => res.data);
  },
};

export const statsAPI = {
  getStats: () =>
    api.get('/api/stats').then(res => res.data),
};

export default api;
