import React, { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Send,
  Paperclip,
  Loader2,
  Sparkles,
  Bot,
  User,
  Zap,
} from 'lucide-react';
import { sendMessage, uploadComplaintFile } from '../features/complaintSlice.js';

export default function ChatCopilot() {
  const dispatch = useDispatch();
  const { messages, loading } = useSelector((state) => state.complaint);
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = (e) => {
    e?.preventDefault();
    if (!inputText.trim() || loading) return;
    dispatch(sendMessage(inputText.trim()));
    setInputText('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      dispatch(uploadComplaintFile(file));
      e.target.value = '';
    }
  };

  const quickPrompts = [
    {
      label: 'Amoxicillin Discoloration',
      prompt:
        'Logging complaint from Apollo Pharmacy: 500 bottles of Amoxicillin 250mg, batch BMX24602, mfg March 2026, exp February 2028. Capsules show severe dark discoloration in primary bottle packaging.',
    },
    {
      label: 'Metformin API Contamination',
      prompt:
        'Raw API complaint from Distributor: Metformin 500 mg API Grade, 50 kg in Fiber Drum. Foreign black particulate matter detected in drum liner.',
    },
    {
      label: 'Update Quantity to 750',
      prompt: 'Change affected quantity to 750 bottles.',
    },
  ];

  const handleQuickPrompt = (prompt) => {
    if (loading) return;
    dispatch(sendMessage(prompt));
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200/90 shadow-sm flex flex-col h-full overflow-hidden">
      {/* Top Header */}
      <div className="px-5 py-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-purple-600 flex items-center justify-center text-white shadow-sm shadow-purple-200">
            <Bot className="w-4.5 h-4.5" />
          </div>
          <div>
            <h3 className="font-bold text-sm text-slate-800 flex items-center gap-1.5">
              AIVOA Copilot
              <span className="inline-block w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            </h3>
            <p className="text-xs text-slate-500 font-medium">
              Drop complaint files or paste text below.
            </p>
          </div>
        </div>
        <div className="text-[11px] font-semibold text-purple-700 bg-purple-50 px-2.5 py-1 rounded-full border border-purple-200">
          Agent Online
        </div>
      </div>

      {/* Messages Feed */}
      <div className="flex-1 p-5 overflow-y-auto space-y-4 bg-slate-50/20">
        {messages.map((msg, index) => {
          const isUser = msg.sender === 'user';
          return (
            <div
              key={index}
              className={`flex items-start gap-2.5 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
            >
              {/* Avatar */}
              <div
                className={`w-7 h-7 rounded-full flex items-center justify-center text-xs shrink-0 ${
                  isUser
                    ? 'bg-purple-700 text-white'
                    : 'bg-purple-100 text-purple-700 border border-purple-200'
                }`}
              >
                {isUser ? <User className="w-3.5 h-3.5" /> : <Sparkles className="w-3.5 h-3.5" />}
              </div>

              {/* Message Content */}
              <div className={`max-w-[82%] space-y-1 ${isUser ? 'items-end' : 'items-start'}`}>
                <div
                  className={`p-3.5 rounded-2xl text-xs leading-relaxed ${
                    isUser
                      ? 'bg-purple-600 text-white rounded-tr-xs shadow-sm'
                      : 'bg-slate-100 text-slate-800 border border-slate-200/90 rounded-tl-xs shadow-xs'
                  }`}
                >
                  <p className="whitespace-pre-line">{msg.text}</p>
                </div>
                <div
                  className={`text-[10px] font-medium text-slate-400 px-1 ${
                    isUser ? 'text-right' : 'text-left'
                  }`}
                >
                  {isUser ? 'You' : 'AIVOA Copilot'}
                </div>
              </div>
            </div>
          );
        })}

        {/* Loading Bubble */}
        {loading && (
          <div className="flex items-start gap-2.5">
            <div className="w-7 h-7 rounded-full bg-purple-100 text-purple-700 border border-purple-200 flex items-center justify-center shrink-0">
              <Sparkles className="w-3.5 h-3.5" />
            </div>
            <div className="bg-slate-100 border border-slate-200 p-3.5 rounded-2xl rounded-tl-xs shadow-xs flex items-center gap-2 text-xs text-slate-600">
              <Loader2 className="w-4 h-4 animate-spin text-purple-600" />
              <span>Analyzing complaint & extracting details...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Quick Action Prompts */}
      <div className="px-5 py-2 bg-slate-50 border-t border-slate-200">
        <div className="flex items-center gap-1 mb-1 text-[10px] font-bold text-slate-500 uppercase tracking-wider">
          <Zap className="w-3 h-3 text-amber-500" />
          <span>Sample Complaints</span>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {quickPrompts.map((item, idx) => (
            <button
              key={idx}
              onClick={() => handleQuickPrompt(item.prompt)}
              disabled={loading}
              className="text-xs bg-white hover:bg-purple-50 hover:text-purple-700 hover:border-purple-300 text-slate-700 border border-slate-200 rounded-full px-3 py-1 transition-all duration-150 shadow-2xs disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      {/* Bottom Input Bar */}
      <div className="p-4 bg-white border-t border-slate-200">
        <form onSubmit={handleSend} className="flex items-center gap-2">
          {/* Hidden File Input */}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept=".pdf,.txt,.eml"
            className="hidden"
          />

          {/* Paperclip Button */}
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={loading}
            title="Upload complaint PDF or text document"
            className="p-2.5 rounded-lg border border-slate-200 hover:bg-slate-100 active:bg-slate-200 text-slate-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Paperclip className="w-4 h-4 text-slate-600" />
          </button>

          {/* Text Input */}
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a message or paste a complaint..."
            disabled={loading}
            className="flex-1 bg-slate-50 border border-slate-200 focus:border-purple-500 focus:bg-white rounded-lg px-3.5 py-2.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none transition-all"
          />

          {/* Send Button */}
          <button
            type="submit"
            disabled={!inputText.trim() || loading}
            className="inline-flex items-center gap-1.5 px-4 py-2.5 bg-purple-600 hover:bg-purple-700 active:bg-purple-800 text-white text-xs font-semibold rounded-lg shadow-sm shadow-purple-200 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
            <span>Send</span>
          </button>
        </form>

        {/* Footer Subtext */}
        <div className="mt-2 text-center text-[10px] font-bold text-slate-400 tracking-wider uppercase">
          POWERED BY LANGGRAPH
        </div>
      </div>
    </div>
  );
}

