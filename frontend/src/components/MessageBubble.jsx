import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark, oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Code, Bot, User } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';

const MessageBubble = ({ 
  message, sender = 'user', subject, question, 
  onRegenerate, isLast, confidence, confidence_level, 
  matched_question, time_taken, theme 
}) => {
  const [feedback, setFeedback] = useState(null);
  const [speaking, setSpeaking] = useState(false);
  const { user } = useAuth();
  const safeSender = sender || 'user';

  const handleCopy = () => {
    navigator.clipboard.writeText(message).then(() => {
      toast.success('Copied to clipboard!');
    });
  };

  const handleVoice = () => {
    if (speaking) {
      window.speechSynthesis.cancel();
      setSpeaking(false);
      return;
    }
    const utterance = new SpeechSynthesisUtterance(message);
    utterance.rate = 0.95;
    utterance.onend = () => setSpeaking(false);
    setSpeaking(true);
    window.speechSynthesis.speak(utterance);
  };

  const handleFeedback = async (rating) => {
    if (feedback) return;
    setFeedback(rating);
    toast.success(rating === 'up' ? '👍 Marked as helpful!' : '👎 Thanks for the feedback!');
    try {
      await fetch('http://localhost:8000/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: question || '', answer: message, rating, username: user || 'anonymous' })
      });
    } catch { /* silent */ }
  };

  // Code block
  if (safeSender === 'code') {
    return (
      <div className="message-row ai animate-entrance">
        <div className="message-wrapper full-width-code">
          <div className="anti-gravity-container">
            <div className="anti-gravity-card glassmorphism neon-border">
              {/* macOS Top Bar */}
              <div className="code-card-header">
                <div className="traffic-lights">
                  <span className="dot red"></span>
                  <span className="dot yellow"></span>
                  <span className="dot green"></span>
                </div>
                <div className="card-title">
                  <Code size={12} className="title-icon" />
                  <span>Code Generator — {subject || 'Python'}</span>
                </div>
                <button className="copy-btn-neon" onClick={handleCopy}>
                  <span>Copy</span>
                </button>
              </div>
              
              <div className="code-area-glow">
                <SyntaxHighlighter 
                  language="python" 
                  style={oneLight}
                  customStyle={{ 
                    margin: 0, 
                    padding: '2.5rem 3rem', 
                    background: 'transparent', 
                    fontSize: '0.9rem',
                    lineHeight: '1.8'
                  }}
                >
                  {message}
                </SyntaxHighlighter>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`message-row ${safeSender === 'ai' ? 'ai' : 'user'}`}>
      <div className="message-wrapper">
        <div className="message-meta">
          {safeSender === 'ai' ? 'Assistant' : 'You'}
        </div>

          <div className="message-content-flex">
            <div className={`avatar-orb ${safeSender === 'ai' ? 'ai' : 'user'}`}>
              {safeSender === 'ai' ? <Bot size={20} /> : <User size={20} />}
            </div>
            
            <div className="message-bubble-column">
            <div className="message-bubble">
          {safeSender === 'ai' ? (
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                p: ({node, ...props}) => <p style={{margin: '0 0 8px', lineHeight: 1.65}} {...props}/>,
                ul: ({node, ...props}) => <ul style={{paddingLeft: '1.4em', margin: '6px 0'}} {...props}/>,
                ol: ({node, ...props}) => <ol style={{paddingLeft: '1.4em', margin: '6px 0'}} {...props}/>,
                li: ({node, ...props}) => <li style={{marginBottom: '4px'}} {...props}/>,
                code({node, inline, className, children, ...props}) {
                  const match = /language-(\w+)/.exec(className || '');
                  return !inline && match ? (
                    <SyntaxHighlighter
                      style={theme === 'dark' ? oneDark : oneLight}
                      language={match[1]}
                      PreTag="div"
                      customStyle={{ borderRadius: '8px', margin: '12px 0' }}
                      {...props}
                    >
                      {String(children).replace(/\n$/, '')}
                    </SyntaxHighlighter>
                  ) : (
                    <code 
                      className={className} 
                      style={{
                        background: 'var(--bg-main)', 
                        padding: '2px 6px', 
                        borderRadius: '4px', 
                        fontSize: '0.9em', 
                        fontFamily: 'var(--mono)',
                        border: '1px solid var(--border-color)'
                      }} 
                      {...props}
                    >
                      {children}
                    </code>
                  );
                },
                h1: ({node, ...props}) => <h1 style={{fontSize:'1.2em', fontWeight:700, margin:'8px 0 4px', color:'var(--text-primary)'}} {...props}/>,
                h2: ({node, ...props}) => <h2 style={{fontSize:'1.1em', fontWeight:700, margin:'6px 0 4px', color:'var(--text-primary)'}} {...props}/>,
                h3: ({node, ...props}) => <h3 style={{fontSize:'1em', fontWeight:700, margin:'6px 0 2px', color:'var(--text-primary)'}} {...props}/>,
                strong: ({node, ...props}) => <strong style={{fontWeight:600, color:'var(--text-primary)'}} {...props}/>,
                blockquote: ({node, ...props}) => <blockquote style={{borderLeft:'3px solid var(--primary)', marginLeft:0, paddingLeft:'12px', color:'var(--text-secondary)', fontStyle:'italic'}} {...props}/>,
                table: ({node, ...props}) => <div style={{overflowX:'auto'}}><table style={{borderCollapse:'collapse', width:'100%', margin:'8px 0'}} {...props}/></div>,
                th: ({node, ...props}) => <th style={{border:'1px solid var(--border-color)', padding:'6px 10px', background:'var(--bg-main)', textAlign:'left', color:'var(--text-primary)'}} {...props}/>,
                td: ({node, ...props}) => <td style={{border:'1px solid var(--border-color)', padding:'6px 10px', color:'var(--text-secondary)'}} {...props}/>,
              }}
            >
              {message}
            </ReactMarkdown>
          ) : (
            message
          )}
        </div>

        {safeSender === 'ai' && matched_question && (
          <div className="explainability-card">
            <div className="explainability-left">
              <span className="explain-label">Matched Dataset Question:</span>
              <span className="explain-text">"{matched_question}"</span>
            </div>
            <div className="explainability-right">
              <span className="explain-label" style={{ marginRight: '12px' }}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ verticalAlign: 'middle', marginRight: '4px', position: 'relative', top: '-1px' }}><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                {time_taken ? `${Number(time_taken).toFixed(1)}s` : '0.0s'}
              </span>
              <span className="explain-label">
                Confidence: {confidence ? confidence.toFixed(2) : '-'}
              </span>
              <span className={`confidence-badge confidence-${confidence_level?.toLowerCase() || 'low'}`} style={{ marginLeft: '8px' }}>
                {confidence_level || 'Low'}
              </span>
            </div>
          </div>
        )}

        {safeSender === 'ai' && (
          <div className="feedback-bar">
            <button className={`thumb-btn ${feedback === 'up' ? 'active up' : ''}`} onClick={() => handleFeedback('up')} disabled={!!feedback} title="Helpful">👍</button>
            <button className={`thumb-btn ${feedback === 'down' ? 'active down' : ''}`} onClick={() => handleFeedback('down')} disabled={!!feedback} title="Not helpful">👎</button>
            <button className="action-icon-btn" onClick={handleCopy} title="Copy message">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
            </button>
            <button className={`action-icon-btn ${speaking ? 'active-voice' : ''}`} onClick={handleVoice} title={speaking ? 'Stop speaking' : 'Read aloud'}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>
            </button>
            {isLast && onRegenerate && (
              <button className="action-icon-btn regenerate-btn" onClick={onRegenerate} title="Regenerate response">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
                Retry
              </button>
            )}
            {feedback && <span className="feedback-thanks">Thanks!</span>}
          </div>
        )}
        </div>
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;
