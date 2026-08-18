export default function ConversationThread({ messages }: { messages: {role: string, content: string}[] }) {
  if (messages.length === 0) {
    return <div className="text-center text-slate-400 mt-10">No messages yet. Send a message to start.</div>;
  }

  return (
    <div className="space-y-4">
      {messages.map((msg, i) => (
        <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
          <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${
            msg.role === 'user' 
              ? 'bg-indigo-600 text-white rounded-tr-sm' 
              : 'bg-white border border-slate-200 text-slate-800 rounded-tl-sm shadow-sm'
          }`}>
            <div className="text-sm whitespace-pre-wrap">{msg.content}</div>
          </div>
        </div>
      ))}
    </div>
  );
}
