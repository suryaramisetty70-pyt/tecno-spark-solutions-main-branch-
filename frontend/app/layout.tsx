import type { Metadata, Viewport } from 'next';
import { AuthProvider } from '@/lib/auth-context';
import ErrorBoundary from './error-boundary';
import './globals.css';

export const metadata: Metadata = {
  title: 'Buddy AI - Operating System',
  description: 'Intelligent AI agent orchestration platform by Tecno Spark Solutions',
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50">
        <ErrorBoundary>
          <AuthProvider>{children}</AuthProvider>
        </ErrorBoundary>
      </body>
    </html>
  );
}
