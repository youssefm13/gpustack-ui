export default function PromptInput({ prompt, setPrompt, isLoading = false, onSubmit }) {
  const handleKeyDown = (e) => {
    if (e.ctrlKey && e.key === 'Enter' && !isLoading && prompt.trim()) {
      e.preventDefault();
      onSubmit?.();
    }
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
        Your Message
      </label>
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type your message here... (Ctrl+Enter to send)"
        disabled={isLoading}
        className="w-full h-32 p-4 border border-gray-300 dark:border-gray-600 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white disabled:opacity-50 disabled:cursor-not-allowed"
      />
      <div className="flex justify-between items-center text-xs text-gray-500 dark:text-gray-400">
        <span>Ctrl+Enter to send</span>
        <span>{prompt.length} characters</span>
      </div>
    </div>
  );
}

