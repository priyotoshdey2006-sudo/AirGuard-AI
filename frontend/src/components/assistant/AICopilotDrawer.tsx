import React, { useState, useRef, useEffect } from 'react';
import { ChatMessage, SensitivityLevel } from '../../types';
import { MessageSquare, Send, Sparkles, X, Bot, User, ShieldAlert } from 'lucide-react';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  messages: ChatMessage[];
  loading: boolean;
  onSendMessage: (text: string) => void;
  currentAQI: number;
  sensitivity: SensitivityLevel;
}

export const AICopilotDrawer: React.FC<Props> = ({
  isOpen,
  onClose,
  messages,
  loading,
  onSendMessage,
  currentAQI,
  sensitivity,
}) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !loading) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  const suggestions = [
    'Should I wear an N95 mask outside right now?',
    'What is the best hour for an outdoor jog today?',
    'When should I open my windows for ventilation?',
    'How does current AQI affect children and asthma?',
  ];

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-[460px] liquid-glass-overlay border-l border-white/15 shadow-glass-lg flex flex-col backdrop-blur-2xl">
      {/* Drawer Header */}
      <div className="p-4.5 border-b border-white/10 bg-midnight-900/60 backdrop-blur-xl flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-500 via-teal-400 to-cyan-400 flex items-center justify-center text-midnight-950 shadow-glow-emerald">
            <Sparkles className="w-4.5 h-4.5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <span>AirGuard Copilot</span>
              <span className="text-[10px] px-2 py-0.5 bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 rounded-full font-mono tracking-wider font-semibold">
                GROUNDED AI
              </span>
            </h3>
            <p className="text-[11px] text-slate-300/80 mt-0.5">
              Live AQI: <strong className="text-emerald-400 font-semibold">{currentAQI}</strong> • Profile:{' '}
              <strong className="text-cyan-300 font-semibold">{sensitivity}</strong>
            </p>
          </div>
        </div>

        <button
          onClick={onClose}
          className="p-1.5 rounded-xl text-slate-400 hover:text-white hover:bg-white/10 transition-all duration-200"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Messages Stream */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3.5">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex items-start gap-2.5 ${msg.sender === 'user' ? 'flex-row-reverse' : ''}`}
          >
            <div
              className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 text-xs font-bold ${
                msg.sender === 'user'
                  ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-midnight-950 shadow-glow-emerald'
                  : 'bg-white/10 text-cyan-400 border border-white/15'
              }`}
            >
              {msg.sender === 'user' ? <User className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5" />}
            </div>

            <div
              className={`max-w-[82%] p-3.5 text-xs leading-relaxed ${
                msg.sender === 'user'
                  ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-midnight-950 font-medium rounded-2xl rounded-tr-sm shadow-glow-emerald'
                  : 'liquid-glass-card text-slate-200 rounded-2xl rounded-tl-sm border border-white/10 shadow-glass-sm'
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.text}</p>
              <div
                className={`text-[9px] mt-1.5 text-right ${
                  msg.sender === 'user' ? 'text-midnight-950/70 font-medium' : 'text-slate-400'
                }`}
              >
                {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-2.5 text-xs text-slate-300 pl-10 py-1">
            <Sparkles className="w-3.5 h-3.5 text-emerald-400 animate-spin" />
            <span className="font-medium">Evaluating atmospheric physics & clinical guidelines...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Quick Prompt Suggestions */}
      <div className="px-4 py-3 border-t border-white/10 bg-midnight-900/50 backdrop-blur-lg">
        <div className="text-[10px] text-slate-400 uppercase font-bold tracking-wider mb-2">Suggested Inquiries</div>
        <div className="flex flex-wrap gap-1.5">
          {suggestions.map((s, idx) => (
            <button
              key={idx}
              onClick={() => onSendMessage(s)}
              disabled={loading}
              className="text-[11px] liquid-glass-control hover:border-emerald-500/40 text-slate-300 hover:text-white px-3 py-1.5 rounded-xl transition-all shadow-glass-sm disabled:opacity-50 text-left truncate max-w-full"
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="p-3.5 border-t border-white/10 bg-midnight-900/70 backdrop-blur-xl flex gap-2.5">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about masks, jogging hours, or room ventilation..."
          disabled={loading}
          className="flex-1 bg-white/5 border border-white/15 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-emerald-400/60 focus:ring-1 focus:ring-emerald-400/40 transition-all"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="px-4 py-2.5 bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 text-midnight-950 font-bold rounded-xl transition-all shadow-glow-emerald disabled:opacity-40"
        >
          <Send className="w-3.5 h-3.5" />
        </button>
      </form>
    </div>
  );
};
