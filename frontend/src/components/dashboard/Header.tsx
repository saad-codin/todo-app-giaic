'use client';

interface HeaderProps {
  onMenuToggle: () => void;
  title?: string;
}

export function Header({ onMenuToggle, title = 'Todo App' }: HeaderProps) {
  return (
    <header className="lg:hidden flex items-center justify-between h-16 px-4 bg-white border-b border-gray-200">
      <button
        onClick={onMenuToggle}
        className="p-2 rounded-lg hover:bg-gray-100 transition-colors min-w-[44px] min-h-[44px] flex items-center justify-center"
        aria-label="Toggle menu"
      >
        <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      <h1 className="text-lg font-bold text-gray-900">{title}</h1>

      {/* Spacer for centering */}
      <div className="w-10" />
    </header>
  );
}
