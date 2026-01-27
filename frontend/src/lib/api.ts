import { ApiError } from '@/types/api';
import type {
  SignUpRequest,
  SignInRequest,
  AuthResponse,
  CreateTaskRequest,
  CreateTaskResponse,
  UpdateTaskRequest,
  UpdateTaskResponse,
  ListTasksRequest,
  ListTasksResponse,
  CompleteTaskResponse,
} from '@/types/api';
import type { Task, User } from '@/types/task';

// Chat types
export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ToolResult {
  tool: string;
  success: boolean;
  task_id?: string;
  count?: number;
  error?: string;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  tool_results?: ToolResult[];
}

export interface ConversationSummary {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ConversationListResponse {
  conversations: ConversationSummary[];
  total: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'tool';
  content: string;
  tool_calls?: Record<string, unknown>;
  created_at: string;
}

export interface ConversationDetailResponse {
  id: string;
  title: string | null;
  messages: ChatMessage[];
  created_at: string;
  updated_at: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Token storage
let authToken: string | null = null;

export function setAuthToken(token: string | null) {
  authToken = token;
  if (typeof window !== 'undefined') {
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  }
}

export function getAuthToken(): string | null {
  if (authToken) return authToken;
  if (typeof window !== 'undefined') {
    authToken = localStorage.getItem('auth_token');
  }
  return authToken;
}

async function fetchWithAuth<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAuthToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    credentials: 'include', // Still include for cookie fallback
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new ApiError(response.status, error.message || 'Request failed', error.code);
  }

  return response.json();
}

function buildQueryString(params: object): string {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.append(key, String(value));
    }
  });
  const query = searchParams.toString();
  return query ? `?${query}` : '';
}

export const api = {
  // Auth endpoints
  signUp: async (data: SignUpRequest) => {
    const response = await fetchWithAuth<AuthResponse & { token?: string }>('/api/auth/signup', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    if (response.token) {
      setAuthToken(response.token);
    }
    return response;
  },

  signIn: async (data: SignInRequest) => {
    const response = await fetchWithAuth<AuthResponse & { token?: string }>('/api/auth/signin', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    if (response.token) {
      setAuthToken(response.token);
    }
    return response;
  },

  signOut: async () => {
    setAuthToken(null);
    return fetchWithAuth<{ success: boolean }>('/api/auth/signout', {
      method: 'POST',
    });
  },

  getMe: () =>
    fetchWithAuth<{ user: User }>('/api/auth/me'),

  // Task endpoints
  getTasks: (params?: ListTasksRequest) =>
    fetchWithAuth<ListTasksResponse>(`/api/tasks${buildQueryString(params || {})}`),

  getTask: (id: string) =>
    fetchWithAuth<{ task: Task }>(`/api/tasks/${id}`),

  createTask: (data: CreateTaskRequest) =>
    fetchWithAuth<CreateTaskResponse>('/api/tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateTask: (id: string, data: UpdateTaskRequest) =>
    fetchWithAuth<UpdateTaskResponse>(`/api/tasks/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  deleteTask: (id: string) =>
    fetchWithAuth<{ success: boolean }>(`/api/tasks/${id}`, {
      method: 'DELETE',
    }),

  completeTask: (id: string) =>
    fetchWithAuth<CompleteTaskResponse>(`/api/tasks/${id}/complete`, {
      method: 'POST',
    }),

  incompleteTask: (id: string) =>
    fetchWithAuth<{ task: Task }>(`/api/tasks/${id}/incomplete`, {
      method: 'POST',
    }),

  // Chat endpoints
  sendChatMessage: (data: ChatRequest) =>
    fetchWithAuth<ChatResponse>('/api/chat', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getConversations: (limit?: number) =>
    fetchWithAuth<ConversationListResponse>(
      `/api/chat/conversations${limit ? `?limit=${limit}` : ''}`
    ),

  getConversation: (id: string, limit?: number) =>
    fetchWithAuth<ConversationDetailResponse>(
      `/api/chat/conversations/${id}${limit ? `?limit=${limit}` : ''}`
    ),
};

export { ApiError };
