import React, { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [role, setRole] = useState(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      // Persistence: Check sessionStorage on boot
      const savedUser = sessionStorage.getItem('yashu_auth_user');
      const savedRole = sessionStorage.getItem('yashu_auth_role');
      const savedBootId = sessionStorage.getItem('yashu_auth_boot_id');

      if (savedUser && savedRole && savedBootId) {
        try {
          // Check if server has restarted
          const res = await fetch('http://localhost:8000/admin/boot-id');
          if (res.ok) {
            const data = await res.json();
            if (data.boot_id === savedBootId) {
              setUser(savedUser);
              setRole(savedRole);
              setIsLoggedIn(true);
            } else {
              // Server restarted, clear session
              logout();
            }
          } else {
            // Server offline or error, safety logout
            logout();
          }
        } catch {
          logout();
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = (username, userRole) => {
    // Get current boot ID on login
    fetch('http://localhost:8000/admin/boot-id')
      .then(res => res.json())
      .then(data => {
        setUser(username);
        setRole(userRole);
        setIsLoggedIn(true);
        sessionStorage.setItem('yashu_auth_user', username);
        sessionStorage.setItem('yashu_auth_role', userRole);
        sessionStorage.setItem('yashu_auth_boot_id', data.boot_id);
      }).catch(() => {
        // Fallback if boot-id fails
        setUser(username);
        setRole(userRole);
        setIsLoggedIn(true);
        sessionStorage.setItem('yashu_auth_user', username);
        sessionStorage.setItem('yashu_auth_role', userRole);
      });
  };

  const logout = () => {
    setUser(null);
    setRole(null);
    setIsLoggedIn(false);
    sessionStorage.clear(); // Clear all session data on logout
  };

  return (
    <AuthContext.Provider value={{ user, role, isLoggedIn, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
