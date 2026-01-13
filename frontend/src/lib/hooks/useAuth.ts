'use client';

import { useState, useEffect, useCallback, ReactNode, createElement } from 'react';
import { useRouter } from 'next/navigation';
import { api, ApiError } from '@/lib/api';
import { AuthContext, AuthContextType } from '@/lib/auth';
import type { User } from '@/types/task';

function useAuthState(): AuthContextType {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  const checkAuth = useCallback(async () => {
    try {
      setIsLoading(true);
      const { user } = await api.getMe();
      setUser(user);
    } catch (error) {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const signIn = useCallback(async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const { user } = await api.signIn({ email, password });
      setUser(user);
      router.push('/');
    } catch (error) {
      setIsLoading(false);
      if (error instanceof ApiError) {
        throw new Error(error.message);
      }
      throw new Error('Sign in failed. Please try again.');
    }
  }, [router]);

  const signUp = useCallback(async (email: string, password: string, name?: string) => {
    setIsLoading(true);
    try {
      const { user } = await api.signUp({ email, password, name });
      setUser(user);
      router.push('/');
    } catch (error) {
      setIsLoading(false);
      if (error instanceof ApiError) {
        throw new Error(error.message);
      }
      throw new Error('Sign up failed. Please try again.');
    }
  }, [router]);

  const signOut = useCallback(async () => {
    try {
      await api.signOut();
    } catch {
      // Ignore errors on sign out
    } finally {
      setUser(null);
      router.push('/signin');
    }
  }, [router]);

  return {
    user,
    isAuthenticated: !!user,
    isLoading,
    signIn,
    signUp,
    signOut,
    checkAuth,
  };
}

// Auth Provider component
export function AuthProvider({ children }: { children: ReactNode }) {
  const auth = useAuthState();

  return createElement(AuthContext.Provider, { value: auth }, children);
}

