export default function ChatBox({ prompt, response, timestamp, isLoading = false }) {
  return (
    <div className="space-y-4">
      {/* User Message */}
      {prompt && (
        <div className="flex justify-end">
          <div className="max-w-3xl bg-blue-600 text-white rounded-lg p-4 shadow-sm">
            <div className="text-sm font-medium mb-1">You</div>
            <div className="whitespace-pre-wrap">{prompt}</div>
            {timestamp && (
              <div className="text-xs text-blue-200 mt-2">
                {new Date(timestamp).toLocaleTimeString()}
              </div>
            )}
          </div>
        </div>
      )}

      {/* AI Response */}
      {response && (
        <div className="flex justify-start">
          <div className="max-w-3xl bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg p-4 shadow-sm">
            <div className="text-sm font-medium mb-1 text-gray-600 dark:text-gray-400">
              🤖 AI Assistant
            </div>
            <div className="whitespace-pre-wrap">{response}</div>
            {timestamp && (
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                {new Date(timestamp).toLocaleTimeString()}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Loading Indicator */}
      {isLoading && (
        <div className="flex justify-start">
          <div className="max-w-3xl bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg p-4 shadow-sm">
            <div className="text-sm font-medium mb-1 text-gray-600 dark:text-gray-400">
              🤖 AI Assistant
            </div>
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
              <span className="text-gray-600 dark:text-gray-400">Thinking...</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

