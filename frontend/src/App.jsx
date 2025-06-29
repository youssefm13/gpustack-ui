import React from 'react';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Header from './components/Header';
import Home from './pages/index';

function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-gray-50">
        <ProtectedRoute>
          <Header />
          <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <Home />
          </main>
        </ProtectedRoute>
      </div>
    </AuthProvider>
  );
}

export default App;
