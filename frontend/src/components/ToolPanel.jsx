export default function ToolPanel({ onFileUpload, onSearch, isUploading = false, isSearching = false }) {
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      onFileUpload?.(file);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8 space-y-8">
      <h2 className="text-xl font-bold mb-2 text-gray-900 dark:text-white flex items-center gap-2">
        🛠️ Tools & Actions
      </h2>
      {/* File Upload */}
      <div className="space-y-2 border-b border-gray-200 dark:border-gray-700 pb-6">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 flex items-center gap-2">
          📁 Upload File
        </label>
        <div className="border-2 border-dashed border-blue-200 dark:border-blue-700 rounded-xl p-6 text-center bg-blue-50 dark:bg-blue-900/20">
          <input
            type="file"
            onChange={handleFileChange}
            disabled={isUploading}
            className="hidden"
            id="file-upload-tool"
            accept=".pdf,.docx,.txt,.jpg,.jpeg,.png"
          />
          <label
            htmlFor="file-upload-tool"
            className={`cursor-pointer inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm transition-colors ${
              isUploading
                ? 'bg-gray-400 text-gray-200 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {isUploading ? '📤 Uploading...' : '📁 Choose File'}
          </label>
          <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
            Supports PDF, DOCX, TXT, and images
          </p>
        </div>
      </div>
      {/* Web Search */}
      <div className="space-y-2 border-b border-gray-200 dark:border-gray-700 pb-6">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 flex items-center gap-2">
          🌐 Web Search
        </label>
        <button
          onClick={onSearch}
          disabled={isSearching}
          className={`w-full px-4 py-2 rounded-lg font-medium transition-colors shadow-sm flex items-center justify-center gap-2 ${
            isSearching
              ? 'bg-gray-400 text-gray-200 cursor-not-allowed'
              : 'bg-green-600 text-white hover:bg-green-700'
          }`}
        >
          {isSearching ? '🔍 Searching...' : '🌐 Search Web (Ctrl+Shift+S)'}
        </button>
      </div>
      {/* Quick Actions */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 flex items-center gap-2">
          ⚡ Quick Actions
        </label>
        <div className="grid grid-cols-2 gap-2">
          <button className="px-3 py-2 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors flex items-center gap-2 shadow-sm">
            📋 Copy Response
          </button>
          <button className="px-3 py-2 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors flex items-center gap-2 shadow-sm">
            💾 Save Chat
          </button>
        </div>
      </div>
    </div>
  );
}

