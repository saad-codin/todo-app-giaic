'use client';

import { motion } from 'framer-motion';
import { StickyNote } from 'lucide-react';

export default function StickyWallPage() {
  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Sticky Wall</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
          Your personal pinboard for quick notes and ideas
        </p>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        className="flex flex-col items-center justify-center py-24 text-center"
      >
        <div className="w-16 h-16 rounded-2xl bg-amber-50 dark:bg-amber-900/20 flex items-center justify-center mb-5">
          <StickyNote className="w-8 h-8 text-amber-500" />
        </div>
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          Coming Soon
        </h2>
        <p className="text-sm text-gray-500 dark:text-gray-400 max-w-xs leading-relaxed">
          Sticky Wall is under construction. Pin quick notes, ideas, and reminders here — right alongside your tasks.
        </p>
      </motion.div>
    </div>
  );
}
