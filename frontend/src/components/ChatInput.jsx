import React, { useState, useEffect, useRef } from 'react';
import { Paperclip, Send, Mic, Square, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';

const ChatInput = ({ input, setInput, onSend, isLoading, session_id }) => {
  const [isListening, setIsListening] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const recognitionRef = useRef(null);
  const fileInputRef = useRef(null);
  const pendingSendRef = useRef(false);

  // Timer while recording
  useEffect(() => {
    let interval;
    if (isListening) {
      setRecordingTime(0);
      interval = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    } else {
      setRecordingTime(0);
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [isListening]);

  // Initialize speech recognition
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recog = new SpeechRecognition();
      recog.continuous = false;
      recog.interimResults = false;
      recog.lang = 'en-US';

      recog.onstart = () => setIsListening(true);

      recog.onend = () => {
        setIsListening(false);
        // If user tried to send while mic was on, send now after recognition ends
        if (pendingSendRef.current) {
          pendingSendRef.current = false;
          setTimeout(() => onSend(), 100); // small delay so state updates
        }
      };

      recog.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInput(prev => prev + (prev ? ' ' : '') + transcript);
      };

      recognitionRef.current = recog;
    }
  }, [setInput, onSend]);

  const toggleListen = () => {
    if (isListening) {
      recognitionRef.current?.stop();
    } else {
      recognitionRef.current?.start();
    }
  };

  const handleSend = () => {
    if (isListening) {
      // Stop mic, then send when it ends (via pendingSendRef)
      pendingSendRef.current = true;
      recognitionRef.current?.stop();
    } else {
      onSend();
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      toast.error('Only PDF files are supported.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    if (session_id) {
      formData.append('session_id', session_id);
    }

    setIsUploading(true);
    const loadingToast = toast.loading(`Uploading ${file.name}...`);

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
      toast.success(`Successfully added ${file.name} to knowledge base!`, { id: loadingToast });
      
      // Optionally notify user about the new capability
      setInput(`Summarize the document: ${file.name}`);
      
    } catch (error) {
      console.error('Upload error:', error);
      toast.error(`Failed to process PDF: ${error.message}`, { id: loadingToast });
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div className="input-glow-wrapper">
      <div className="input-actions-left">
        <input 
          type="file" 
          ref={fileInputRef}
          onChange={handleFileUpload}
          accept=".pdf"
          style={{ display: 'none' }}
        />
        <button
          className="action-btn upload-paperclip"
          onClick={() => fileInputRef.current?.click()}
          title="Upload PDF Knowledge"
          disabled={isUploading || isLoading}
          type="button"
        >
          {isUploading ? <Loader2 className="animate-spin" size={18} /> : <Paperclip size={18} />}
        </button>

        <div className={`mic-container ${isListening ? 'active' : ''}`}>
          <button
            className={`mic-btn ${isListening ? 'listening' : ''}`}
            onClick={toggleListen}
            title={isListening ? 'Stop Recording' : 'Start Voice Input'}
            type="button"
            disabled={isUploading || isLoading}
          >
            <Mic size={18} />
          </button>
          {isListening && (
            <span className="recording-timer">{formatTime(recordingTime)}</span>
          )}
        </div>
      </div>
      <input
        type="text"
        className="chat-input-dashboard"
        placeholder={isListening ? 'Listening...' : 'Type your technical inquiry here...'}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={isLoading}
      />
      <button
        className="send-btn-dashboard"
        onClick={handleSend}
        disabled={isLoading || (!input.trim() && !isListening)}
      >
        {isLoading ? 'Processing...' : isListening ? '⏹ Send' : 'Send'}
      </button>
    </div>
  );
};

export default ChatInput;
