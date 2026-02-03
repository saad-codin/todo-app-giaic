'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Script from 'next/script';
import { ChatKit, useChatKit } from '@openai/chatkit-react';
import { useAuthContext } from '@/lib/auth';
import { getAuthToken } from '@/lib/api';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const DOMAIN_KEY = process.env.NEXT_PUBLIC_CHATKIT_DOMAIN_KEY || '';

// Debug logging - remove in production
console.log('[ChatKit Debug] API_BASE:', API_BASE);
console.log('[ChatKit Debug] DOMAIN_KEY exists:', !!DOMAIN_KEY);
console.log('[ChatKit Debug] DOMAIN_KEY length:', DOMAIN_KEY.length);

export default function ChatPage() {
  const { user, isLoading: isAuthLoading } = useAuthContext();
  const router = useRouter();
  const [chatKitError, setChatKitError] = useState<string | null>(null);

  // Check for missing configuration
  useEffect(() => {
    if (!DOMAIN_KEY) {
      console.error('[ChatKit Error] NEXT_PUBLIC_CHATKIT_DOMAIN_KEY is not set!');
      setChatKitError('ChatKit domain key is not configured. Please set NEXT_PUBLIC_CHATKIT_DOMAIN_KEY in environment variables.');
    }
    if (!API_BASE || API_BASE === 'http://localhost:8000') {
      console.warn('[ChatKit Warning] Using default/localhost API_BASE:', API_BASE);
    }
  }, []);

  // ChatKit hook - connects to our custom backend with MCP tools
  const { control } = useChatKit({
    api: {
      // Point to our custom ChatKit server
      url: `${API_BASE}/api/chatkit`,
      // Domain key from OpenAI (required for custom backends)
      domainKey: DOMAIN_KEY,
      // Custom fetch to include auth credentials
      fetch: async (input, init) => {
        const token = getAuthToken();
        console.log('[ChatKit Debug] Making request to:', input);
        console.log('[ChatKit Debug] Auth token exists:', !!token);
        return fetch(input, {
          ...init,
          credentials: 'include',
          headers: {
            ...init?.headers,
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
        });
      },
    },
    // Start screen with todo-specific prompts
    startScreen: {
      greeting: 'Hi! I\'m your AI Todo Assistant. How can I help you manage your tasks today?',
      prompts: [
        {
          label: 'Add a task',
          prompt: 'Add a new task: Buy groceries tomorrow',
        },
        {
          label: 'Show my tasks',
          prompt: 'Show me all my pending tasks',
        },
        {
          label: 'Complete a task',
          prompt: 'Mark my first task as complete',
        },
        {
          label: 'Search tasks',
          prompt: 'Search for tasks related to work',
        },
      ],
    },
    theme: 'light',
    onError: ({ error }) => {
      console.error('[ChatKit Error]:', error);
      setChatKitError(error?.message || 'ChatKit encountered an error');
    },
  });

  // Redirect to signin if not authenticated
  useEffect(() => {
    if (!isAuthLoading && !user) {
      router.push('/signin');
    }
  }, [isAuthLoading, user, router]);

  if (isAuthLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ChatKit Script - required for the component to work */}
      <Script
        src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js"
        strategy="beforeInteractive"
      />

      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <a href="/dashboard" className="text-gray-600 hover:text-gray-900">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                  stroke="currentColor"
                  className="w-6 h-6"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18"
                  />
                </svg>
              </a>
              <h1 className="text-xl font-semibold text-gray-900">
                AI Todo Assistant
              </h1>
            </div>
            <div className="text-sm text-gray-500">
              {user?.email}
            </div>
          </div>
        </div>
      </header>

      {/* Main content - ChatKit */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          {chatKitError ? (
            <div className="h-[calc(100vh-10rem)] w-full flex items-center justify-center p-8">
              <div className="text-center">
                <div className="text-red-500 text-6xl mb-4">⚠️</div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">ChatKit Configuration Error</h2>
                <p className="text-gray-600 mb-4">{chatKitError}</p>
                <div className="text-sm text-gray-500 bg-gray-100 p-4 rounded-lg text-left">
                  <p className="font-semibold mb-2">Debug Info:</p>
                  <p>API_BASE: {API_BASE}</p>
                  <p>DOMAIN_KEY set: {DOMAIN_KEY ? 'Yes' : 'No'}</p>
                  <p>DOMAIN_KEY length: {DOMAIN_KEY.length}</p>
                </div>
              </div>
            </div>
          ) : (
            <ChatKit
              control={control}
              className="h-[calc(100vh-10rem)] w-full"
            />
          )}
        </div>
      </main>
    </div>
  );
}
