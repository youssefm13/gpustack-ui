export default function ToolPanel({ onFileUpload, onSearch, isUploading = false, isSearching = false }) {
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      onFileUpload?.(file);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
      <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
        Tools & Actions
      </h2>
      
      <div className="space-y-4">
        {/* File Upload */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Upload File
          </label>
          <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-4 text-center">
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
              className={`cursor-pointer inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md ${
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
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Web Search
          </label>
          <button
            onClick={onSearch}
            disabled={isSearching}
            className={`w-full px-4 py-2 rounded-lg font-medium transition-colors ${
              isSearching
                ? 'bg-gray-400 text-gray-200 cursor-not-allowed'
                : 'bg-green-600 text-white hover:bg-green-700'
            }`}
          >
            {isSearching ? '🔍 Searching...' : '🌐 Search Web (Ctrl+Shift+S)'}
          </button>
        </div>

        {/* Quick Actions */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Quick Actions
          </label>
          <div className="grid grid-cols-2 gap-2">
            <button className="px-3 py-2 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors">
              📋 Copy Response
            </button>
            <button className="px-3 py-2 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors">
              💾 Save Chat
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

