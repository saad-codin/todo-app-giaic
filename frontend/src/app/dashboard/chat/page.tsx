'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User, Sparkles } from 'lucide-react';
import { api } from '@/lib/api';

const SUGGESTED_PROMPTS = [
  { label: 'Show my tasks', prompt: 'Show me all my pending tasks' },
  { label: 'Add a task', prompt: 'Add a new task: ' },
  { label: 'Complete a task', prompt: 'Mark my first task as complete' },
  { label: 'Search tasks', prompt: 'Find tasks related to work' },
];

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim() || isLoading) return;

    const userMsg: Message = { id: `${Date.now()}_u`, role: 'user', content: text.trim() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await api.sendChatMessage({ message: text.trim(), conversation_id: conversationId });
      setConversationId(res.conversation_id);
      const assistantMsg: Message = {
        id: `${Date.now()}_a`,
        role: 'assistant',
        content: res.response,
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch {
      setMessages(prev => [
        ...prev,
        { id: `${Date.now()}_e`, role: 'assistant', content: 'Sorry, something went wrong. Please try again.' },
      ]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  }, [isLoading, conversationId]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] max-w-3xl mx-auto p-4 sm:p-6">
      <div className="mb-4">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">AI Assistant</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
          Chat with your AI to manage tasks naturally
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto rounded-2xl border border-gray-100 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-sm p-4">
        {messages.length === 0 && !isLoading && (
          <div className="flex flex-col items-center justify-center h-full py-12 text-center">
            <div className="w-16 h-16 rounded-2xl bg-sage-100 dark:bg-sage-900/30 flex items-center justify-center mb-4">
              <Sparkles className="w-8 h-8 text-sage-600 dark:text-sage-400" />
            </div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
              Hi! I&apos;m your AI Todo Assistant
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-6 max-w-xs">
              Ask me to create, update, or find tasks. I can help you stay organized!
            </p>
            <div className="grid grid-cols-2 gap-2">
              {SUGGESTED_PROMPTS.map(({ label, prompt }) => (
                <button
                  key={label}
                  onClick={() => sendMessage(prompt)}
                  className="px-3 py-2 text-sm font-medium text-sage-700 dark:text-sage-400 bg-sage-50 dark:bg-sage-900/20 hover:bg-sage-100 dark:hover:bg-sage-900/40 border border-sage-200 dark:border-sage-800 rounded-xl transition-colors text-left"
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        )}

        <AnimatePresence initial={false}>
          {messages.map(msg => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex gap-3 mb-4 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
            >
              <div className={`w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 ${
                msg.role === 'user'
                  ? 'bg-sage-500'
                  : 'bg-gray-100 dark:bg-gray-700'
              }`}>
                {msg.role === 'user'
                  ? <User className="w-4 h-4 text-white" />
                  : <Bot className="w-4 h-4 text-gray-600 dark:text-gray-300" />
                }
              </div>
              <div className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap ${
                msg.role === 'user'
                  ? 'bg-sage-500 text-white rounded-tr-sm'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-tl-sm'
              }`}>
                {msg.content}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Typing indicator */}
        {isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex gap-3 mb-4"
          >
            <div className="w-8 h-8 rounded-xl bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
              <Bot className="w-4 h-4 text-gray-600 dark:text-gray-300" />
            </div>
            <div className="bg-gray-100 dark:bg-gray-700 rounded-2xl rounded-tl-sm px-4 py-3 flex gap-1 items-center">
              {[0, 1, 2].map(i => (
                <motion.div
                  key={i}
                  className="w-1.5 h-1.5 rounded-full bg-gray-400"
                  animate={{ y: [0, -4, 0] }}
                  transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.15 }}
                />
              ))}
            </div>
          </motion.div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="mt-3 flex gap-2 items-end bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm p-3">
        <textarea
          ref={inputRef}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask me to manage your tasks..."
          rows={1}
          className="flex-1 resize-none bg-transparent text-sm text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none overflow-y-auto"
          style={{ minHeight: '24px', maxHeight: '128px' }}
        />
        <button
          onClick={() => sendMessage(input)}
          disabled={!input.trim() || isLoading}
          className="w-9 h-9 rounded-xl bg-sage-500 hover:bg-sage-600 disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center transition-colors flex-shrink-0"
        >
          <Send className="w-4 h-4 text-white" />
        </button>
      </div>
    </div>
  );
}
