export default function ChatBox({ prompt, response }) {
  return (
    <div className="chat-box">
      <div><strong>Prompt:</strong> {prompt}</div>
      <div><strong>Response:</strong> {response}</div>
    </div>
  );
}

