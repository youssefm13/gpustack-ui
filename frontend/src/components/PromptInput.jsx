export default function PromptInput({ prompt, setPrompt }) {
  return (
    <textarea
      value={prompt}
      onChange={(e) => setPrompt(e.target.value)}
      className="w-full h-40 border p-2"
    />
  );
}

