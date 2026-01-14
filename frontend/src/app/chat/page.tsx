'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Script from 'next/script';
import { ChatKit, useChatKit } from '@openai/chatkit-react';
import { useAuthContext } from '@/lib/auth';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function ChatPage() {
  const { user, isLoading: isAuthLoading } = useAuthContext();
  const router = useRouter();

  // ChatKit hook - connects to our custom backend with MCP tools
  const { control } = useChatKit({
    api: {
      // Point to our custom ChatKit server
      url: `${API_BASE}/api/chatkit`,
      // Custom fetch to include auth credentials
      fetch: async (input, init) => {
        return fetch(input, {
          ...init,
          credentials: 'include',
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
      console.error('ChatKit error:', error);
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
          <ChatKit
            control={control}
            className="h-[calc(100vh-10rem)] w-full"
          />
        </div>
      </main>
    </div>
  );
}
