import React from 'react';

function Error({ statusCode }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-lg p-8 max-w-md w-full text-center">
        <div className="text-6xl mb-4">
          {statusCode === 404 ? '🔍' : '⚠️'}
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          {statusCode === 404 ? 'Page Not Found' : 'Something went wrong'}
        </h1>
        <p className="text-gray-600 mb-6">
          {statusCode === 404 
            ? 'The page you are looking for does not exist.'
            : `An error ${statusCode} occurred on server.`
          }
        </p>
        <button
          onClick={() => window.location.href = '/'}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          Go Home
        </button>
      </div>
    </div>
  );
}

Error.getInitialProps = ({ res, err }) => {
  const statusCode = res ? res.statusCode : err ? err.statusCode : 404;
  return { statusCode };
};

export default Error; 