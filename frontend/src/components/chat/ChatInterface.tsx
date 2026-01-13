'use client';

import { useState, useCallback } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api, ChatMessage, ChatResponse } from '@/lib/api';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';

interface ChatInterfaceProps {
  conversationId?: string;
  onConversationChange?: (id: string) => void;
}

export function ChatInterface({
  conversationId: initialConversationId,
  onConversationChange,
}: ChatInterfaceProps) {
  const [conversationId, setConversationId] = useState<string | undefined>(
    initialConversationId
  );
  const [localMessages, setLocalMessages] = useState<ChatMessage[]>([]);
  const queryClient = useQueryClient();

  // Load conversation history if we have a conversation ID
  const { data: conversationData, isLoading: isLoadingHistory } = useQuery({
    queryKey: ['conversation', conversationId],
    queryFn: () => api.getConversation(conversationId!),
    enabled: !!conversationId,
  });

  // Combine server messages with local optimistic messages
  const messages = conversationData?.messages || localMessages;

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: api.sendChatMessage,
    onSuccess: (response: ChatResponse) => {
      // Update conversation ID if this is a new conversation
      if (!conversationId && response.conversation_id) {
        setConversationId(response.conversation_id);
        onConversationChange?.(response.conversation_id);
      }

      // Create assistant message from response
      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.response,
        tool_calls: response.tool_results
          ? { results: response.tool_results }
          : undefined,
        created_at: new Date().toISOString(),
      };

      // Update local messages
      setLocalMessages((prev) => [...prev, assistantMessage]);

      // Invalidate conversation query to refresh from server
      if (conversationId || response.conversation_id) {
        queryClient.invalidateQueries({
          queryKey: ['conversation', conversationId || response.conversation_id],
        });
        queryClient.invalidateQueries({
          queryKey: ['conversations'],
        });
      }

      // Invalidate tasks query since AI might have modified tasks
      queryClient.invalidateQueries({
        queryKey: ['tasks'],
      });
    },
  });

  const handleSendMessage = useCallback(
    (message: string) => {
      // Create optimistic user message
      const userMessage: ChatMessage = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: message,
        created_at: new Date().toISOString(),
      };

      // Add to local messages immediately
      setLocalMessages((prev) => [...prev, userMessage]);

      // Send to API
      sendMessageMutation.mutate({
        message,
        conversation_id: conversationId,
      });
    },
    [conversationId, sendMessageMutation]
  );

  const handleNewConversation = useCallback(() => {
    setConversationId(undefined);
    setLocalMessages([]);
    onConversationChange?.('');
  }, [onConversationChange]);

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Chat Assistant</h2>
        <button
          onClick={handleNewConversation}
          className="text-sm text-blue-600 hover:text-blue-700 focus:outline-none"
        >
          New Chat
        </button>
      </div>

      {/* Messages */}
      <MessageList
        messages={messages}
        isLoading={sendMessageMutation.isPending || isLoadingHistory}
      />

      {/* Input */}
      <MessageInput
        onSend={handleSendMessage}
        disabled={sendMessageMutation.isPending}
        placeholder="Ask me to add, list, complete, or update tasks..."
      />
    </div>
  );
}
