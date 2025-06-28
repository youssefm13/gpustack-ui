import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import ErrorMessage from "../components/ErrorMessage";
import SuccessMessage from "../components/SuccessMessage";
import ChatBox from "../components/ChatBox";
import ToolPanel from "../components/ToolPanel";

// Get backend URL from config
const getBackendUrl = () => {
  return window.CONFIG?.BACKEND_URL || 'http://localhost:8001';
};

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
  const [selectedModel, setSelectedModel] = useState("qwen3");

  // Available models
  const availableModels = [
    { id: "qwen3", name: "Qwen 3", description: "Fast and efficient model" },
    { id: "qwen2.5", name: "Qwen 2.5", description: "Balanced performance" },
    { id: "llama3.1", name: "Llama 3.1", description: "High quality responses" },
    { id: "gemma2", name: "Gemma 2", description: "Google's latest model" },
    { id: "mistral", name: "Mistral", description: "Fast and accurate" }
  ];

  const showSuccessMessage = useCallback((message) => {
    setSuccessMessage(message);
    setTimeout(() => setSuccessMessage(''), 3000);
  }, []);

  const saveConversation = useCallback(() => {
    if (!prompt && !response) return;
    
    const conversation = {
      id: currentConversation?.id || Date.now(),
      prompt,
      response,
      fileText,
      model: selectedModel,
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
  }, [prompt, response, fileText, currentConversation, selectedModel, showSuccessMessage]);

  // Auto-save conversation every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      if (prompt || response) {
        saveConversation();
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [prompt, response, saveConversation]);

  // Load saved conversations on mount
  useEffect(() => {
    loadSavedConversations();
    
    // Test backend connectivity
    const testBackend = async () => {
      try {
        const res = await axios.get(`${getBackendUrl()}/api/health`);
        console.log('Backend is reachable:', res.data);
      } catch (err) {
        console.error('Backend connectivity test failed:', err);
        setError('Cannot connect to backend server. Please check if the backend is running.');
      }
    };
    
    testBackend();
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
  }, [handleSubmit, saveConversation, handleSearch]);

  const loadSavedConversations = () => {
    const saved = JSON.parse(localStorage.getItem('gpustack-conversations') || '[]');
    setConversations(saved);
  };

  const loadConversation = (conversation) => {
    setCurrentConversation(conversation);
    setPrompt(conversation.prompt || '');
    setResponse(conversation.response || '');
    setFileText(conversation.fileText || '');
    setSelectedModel(conversation.model || 'qwen3');
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

  const handleFileUpload = async (file) => {
    if (!file) return;

    setIsUploading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await axios.post(`${getBackendUrl()}/api/files/upload`, formData);
      setFileText(res.data.content);
      
      showSuccessMessage('File uploaded and processed successfully!');
    } catch (err) {
      setError(`File upload failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  const handleSearch = useCallback(async () => {
    if (!(prompt?.trim() || '')) {
      setError('Please enter a search query');
      return;
    }

    setIsSearching(true);
    setError('');

    try {
      const res = await axios.post(`${getBackendUrl()}/api/tools/search`, { q: prompt });
      setPrompt(res.data.result);
      showSuccessMessage('Web search completed!');
    } catch (err) {
      setError(`Search failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setIsSearching(false);
    }
  }, [prompt, showSuccessMessage]);

  const handleSubmit = useCallback(async () => {
    if (!(prompt?.trim() || '')) {
      setError('Please enter a message');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      console.log('Sending request to:', `${getBackendUrl()}/api/inference/infer`);
      const res = await axios.post(`${getBackendUrl()}/api/inference/infer`, {
        model: selectedModel,
        messages: [{ role: "user", content: prompt }],
        max_tokens: 2000,
        temperature: 0.7,
        repetition_penalty: 1.1,
        frequency_penalty: 0.3,
        presence_penalty: 0.1,
        top_p: 0.9
      });
      
      console.log('Response received:', res.data);
      setResponse(res.data.choices[0].message.content);
      saveConversation();
      showSuccessMessage('Response received!');
    } catch (err) {
      console.error('API Error:', err);
      setError(`Request failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setIsLoading(false);
    }
  }, [prompt, selectedModel, saveConversation, showSuccessMessage]);

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      showSuccessMessage('Copied to clipboard!');
    } catch (err) {
      setError('Failed to copy to clipboard');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-100 dark:from-gray-900 dark:to-gray-800">
      <div className="flex flex-col min-h-screen">
        {/* Header */}
        <header className="bg-white dark:bg-gray-900 shadow-md py-4 px-8 flex items-center justify-between">
          <h1 className="text-3xl font-extrabold text-blue-700 dark:text-blue-300 tracking-tight">GPUStack UI</h1>
          <div className="flex gap-2">
            <button
              onClick={saveConversation}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
              title="Save conversation (Ctrl+S)"
              disabled={!prompt && !response}
            >
              💾 Save
            </button>
            <button
              onClick={clearConversation}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
            >
              🗑️ Clear
            </button>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 container mx-auto px-4 py-8 max-w-7xl">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            {/* Sidebar: Saved Conversations */}
            <aside className="lg:col-span-1">
              <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 mb-6 sticky top-8">
                <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Saved Conversations</h2>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {conversations.length === 0 ? (
                    <p className="text-gray-500 dark:text-gray-400 text-sm">No saved conversations</p>
                  ) : (
                    conversations.map((c) => (
                      <button
                        key={c.id}
                        onClick={() => loadConversation(c)}
                        className={`w-full text-left px-3 py-2 rounded-lg transition-colors font-medium ${
                          currentConversation?.id === c.id
                            ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-200'
                            : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-blue-50 dark:hover:bg-blue-800'
                        }`}
                      >
                        <span className="block truncate">{c.prompt?.slice(0, 40) || 'Untitled'}</span>
                        <span className="block text-xs text-gray-400 dark:text-gray-500">
                          {c.model ? `${c.model} • ` : ''}{new Date(c.timestamp).toLocaleString()}
                        </span>
                      </button>
                    ))
                  )}
                </div>
              </div>
            </aside>

            {/* Main Chat & Tools */}
            <section className="lg:col-span-3 space-y-8">
              {/* File Upload & Tools */}
              <ToolPanel
                onFileUpload={handleFileUpload}
                onSearch={handleSearch}
                isUploading={isUploading}
                isSearching={isSearching}
              />

              {/* Chat Interface */}
              <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-gray-900 dark:text-white">Chat Interface</h2>
                  <div className="flex items-center gap-3">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Model:</label>
                    <select
                      value={selectedModel}
                      onChange={(e) => setSelectedModel(e.target.value)}
                      className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm"
                      disabled={isLoading}
                    >
                      {availableModels.map((model) => (
                        <option key={model.id} value={model.id}>
                          {model.name} - {model.description}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                <div className="space-y-6">
                  <ChatBox
                    prompt={prompt}
                    response={response}
                    timestamp={currentConversation?.timestamp}
                    isLoading={isLoading}
                    model={selectedModel}
                  />
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Your Message</label>
                    <textarea
                      placeholder="Type your message here... (Ctrl+Enter to send)"
                      className="w-full h-32 p-4 border border-gray-300 dark:border-gray-600 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm"
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                      disabled={isLoading}
                    />
                    <div className="flex justify-between items-center mt-2 text-xs text-gray-500 dark:text-gray-400">
                      <span>Ctrl+Enter to send</span>
                      <span>{prompt.length} characters</span>
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <button
                      onClick={handleSubmit}
                      disabled={isLoading || !(prompt?.trim() || '')}
                      className="flex-1 px-4 py-2 rounded-lg font-medium transition-colors bg-blue-600 text-white hover:bg-blue-700 disabled:bg-gray-400 disabled:text-gray-200 disabled:cursor-not-allowed"
                    >
                      💬 Send Message
                    </button>
                    <button
                      onClick={handleSearch}
                      disabled={isSearching || !(prompt?.trim() || '')}
                      className="px-6 py-2 rounded-lg font-medium transition-colors bg-green-600 text-white hover:bg-green-700 disabled:bg-gray-400 disabled:text-gray-200 disabled:cursor-not-allowed"
                    >
                      🌐 Search Web
                    </button>
                  </div>
                </div>
              </div>
            </section>
          </div>
        </main>

        {/* Footer */}
        <footer className="bg-white dark:bg-gray-900 shadow-inner py-4 px-8 text-center text-gray-400 text-xs mt-8">
          GPUStack UI &copy; {new Date().getFullYear()} | Powered by FastAPI, Next.js, and Tailwind CSS
        </footer>

        {/* Error & Success Messages */}
        <div className="fixed bottom-6 right-6 z-50 space-y-2 w-96 max-w-full">
          {error && <ErrorMessage message={error} />}
          {successMessage && <SuccessMessage message={successMessage} />}
        </div>
      </div>
    </div>
  );
}

