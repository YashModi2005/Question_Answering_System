import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { Toaster } from 'react-hot-toast'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 2500,
            style: { fontFamily: 'Inter, sans-serif', fontSize: '0.875rem', borderRadius: '10px', boxShadow: '0 8px 20px rgba(0,0,0,0.08)' },
            success: { iconTheme: { primary: '#6366f1', secondary: '#fff' } }
          }}
        />
        <App />
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>,
)
