import { useState } from "react";
import axios from "axios";

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [response, setResponse] = useState("");
  const [fileText, setFileText] = useState("");

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append("file", file);

    const res = await axios.post("/api/upload", formData);
    setFileText(res.data.content);
  };

  const handleSearch = async () => {
    const res = await axios.post("/api/search", { q: prompt });
    setPrompt(res.data.result);
  };

  const handleSubmit = async () => {
    const res = await axios.post("/api/infer", {
      messages: [{ role: "user", content: prompt }],
      max_tokens: 2000,
      temperature: 0.7,
      repetition_penalty: 1.1,
      frequency_penalty: 0.3,
      presence_penalty: 0.1,
      top_p: 0.9
    });
    setResponse(res.choices[0].message.content);
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">GPUStack UI</h1>
      <input type="file" onChange={handleFileUpload} />
      <button onClick={handleSearch}>Search Web</button>
      <textarea value={prompt} onChange={(e) => setPrompt(e.target.value)} />
      <button onClick={handleSubmit}>Send</button>
      <pre>{response}</pre>
    </div>
  );
}

