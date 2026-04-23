import React from 'react';
import { User } from 'lucide-react';

const SidebarProfile = ({ user }) => {
  return (
    <div className="sidebar-profile">
      <div className="avatar-orb user">
        <User size={18} />
      </div>
      <div className="sidebar-user-info">
        <span className="sidebar-user-name">{user?.username || 'Guest User'}</span>
        <span className="sidebar-user-role">{user?.role || 'User'}</span>
      </div>
    </div>
  );
};

export default SidebarProfile;
