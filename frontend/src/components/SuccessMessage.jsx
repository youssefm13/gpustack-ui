export default function SuccessMessage({ message, onDismiss, className = "" }) {
  if (!message) return null;

  return (
    <div className={`p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg ${className}`}>
      <div className="flex">
        <div className="flex-shrink-0">
          <span className="text-green-400">✅</span>
        </div>
        <div className="ml-3 flex-1">
          <p className="text-sm text-green-800 dark:text-green-200">{message}</p>
        </div>
        {onDismiss && (
          <div className="ml-auto pl-3">
            <button
              onClick={onDismiss}
              className="inline-flex text-green-400 hover:text-green-600 dark:hover:text-green-300"
            >
              <span className="sr-only">Dismiss</span>
              <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        )}
      </div>
    </div>
  );
} 