export default function ChatBox({ prompt, response, timestamp, isLoading = false, model = "qwen3" }) {
  return (
    <div className="space-y-6">
      {/* User Message */}
      {prompt && (
        <div className="flex items-end justify-end gap-2">
          <div className="hidden sm:block w-8 h-8 rounded-full bg-blue-200 flex items-center justify-center text-blue-700 font-bold">🧑</div>
          <div className="max-w-2xl bg-blue-600 text-white rounded-2xl p-4 shadow-md relative">
            <div className="text-xs font-semibold mb-1 opacity-80">You</div>
            <div className="whitespace-pre-wrap break-words text-base">{prompt}</div>
            {timestamp && (
              <div className="text-xs text-blue-200 mt-2 text-right">{new Date(timestamp).toLocaleTimeString()}</div>
            )}
            <div className="absolute right-0 top-0 w-3 h-3 bg-blue-400 rounded-tr-2xl rounded-bl-2xl"></div>
          </div>
        </div>
      )}

      {/* AI Response */}
      {response && (
        <div className="flex items-end justify-start gap-2">
          <div className="hidden sm:block w-8 h-8 rounded-full bg-gray-300 dark:bg-gray-700 flex items-center justify-center text-gray-700 dark:text-gray-200 font-bold">🤖</div>
          <div className="max-w-2xl bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-2xl p-4 shadow-md relative">
            <div className="text-xs font-semibold mb-1 text-gray-600 dark:text-gray-400 opacity-80">
              {model === "qwen3" ? "Qwen 3" : 
               model === "qwen2.5" ? "Qwen 2.5" : 
               model === "llama3.1" ? "Llama 3.1" : 
               model === "gemma2" ? "Gemma 2" : 
               model === "mistral" ? "Mistral" : 
               model.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </div>
            <div className="whitespace-pre-wrap break-words text-base">{response}</div>
            {timestamp && (
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-2 text-right">{new Date(timestamp).toLocaleTimeString()}</div>
            )}
            <div className="absolute left-0 top-0 w-3 h-3 bg-gray-300 dark:bg-gray-700 rounded-tl-2xl rounded-br-2xl"></div>
          </div>
        </div>
      )}

      {/* Loading Indicator */}
      {isLoading && (
        <div className="flex items-end justify-start gap-2">
          <div className="hidden sm:block w-8 h-8 rounded-full bg-gray-300 dark:bg-gray-700 flex items-center justify-center text-gray-700 dark:text-gray-200 font-bold">🤖</div>
          <div className="max-w-2xl bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-2xl p-4 shadow-md flex items-center gap-2">
            <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></span>
            <span className="text-gray-600 dark:text-gray-400">
              Thinking with {model === "qwen3" ? "Qwen 3" : 
                           model === "qwen2.5" ? "Qwen 2.5" : 
                           model === "llama3.1" ? "Llama 3.1" : 
                           model === "gemma2" ? "Gemma 2" : 
                           model === "mistral" ? "Mistral" : 
                           model.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}...
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

