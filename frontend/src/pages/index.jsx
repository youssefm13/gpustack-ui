import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import ErrorMessage from "../components/ErrorMessage";
import SuccessMessage from "../components/SuccessMessage";

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [response, setResponse] = useState("");
  const [fileText, setFileText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [conversations, setConversations] = useState([]);
  const [currentConversation, setCurrentConversation] = useState(null);

  // Auto-save conversation every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      if (prompt || response) {
        saveConversation();
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [prompt, response]);

  // Load saved conversations on mount
  useEffect(() => {
    loadSavedConversations();
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Ctrl+Enter to send message
      if (e.ctrlKey && e.key === 'Enter') {
        e.preventDefault();
        handleSubmit();
      }
      // Ctrl+S to save conversation
      if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        saveConversation();
      }
      // Ctrl+Shift+S to search web
      if (e.ctrlKey && e.shiftKey && e.key === 'S') {
        e.preventDefault();
        handleSearch();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [prompt]);

  const saveConversation = useCallback(() => {
    if (!prompt && !response) return;
    
    const conversation = {
      id: currentConversation?.id || Date.now(),
      prompt,
      response,
      fileText,
      timestamp: new Date().toISOString(),
    };

    const saved = JSON.parse(localStorage.getItem('gpustack-conversations') || '[]');
    const existingIndex = saved.findIndex(c => c.id === conversation.id);
    
    if (existingIndex >= 0) {
      saved[existingIndex] = conversation;
    } else {
      saved.push(conversation);
    }

    localStorage.setItem('gpustack-conversations', JSON.stringify(saved));
    setCurrentConversation(conversation);
    setConversations(saved);
    showSuccessMessage('Conversation saved successfully!');
  }, [prompt, response, fileText, currentConversation]);

  const loadSavedConversations = () => {
    const saved = JSON.parse(localStorage.getItem('gpustack-conversations') || '[]');
    setConversations(saved);
  };

  const loadConversation = (conversation) => {
    setCurrentConversation(conversation);
    setPrompt(conversation.prompt || '');
    setResponse(conversation.response || '');
    setFileText(conversation.fileText || '');
    setError('');
    showSuccessMessage('Conversation loaded!');
  };

  const clearConversation = () => {
    setPrompt('');
    setResponse('');
    setFileText('');
    setCurrentConversation(null);
    setError('');
    showSuccessMessage('Conversation cleared!');
  };

  const showSuccessMessage = (message) => {
    setSuccessMessage(message);
    setTimeout(() => setSuccessMessage(''), 3000);
  };

  const handleFileUpload = async (file) => {
    if (!file) return;

    setIsUploading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await axios.post("/api/files/upload", formData);
      setFileText(res.data.content);
      
      showSuccessMessage('File uploaded and processed successfully!');
    } catch (err) {
      setError(`File upload failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  const handleSearch = async () => {
    if (!prompt.trim()) {
      setError('Please enter a search query');
      return;
    }

    setIsSearching(true);
    setError('');

    try {
      const res = await axios.post("/api/tools/search", { q: prompt });
      setPrompt(res.data.result);
      showSuccessMessage('Web search completed!');
    } catch (err) {
      setError(`Search failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setIsSearching(false);
    }
  };

  const handleSubmit = async () => {
    if (!prompt.trim()) {
      setError('Please enter a message');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const res = await axios.post("/api/inference/infer", {
        messages: [{ role: "user", content: prompt }],
        max_tokens: 2000,
        temperature: 0.7,
        repetition_penalty: 1.1,
        frequency_penalty: 0.3,
        presence_penalty: 0.1,
        top_p: 0.9
      });
      
      setResponse(res.data.choices[0].message.content);
      saveConversation();
      showSuccessMessage('Response received!');
    } catch (err) {
      setError(`Request failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      showSuccessMessage('Copied to clipboard!');
    } catch (err) {
      setError('Failed to copy to clipboard');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto p-4 max-w-6xl">
        {/* Header */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 mb-6">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              GPUStack UI
            </h1>
            <div className="flex gap-2">
              <button
                onClick={saveConversation}
                disabled={!prompt && !response}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                title="Save conversation (Ctrl+S)"
              >
                💾 Save
              </button>
              <button
                onClick={clearConversation}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
              >
                🗑️ Clear
              </button>
            </div>
          </div>
          
          {/* Keyboard shortcuts help */}
          <div className="mt-4 text-sm text-gray-600 dark:text-gray-400">
            <span className="mr-4">⌘+Enter: Send</span>
            <span className="mr-4">⌘+S: Save</span>
            <span>⌘+Shift+S: Search Web</span>
          </div>
        </div>

        {/* Messages */}
        <div className="mb-6 space-y-4">
          <ErrorMessage 
            error={error} 
            onDismiss={() => setError('')} 
          />
          <SuccessMessage 
            message={successMessage} 
            onDismiss={() => setSuccessMessage('')} 
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Conversations Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4">
              <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
                Saved Conversations
              </h2>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {conversations.length === 0 ? (
                  <p className="text-gray-500 dark:text-gray-400 text-sm">
                    No saved conversations
                  </p>
                ) : (
                  conversations.map((conv) => (
                    <button
                      key={conv.id}
                      onClick={() => loadConversation(conv)}
                      className={`w-full text-left p-3 rounded-lg border transition-colors ${
                        currentConversation?.id === conv.id
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                          : 'border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700'
                      }`}
                    >
                      <div className="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {conv.prompt || 'Empty conversation'}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        {new Date(conv.timestamp).toLocaleDateString()}
                      </div>
                    </button>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Main Chat Area */}
          <div className="lg:col-span-3 space-y-6">
            {/* File Upload */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
              <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
                File Upload
              </h2>
              <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center">
                <input
                  type="file"
                  onChange={(e) => handleFileUpload(e.target.files[0])}
                  disabled={isUploading}
                  className="hidden"
                  id="file-upload"
                  accept=".pdf,.docx,.txt,.jpg,.jpeg,.png"
                />
                <label
                  htmlFor="file-upload"
                  className={`cursor-pointer inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md ${
                    isUploading
                      ? 'bg-gray-400 text-gray-200 cursor-not-allowed'
                      : 'bg-blue-600 text-white hover:bg-blue-700'
                  }`}
                >
                  {isUploading ? '📤 Uploading...' : '📁 Choose File'}
                </label>
                <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                  Supports PDF, DOCX, TXT, and images
                </p>
              </div>
              {fileText && (
                <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="flex justify-between items-center mb-2">
                    <h3 className="font-medium text-gray-900 dark:text-white">
                      File Content Preview:
                    </h3>
                    <button
                      onClick={() => copyToClipboard(fileText)}
                      className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400"
                    >
                      📋 Copy
                    </button>
                  </div>
                  <div className="text-sm text-gray-700 dark:text-gray-300 max-h-32 overflow-y-auto">
                    {fileText.substring(0, 500)}
                    {fileText.length > 500 && '...'}
                  </div>
                </div>
              )}
            </div>

            {/* Chat Interface */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
              <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
                Chat Interface
              </h2>

              {/* Input Area */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Your Message
                  </label>
                  <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Type your message here... (Ctrl+Enter to send)"
                    className="w-full h-32 p-4 border border-gray-300 dark:border-gray-600 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    disabled={isLoading}
                  />
                  <div className="flex justify-between items-center mt-2 text-xs text-gray-500 dark:text-gray-400">
                    <span>Ctrl+Enter to send</span>
                    <span>{prompt.length} characters</span>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3">
                  <button
                    onClick={handleSubmit}
                    disabled={isLoading || !prompt.trim()}
                    className={`flex-1 px-4 py-2 rounded-lg font-medium transition-colors ${
                      isLoading || !prompt.trim()
                        ? 'bg-gray-400 text-gray-200 cursor-not-allowed'
                        : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
                  >
                    {isLoading ? '⏳ Processing...' : '💬 Send Message'}
                  </button>
                  <button
                    onClick={handleSearch}
                    disabled={isSearching || !prompt.trim()}
                    className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                      isSearching || !prompt.trim()
                        ? 'bg-gray-400 text-gray-200 cursor-not-allowed'
                        : 'bg-green-600 text-white hover:bg-green-700'
                    }`}
                  >
                    {isSearching ? '🔍 Searching...' : '🌐 Search Web'}
                  </button>
                </div>
              </div>

              {/* Response Area */}
              {response && (
                <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="flex justify-between items-center mb-2">
                    <h3 className="font-medium text-gray-900 dark:text-white">
                      AI Response:
                    </h3>
                    <button
                      onClick={() => copyToClipboard(response)}
                      className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400"
                    >
                      📋 Copy
                    </button>
                  </div>
                  <div className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                    {response}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

