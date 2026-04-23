import React, { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';

const KnowledgeUpload = () => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null); // 'idle', 'uploading', 'success', 'error'
  const fileInputRef = useRef(null);

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      toast.error('Only PDF files are supported.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setIsUploading(true);
    setUploadStatus('uploading');

    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const data = await response.json();
      setUploadStatus('success');
      toast.success(`Processed ${file.name}: ${data.chunks_added} chunks added.`);
      
      // Reset after 3 seconds
      setTimeout(() => {
        setUploadStatus('idle');
        if (fileInputRef.current) fileInputRef.current.value = '';
      }, 3000);

    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus('error');
      toast.error(`Error: ${error.message}`);
      
      setTimeout(() => setUploadStatus('idle'), 5000);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="knowledge-upload-section">
      <div className="upload-header">
        <Upload size={14} className="text-blue-500" />
        <span>Expand Knowledge Base</span>
      </div>
      
      <div className={`upload-card ${uploadStatus}`}>
        <input 
          type="file" 
          ref={fileInputRef}
          onChange={handleFileChange}
          accept=".pdf"
          style={{ display: 'none' }}
        />
        
        <button 
          className={`upload-btn ${isUploading ? 'loading' : ''}`}
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading}
        >
          {isUploading ? (
            <Loader2 className="animate-spin" size={18} />
          ) : uploadStatus === 'success' ? (
            <CheckCircle className="text-green-500" size={18} />
          ) : uploadStatus === 'error' ? (
            <AlertCircle className="text-red-500" size={18} />
          ) : (
            <FileText size={18} />
          )}
          
          <div className="upload-text">
            {isUploading ? 'Processing PDF...' : 
             uploadStatus === 'success' ? 'Knowledge Added!' : 
             uploadStatus === 'error' ? 'Upload Failed' : 
             'Upload Research PDF'}
          </div>
        </button>
        
        <p className="upload-hint">Extracts text and adds to FAISS index</p>
      </div>
    </div>
  );
};

export default KnowledgeUpload;
