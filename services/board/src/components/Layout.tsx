import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import './Layout.css'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const { logout } = useAuthStore()

  const navItems = [
    { path: '/', label: 'Dashboard', icon: '📊' },
    { path: '/runs', label: 'Runs', icon: '▶️' },
    { path: '/projects', label: 'Projects', icon: '📁' },
    { path: '/infrastructure', label: 'Infrastructure', icon: '⚙️' },
    { path: '/configuration', label: 'Configuration', icon: '🔧' },
  ]

  return (
    <div className="layout">
      <nav className="sidebar">
        <div className="sidebar-header">
          <h1>QAtron</h1>
        </div>
        <ul className="nav-list">
          {navItems.map((item) => (
            <li key={item.path}>
              <Link
                to={item.path}
                className={location.pathname === item.path ? 'active' : ''}
              >
                <span className="icon">{item.icon}</span>
                {item.label}
              </Link>
            </li>
          ))}
        </ul>
        <div className="sidebar-footer">
          <button onClick={logout} className="logout-btn">
            Logout
          </button>
        </div>
      </nav>
      <main className="main-content">{children}</main>
    </div>
  )
}
