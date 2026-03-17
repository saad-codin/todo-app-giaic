'use client';

import { useEffect, useRef, useCallback, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';

interface WsMessage {
  type: string;
  [key: string]: any;
}

interface UseWebSocketOptions {
  url: string;
  token: string | null;
  onMessage?: (message: WsMessage) => void;
  enabled?: boolean;
}

export function useWebSocket({ url, token, onMessage, enabled = true }: UseWebSocketOptions) {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  const [isConnected, setIsConnected] = useState(false);
  const queryClient = useQueryClient();

  const maxReconnectAttempts = 10;
  const baseDelay = 1000; // 1 second

  const connect = useCallback(() => {
    if (!token || !enabled) return;

    const wsUrl = `${url}?token=${token}`;

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        reconnectAttempts.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const message: WsMessage = JSON.parse(event.data);

          // Handle task updates - invalidate React Query cache
          if (message.type === 'task_update') {
            queryClient.invalidateQueries({ queryKey: ['tasks'] });
          }

          // Forward to custom handler
          if (onMessage) {
            onMessage(message);
          }
        } catch (e) {
          // Ignore parse errors
        }
      };

      ws.onclose = (event) => {
        setIsConnected(false);
        wsRef.current = null;

        // Reconnect with exponential backoff
        if (reconnectAttempts.current < maxReconnectAttempts && enabled) {
          const delay = Math.min(baseDelay * Math.pow(2, reconnectAttempts.current), 30000);
          reconnectAttempts.current += 1;
          reconnectTimeoutRef.current = setTimeout(connect, delay);
        }
      };

      ws.onerror = () => {
        // onclose will be called after onerror
      };
    } catch (e) {
      // Connection failed, will retry via onclose
    }
  }, [url, token, enabled, onMessage, queryClient]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  return { isConnected };
}
