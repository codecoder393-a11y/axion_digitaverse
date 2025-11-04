import React, { useState, useRef, useEffect } from 'react';
import { useUser } from '../UserContext';
import { FaPaperPlane } from 'react-icons/fa';

const Chat: React.FC = () => {
  const { user } = useUser();
  const [messages, setMessages] = useState<{ from: string; text: string; time: string }[]>([]);
  const [text, setText] = useState('');
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    // welcome message
    setMessages([{ from: 'System', text: 'Welcome to Axion Chat. Be kind and keep keys private.', time: new Date().toLocaleTimeString() }]);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!text.trim()) return;
    const msg = { from: user?.address ? shortAddress(user.address) : 'Guest', text: text.trim(), time: new Date().toLocaleTimeString() };
    setMessages(prev => [...prev, msg]);
    setText('');

    // For now, echo reply locally. Later we can wire to backend or AI.
    setTimeout(() => {
      setMessages(prev => [...prev, { from: 'AxionBot', text: `Echo: ${msg.text}`, time: new Date().toLocaleTimeString() }]);
    }, 600);
  };

  const onKeyDown: React.KeyboardEventHandler<HTMLInputElement> = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      sendMessage();
    }
  };

  function shortAddress(address: string) {
    if (!address) return '';
    return address.slice(0, 8) + '...' + address.slice(-4);
  }

  return (
    <div className="container py-4">
      <h3 className="text-white mb-3">Chat</h3>
      <div className="card p-3" style={{ maxWidth: 900 }}>
        <div style={{ maxHeight: 400, overflowY: 'auto' }} className="mb-3">
          {messages.map((m, i) => (
            <div key={i} className="mb-2">
              <div className="small text-muted">{m.from} • {m.time}</div>
              <div className="p-2" style={{ background: 'rgba(30,30,30,0.5)', borderRadius: 8 }}>{m.text}</div>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>
        <div className="d-flex gap-2">
          <input type="text" className="form-control" placeholder="Type a message..." value={text} onChange={e => setText(e.target.value)} onKeyDown={onKeyDown} />
          <button className="btn btn-primary" onClick={sendMessage}><FaPaperPlane /></button>
        </div>
      </div>
    </div>
  );
};

export default Chat;
