import React, { useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';
import { Cpu, Code, Sigma, Globe, MessageSquare } from 'lucide-react';

const ChatWindow = ({ messages, isLoading, onRegenerate, theme }) => {
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const showWelcome = messages.length <= 1;

  return (
    <div className="chat-window">
      {showWelcome ? (
        <div className="messages-container animate-fade-in">
          <div className="welcome-card card-entrance">
            <div className="welcome-icon">
              <MessageSquare size={28} />
            </div>
            <h2>Knowledge Assistant</h2>
            <p style={{marginBottom: '1.5rem', opacity: 0.8, fontSize: '0.9rem'}}>Curated Technical Insight Engine</p>
            
            <div className="welcome-topics-grid">
              <div className="topic-pill">
                <Cpu size={16} />
                <span>Artificial Intelligence</span>
              </div>
              <div className="topic-pill">
                <Code size={16} />
                <span>Programming</span>
              </div>
              <div className="topic-pill">
                <Sigma size={16} />
                <span>Mathematics</span>
              </div>
              <div className="topic-pill">
                <Globe size={16} />
                <span>Technology</span>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="messages-container">
          {messages.map((msg, index) => {
            const isLastAi = msg.sender === 'ai' && index === messages.length - 1;
            return (
              <MessageBubble
                key={index}
                message={msg.text}
                sender={msg.sender}
                subject={msg.subject}
                question={msg.question}
                confidence={msg.confidence}
                confidence_level={msg.confidence_level}
                matched_question={msg.matched_question}
                time_taken={msg.time_taken}
                isLast={isLastAi}
                onRegenerate={isLastAi ? onRegenerate : undefined}
                theme={theme}
              />
            );
          })}
          {isLoading && (
            <div className="message-row ai">
              <div className="message-wrapper">
                <div className="message-meta">🤖 Assistant</div>
                <div className="message-bubble typing-indicator-bubble" style={{background: 'var(--bg-main)', border: '1px dashed var(--border-active)'}}>
                  <span className="typing-text" style={{color: 'var(--text-secondary)', fontStyle: 'italic'}}>
                    AI is retrieving relevant facts and thinking...
                  </span>
                  <div className="dots-loader">
                    <span className="dot"/><span className="dot"/><span className="dot"/>
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      )}

      {showWelcome && isLoading && (
        <div className="messages-container" style={{paddingTop: 0}}>
          <div className="message-row ai">
            <div className="message-wrapper">
              <div className="message-meta">🤖 Assistant</div>
              <div className="message-bubble typing-indicator-bubble" style={{background: 'var(--bg-main)', border: '1px dashed var(--border-active)'}}>
                <span className="typing-text" style={{color: 'var(--text-secondary)', fontStyle: 'italic'}}>
                  AI is searching the knowledge base...
                </span>
                <div className="dots-loader">
                  <span className="dot"/><span className="dot"/><span className="dot"/>
                </div>
              </div>
            </div>
          </div>
          <div ref={messagesEndRef} />
        </div>
      )}
    </div>
  );
};

export default ChatWindow;
