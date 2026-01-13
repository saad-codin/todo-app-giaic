'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { ChatInterface } from '@/components/chat/ChatInterface';
import { api, ConversationSummary } from '@/lib/api';
import { useAuthContext } from '@/lib/auth';

export default function ChatPage() {
  const { user, isLoading: isAuthLoading } = useAuthContext();
  const router = useRouter();
  const [selectedConversationId, setSelectedConversationId] = useState<string>();

  // Redirect to signin if not authenticated
  if (!isAuthLoading && !user) {
    router.push('/signin');
    return null;
  }

  // Fetch conversations list
  const { data: conversationsData } = useQuery({
    queryKey: ['conversations'],
    queryFn: () => api.getConversations(10),
    enabled: !!user,
  });

  const conversations = conversationsData?.conversations || [];

  const handleConversationChange = (id: string) => {
    setSelectedConversationId(id || undefined);
  };

  const handleSelectConversation = (conv: ConversationSummary) => {
    setSelectedConversationId(conv.id);
  };

  if (isAuthLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
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

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex gap-6 h-[calc(100vh-8rem)]">
          {/* Sidebar - Conversation History */}
          <aside className="w-64 flex-shrink-0 hidden md:block">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 h-full overflow-hidden">
              <div className="px-4 py-3 border-b border-gray-200">
                <h3 className="font-medium text-gray-900">Conversations</h3>
              </div>
              <div className="overflow-y-auto h-[calc(100%-3rem)]">
                {conversations.length === 0 ? (
                  <p className="px-4 py-3 text-sm text-gray-500">
                    No conversations yet
                  </p>
                ) : (
                  <ul className="divide-y divide-gray-100">
                    {conversations.map((conv) => (
                      <li key={conv.id}>
                        <button
                          onClick={() => handleSelectConversation(conv)}
                          className={`w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors ${
                            selectedConversationId === conv.id
                              ? 'bg-blue-50 border-l-2 border-blue-600'
                              : ''
                          }`}
                        >
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {conv.title || 'New conversation'}
                          </p>
                          <p className="text-xs text-gray-500 mt-1">
                            {new Date(conv.updated_at).toLocaleDateString()} ·{' '}
                            {conv.message_count} messages
                          </p>
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          </aside>

          {/* Chat Interface */}
          <div className="flex-1">
            <ChatInterface
              conversationId={selectedConversationId}
              onConversationChange={handleConversationChange}
            />
          </div>
        </div>
      </main>
    </div>
  );
}
