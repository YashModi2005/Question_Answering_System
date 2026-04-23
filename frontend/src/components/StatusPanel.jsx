import React from 'react';

const StatusPanel = () => {
  return (
    <div className="system-status-indicator">
      <div className="panel-row">
        <span className="panel-badge">Enhanced Hybrid NLP Engine</span>
        <span className="panel-badge">Conversational Context Active</span>
      </div>
      <div className="panel-row">
        <span className="panel-badge">Memory Enabled</span>
        <span className="panel-badge">Final Elite Build v1.0</span>
      </div>
    </div>
  );
};

export default StatusPanel;
