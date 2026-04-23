import React from 'react';
import { Link } from 'react-router-dom';
import { Database, Cpu, Layers, Activity, User, Search, Terminal, Key } from 'lucide-react';

const ArchitectureInfo = () => {
  return (
    <div className="auth-page" style={{ background: '#f8fafc', overflowY: 'auto' }}>
      <div className="arch-page-wrapper">
        <div className="nav-header">
          <Link to="/dashboard" className="back-link">← Back to Terminal</Link>
        </div>
        
        <div className="admin-header" style={{ marginBottom: '40px' }}>
          <div className="admin-title-row">
            <div className="premium-logo-box">🏛️</div>
            <div>
              <h1 className="technical-title">System Architecture</h1>
              <p className="access-subtitle">Technical blueprint of the RAG Knowledge Engine</p>
            </div>
          </div>
          <div className="admin-badge" style={{ 
            background: 'linear-gradient(135deg, #6366f1, #06b6d4)', 
            color: 'white',
            fontWeight: '800',
            fontSize: '0.7rem',
            letterSpacing: '0.15em',
            padding: '8px 16px',
            borderRadius: '20px',
            boxShadow: '0 4px 12px rgba(99, 102, 241, 0.3)',
            textTransform: 'uppercase'
          }}>CORE LOGIC</div>
        </div>

        <div className="arch-stats-grid">
          {[
            { label: 'VECTOR DB', value: 'FAISS (Meta)', Icon: Database },
            { label: 'BASE LLM', value: 'Llama 3.2', Icon: Cpu },
            { label: 'EMBEDDINGS', value: 'MiniLM-L6', Icon: Layers },
            { label: 'API FRAMEWORK', value: 'FastAPI', Icon: Activity },
          ].map((item, i) => (
            <div key={i} className="arch-stack-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
                <span className="stack-label">{item.label}</span>
                <item.Icon size={16} color="#6366f1" />
              </div>
              <span className="stack-value">{item.value}</span>
            </div>
          ))}
        </div>

        <div className="neural-pipeline-card">
          <h2 className="technical-title" style={{ fontSize: '1.2rem', marginBottom: '40px', textAlign: 'center' }}>
            The RAG Knowledge Pipeline
          </h2>
          
          <div className="neural-flow-container">
            {[
              { title: 'User Input', desc: 'Secure query ingestion', Icon: User, active: false },
              { title: 'Embedding Model', desc: 'Converts text into 384-dimensional Vectors', Icon: Key, active: true },
              { title: 'Similarity Search', desc: 'Queries FAISS indexing for tech context', Icon: Search, active: true },
              { title: 'Generative AI', desc: 'Llama 3.2 synthesizes final reasoning', Icon: Terminal, active: true },
              { title: 'Final Answer', desc: 'Optimized technical solution delivery', Icon: Activity, active: false },
            ].map((node, i, arr) => (
              <React.Fragment key={i}>
                <div className={`neural-node ${node.active ? 'active' : ''}`}>
                  <div className="node-icon-box">
                    <node.Icon size={20} />
                  </div>
                  <div className="node-content">
                    <span className="node-title">{node.title}</span>
                    <span className="node-desc">{node.desc}</span>
                  </div>
                </div>
                {i < arr.length - 1 && <div className="flow-connector"></div>}
              </React.Fragment>
            ))}
          </div>
        </div>

        <div className="arch-kpi-grid">
          <div className="arch-kpi-card indigo">
            <h3>Why FAISS?</h3>
            <p style={{ fontSize: '0.9rem', opacity: 0.9, lineHeight: '1.6' }}>
              Meta's FAISS allows us to perform "Semantic Search" instead of just keyword matching. 
              Even if the user phrases a question differently, we find the right answer through vector mathematics.
            </p>
          </div>
          <div className="arch-kpi-card purple">
            <h3>Local Inference</h3>
            <p style={{ fontSize: '0.9rem', opacity: 0.9, lineHeight: '1.6' }}>
              The system runs entirely on your local machine using <strong>Ollama</strong>. 
              No data is sent to external clouds, ensuring 100% privacy and zero-latency technical assistance.
            </p>
          </div>
        </div>

        <div className="signature-branding" style={{ textAlign: 'center', marginTop: '60px' }}>
          ENGINEERED BY <span>YASHU</span>
        </div>
      </div>
    </div>
  );
};

export default ArchitectureInfo;
