export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-sage-50 via-white to-blue-50 dark:from-gray-900 dark:via-gray-950 dark:to-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-md">
        {children}
      </div>
    </div>
  );
}
