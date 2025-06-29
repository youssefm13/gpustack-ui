import { useState } from "react";
import axios from "axios";
import { useAuth } from '../contexts/AuthContext';

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [response, setResponse] = useState("");
  const [fileText, setFileText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const { token } = useAuth();

  // Configure axios with auth header
  const apiCall = async (method, url, data = null) => {
    try {
      const config = {
        method,
        url,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      };
      
      if (data) {
        config.data = data;
      }
      
      return await axios(config);
    } catch (err) {
      console.error('API call failed:', err);
      throw err;
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    setLoading(true);
    setError("");
    
    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await axios.post("/api/files/upload", formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setFileText(res.data.content);
      setPrompt(prev => prev + "\n\nFile content:\n" + res.data.content);
    } catch (err) {
      setError("File upload failed: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!prompt.trim()) {
      setError("Please enter a search query");
      return;
    }
    
    setLoading(true);
    setError("");
    
    try {
      const res = await apiCall('POST', '/api/tools/search', { q: prompt });
      const searchResult = res.data.result;
      
      // Update prompt with search results
      if (searchResult.llm_summary) {
        setPrompt(prev => prev + "\n\nSearch Results:\n" + searchResult.llm_summary);
      }
    } catch (err) {
      setError("Search failed: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!prompt.trim()) {
      setError("Please enter a message");
      return;
    }
    
    setLoading(true);
    setError("");
    
    try {
      const res = await apiCall('POST', '/api/inference', {
        model: "qwen3", // Default model
        messages: [{ role: "user", content: prompt }],
        max_tokens: 2000,
        temperature: 0.7,
        repetition_penalty: 1.1,
        frequency_penalty: 0.3,
        presence_penalty: 0.1,
        top_p: 0.9
      });
      
      setResponse(res.data.choices[0].message.content);
    } catch (err) {
      setError("Inference failed: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-6">AI Chat Interface</h2>
        
        {/* File Upload Section */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Upload File (optional)
          </label>
          <input 
            type="file" 
            onChange={handleFileUpload}
            disabled={loading}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
          />
        </div>

        {/* Search Section */}
        <div className="mb-6">
          <button 
            onClick={handleSearch}
            disabled={loading || !prompt.trim()}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Searching...' : 'Search Web'}
          </button>
        </div>

        {/* Prompt Input */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Your Message
          </label>
          <textarea 
            value={prompt} 
            onChange={(e) => setPrompt(e.target.value)}
            disabled={loading}
            rows={6}
            className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
            placeholder="Enter your message here..."
          />
        </div>

        {/* Submit Button */}
        <div className="mb-6">
          <button 
            onClick={handleSubmit}
            disabled={loading || !prompt.trim()}
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Processing...' : 'Send Message'}
          </button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative">
            <span className="block sm:inline">{error}</span>
          </div>
        )}

        {/* Response Display */}
        {response && (
          <div className="bg-gray-50 border border-gray-200 rounded-md p-4">
            <h3 className="text-lg font-medium text-gray-900 mb-2">AI Response:</h3>
            <div className="prose max-w-none">
              <pre className="whitespace-pre-wrap text-sm text-gray-700">{response}</pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

