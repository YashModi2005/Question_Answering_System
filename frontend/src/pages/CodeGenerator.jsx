import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Code, Terminal, Zap, Download, Copy, Play } from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark, oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import toast from 'react-hot-toast';

const CodeGenerator = () => {
  const [prompt, setPrompt] = useState('');
  const [language, setLanguage] = useState('python');
  const [generatedCode, setGeneratedCode] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerate = async () => {
    if (!prompt.trim()) return toast.error('Please enter a prompt first!');
    
    setIsGenerating(true);
    setGeneratedCode('');
    
    try {
      // We use the existing /ask endpoint but wrap the prompt to force code generation
      const response = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          question: `Generate a detailed ${language} code snippet for: ${prompt}. Only return the code block.` 
        }),
      });

      if (!response.ok) throw new Error("Backend unreachable");
      
      const data = await response.json();
      // Clean up the response to extract just the code if LLM included text
      const codeMatch = data.answer.match(/```(?:\w+)?\n([\s\S]*?)```/) || [null, data.answer];
      setGeneratedCode(codeMatch[1].trim());
      toast.success('Code Generated Successfully!');
    } catch (error) {
      toast.error('Generation Failed. Is the backend running?');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(generatedCode);
    toast.success('Copied to clipboard!');
  };

  return (
    <div className="generator-page-wrapper">
      <div className="particle-background"></div>
      
      <div className="nav-header" style={{ padding: '20px 40px' }}>
        <Link to="/dashboard" className="back-link">← Return to Home Office</Link>
      </div>

      <div className="generator-content">
        {/* Floating Input Panel */}
        <div className="generator-input-card glassmorphism float-slow">
          <div className="input-glow-accent"></div>
          <div className="input-header">
            <Zap size={18} className="neon-cyan" />
            <h3>Neural Code Lab</h3>
          </div>
          
          <div className="input-group-cyber">
            <textarea
              className="cyber-textarea"
              placeholder="Describe the algorithm or component you want to build..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
            />
          </div>

          <div className="control-row">
            <div className="cyber-select-wrapper">
              <select 
                className="cyber-select"
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
              >
                <option value="python">Python 3.12</option>
                <option value="javascript">JavaScript (ES6+)</option>
                <option value="cpp">C++ 20</option>
                <option value="java">Java 21</option>
              </select>
            </div>
            
            <button 
              className={`generate-btn-neon ${isGenerating ? 'loading' : ''}`}
              onClick={handleGenerate}
              disabled={isGenerating}
            >
              <div className="btn-shine"></div>
              {isGenerating ? 'Synthesizing...' : 'GENERATE CODE'}
            </button>
          </div>
        </div>

        {/* Results Area */}
        {generatedCode && (
          <div className="anti-gravity-container result-entrance">
            <div className="anti-gravity-card glassmorphism neon-purple">
              <div className="code-card-header">
                <div className="traffic-lights">
                  <span className="dot red"></span>
                  <span className="dot yellow"></span>
                  <span className="dot green"></span>
                </div>
                <div className="card-title">
                  <Terminal size={14} className="title-icon-purple" />
                  <span>Synthesized Output — {language.toUpperCase()}</span>
                </div>
                <div className="card-actions">
                  <button className="action-neon-btn" onClick={handleCopy} title="Copy Code">
                    <Copy size={16} />
                  </button>
                  <button className="action-neon-btn" title="Download File">
                    <Download size={16} />
                  </button>
                </div>
              </div>
              
              <div className="code-area-scrollable">
                <SyntaxHighlighter 
                  language={language} 
                  style={oneLight}
                  customStyle={{ 
                    margin: 0, 
                    padding: '2.5rem 3.5rem', 
                    background: 'transparent', 
                    fontSize: '0.95rem',
                    lineHeight: '1.9'
                  }}
                >
                  {generatedCode}
                </SyntaxHighlighter>
              </div>
            </div>
          </div>
        )}
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        .generator-page-wrapper {
          min-height: 100vh;
          width: 100%;
          background: #020617;
          position: relative;
          color: white;
          overflow-x: hidden;
        }

        .generator-content {
          max-width: 900px;
          margin: 0 auto;
          padding: 20px;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 40px;
        }

        /* Particles */
        .particle-background {
          position: fixed;
          top: 0; left: 0; width: 100%; height: 100%;
          background-image: 
            radial-gradient(circle at 2px 2px, rgba(99, 102, 241, 0.15) 1px, transparent 0);
          background-size: 40px 40px;
          z-index: 0;
          pointer-events: none;
        }

        /* Glassmorphism Input Card */
        .generator-input-card {
          width: 100%;
          padding: 30px;
          border-radius: 28px;
          position: relative;
          z-index: 10;
          border: 1px solid rgba(255, 255, 255, 0.1);
          box-shadow: 0 30px 60px rgba(0,0,0,0.5);
        }

        .input-glow-accent {
          position: absolute;
          top: -20px; left: 50%; transform: translateX(-50%);
          width: 40%; height: 2px;
          background: linear-gradient(90deg, transparent, #06b6d4, transparent);
          box-shadow: 0 0 20px #06b6d4;
        }

        .input-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 20px;
        }

        .input-header h3 {
          margin: 0;
          font-size: 0.9rem;
          text-transform: uppercase;
          letter-spacing: 0.2em;
          color: #94a3b8;
        }

        .cyber-textarea {
          width: 100%;
          height: 120px;
          background: rgba(0,0,0,0.3);
          border: 1px solid rgba(255, 255, 255, 0.05);
          border-radius: 16px;
          padding: 20px;
          color: #e2e8f0;
          font-family: inherit;
          font-size: 1rem;
          resize: none;
          outline: none;
          transition: border-color 0.3s ease;
        }

        .cyber-textarea:focus {
          border-color: #06b6d4;
        }

        .control-row {
          display: flex;
          justify-content: space-between;
          margin-top: 20px;
          gap: 20px;
        }

        .cyber-select {
          background: rgba(15, 23, 42, 0.8);
          color: white;
          border: 1px solid rgba(255, 255, 255, 0.1);
          padding: 10px 20px;
          border-radius: 12px;
          outline: none;
          cursor: pointer;
          min-width: 180px;
        }

        .generate-btn-neon {
          flex: 1;
          background: linear-gradient(90deg, #6366f1, #06b6d4);
          color: white;
          font-weight: 800;
          border: none;
          border-radius: 12px;
          letter-spacing: 0.1em;
          cursor: pointer;
          transition: all 0.3s ease;
          position: relative;
          overflow: hidden;
        }

        .generate-btn-neon:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 0 30px rgba(99, 102, 241, 0.4);
        }

        .btn-shine {
          position: absolute;
          top: 0; left: -100%;
          width: 100%; height: 100%;
          background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
          animation: shine 3s infinite;
        }

        @keyframes shine {
          to { left: 100%; }
        }

        /* Animations */
        .float-slow {
          animation: floating 8s ease-in-out infinite;
        }

        .result-entrance {
          animation: slideUpFade 0.7s cubic-bezier(0.19, 1, 0.22, 1) forwards;
        }

        @keyframes slideUpFade {
          from { opacity: 0; transform: translateY(40px); }
          to { opacity: 1; transform: translateY(0); }
        }

        .neon-cyan { color: #06b6d4; filter: drop-shadow(0 0 5px #06b6d4); }
        .title-icon-purple { color: #a855f7; filter: drop-shadow(0 0 5px #a855f7); }
        
        .action-neon-btn {
          background: transparent;
          border: none;
          color: #94a3b8;
          cursor: pointer;
          padding: 8px;
          border-radius: 8px;
          transition: all 0.2s ease;
        }

        .action-neon-btn:hover {
          color: white;
          background: rgba(255, 255, 255, 0.1);
        }
      `}} />
    </div>
  );
};

export default CodeGenerator;
