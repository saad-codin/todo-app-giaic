'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { CheckCircle2, Bot, Calendar, Moon, Zap, Repeat } from 'lucide-react';
import { useAuthContext } from '@/lib/auth';

const features = [
  {
    icon: CheckCircle2,
    title: 'Task Management',
    description: 'Create, organize, and prioritize tasks with ease. Color-coded priorities keep you focused.',
    color: 'text-sage-500',
    bg: 'bg-sage-50 dark:bg-sage-900/20',
  },
  {
    icon: Bot,
    title: 'AI Assistant',
    description: 'Chat naturally with your AI assistant to add, search, and manage tasks hands-free.',
    color: 'text-blue-500',
    bg: 'bg-blue-50 dark:bg-blue-900/20',
  },
  {
    icon: Calendar,
    title: 'Calendar View',
    description: 'Visualize your entire schedule in a beautiful calendar with task overlays.',
    color: 'text-purple-500',
    bg: 'bg-purple-50 dark:bg-purple-900/20',
  },
  {
    icon: Moon,
    title: 'Dark Mode',
    description: 'Switch between light and dark themes instantly. Your preference is remembered.',
    color: 'text-slate-500',
    bg: 'bg-slate-50 dark:bg-slate-800/40',
  },
  {
    icon: Zap,
    title: 'Real-time Sync',
    description: 'Tasks sync live across all devices. Get instant reminders delivered in-app.',
    color: 'text-amber-500',
    bg: 'bg-amber-50 dark:bg-amber-900/20',
  },
  {
    icon: Repeat,
    title: 'Recurring Tasks',
    description: 'Set daily, weekly, or monthly recurrence — never miss a repeating obligation.',
    color: 'text-emerald-500',
    bg: 'bg-emerald-50 dark:bg-emerald-900/20',
  },
];

export default function LandingPage() {
  const { isAuthenticated, isLoading } = useAuthContext();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sage-500" />
      </div>
    );
  }

  if (isAuthenticated) return null;

  return (
    <div className="min-h-screen bg-white dark:bg-gray-950">
      {/* Nav */}
      <nav className="fixed top-0 inset-x-0 z-50 bg-white/80 dark:bg-gray-950/80 backdrop-blur-sm border-b border-gray-200/50 dark:border-gray-800/50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-sage-500 flex items-center justify-center">
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <span className="text-lg font-bold text-gray-900 dark:text-white">TaskFlow</span>
          </div>
          <div className="flex items-center gap-3">
            <Link
              href="/signin"
              className="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
            >
              Sign In
            </Link>
            <Link
              href="/signup"
              className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-sage-500 hover:bg-sage-600 rounded-lg transition-colors"
            >
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative pt-32 pb-24 px-4 sm:px-6 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-sage-50 via-white to-blue-50 dark:from-gray-900 dark:via-gray-950 dark:to-gray-900" />
        <div className="relative max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-sage-100 dark:bg-sage-900/40 text-sage-700 dark:text-sage-400 mb-6">
              AI-Powered Productivity
            </span>
            <h1 className="text-5xl sm:text-6xl font-bold text-gray-900 dark:text-white leading-tight tracking-tight mb-6">
              Organize your work,{' '}
              <span className="text-sage-500">amplify</span> your focus
            </h1>
            <p className="text-xl text-gray-500 dark:text-gray-400 mb-10 max-w-2xl mx-auto leading-relaxed">
              The modern task manager that thinks with you. Manage tasks, chat with your AI assistant, and stay on top of your schedule — all in one beautiful workspace.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.15 }}
            className="flex flex-col sm:flex-row gap-4 justify-center"
          >
            <motion.div whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.98 }}>
              <Link
                href="/signup"
                className="inline-flex items-center justify-center px-8 py-3.5 text-base font-semibold text-white bg-sage-500 hover:bg-sage-600 rounded-xl shadow-lg shadow-sage-500/25 transition-colors"
              >
                Get Started Free
              </Link>
            </motion.div>
            <motion.div whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.98 }}>
              <Link
                href="/signin"
                className="inline-flex items-center justify-center px-8 py-3.5 text-base font-semibold text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                Sign In
              </Link>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-24 px-4 sm:px-6 bg-gray-50 dark:bg-gray-900">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Everything you need to stay productive
            </h2>
            <p className="text-lg text-gray-500 dark:text-gray-400 max-w-xl mx-auto">
              Powerful features designed to help you get more done with less effort.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, i) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: i * 0.07 }}
                  className="p-6 bg-white dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 shadow-sm hover:shadow-md transition-shadow"
                >
                  <div className={`w-11 h-11 rounded-xl ${feature.bg} flex items-center justify-center mb-4`}>
                    <Icon className={`w-5 h-5 ${feature.color}`} />
                  </div>
                  <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
                    {feature.description}
                  </p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Banner */}
      <section className="py-20 px-4 sm:px-6 bg-sage-500 dark:bg-sage-600">
        <div className="max-w-3xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
              Start for free today
            </h2>
            <p className="text-sage-100 mb-8 text-lg">
              Join thousands of people who use TaskFlow to stay organized and productive.
            </p>
            <motion.div whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.98 }} className="inline-block">
              <Link
                href="/signup"
                className="inline-flex items-center justify-center px-8 py-3.5 text-base font-semibold text-sage-700 bg-white hover:bg-sage-50 rounded-xl shadow-lg transition-colors"
              >
                Create your free account
              </Link>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 sm:px-6 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-5 h-5 rounded-md bg-sage-500 flex items-center justify-center">
              <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">TaskFlow</span>
          </div>
          <p className="text-xs text-gray-400 dark:text-gray-500">
            © 2026 TaskFlow. Built with AI-powered productivity in mind.
          </p>
        </div>
      </footer>
    </div>
  );
}
