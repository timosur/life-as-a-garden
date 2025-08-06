import { Link, useLocation } from 'react-router-dom';
import './Navigation.scss';

const Navigation = () => {
  const location = useLocation();

  return (
    <nav className="app-navigation">
      <div className="nav-container">
        <h1 className="app-title">🌱 Life as a Garden</h1>
        <div className="nav-buttons">
          <Link
            to="/"
            className={`nav-button ${location.pathname === '/' ? 'active' : ''}`}
          >
            🏡 Garden
          </Link>
          <Link
            to="/notes"
            className={`nav-button ${location.pathname === '/notes' ? 'active' : ''}`}
          >
            📝 Notes
          </Link>
          <Link
            to="/edit"
            className={`nav-button ${location.pathname === '/edit' ? 'active' : ''}`}
          >
            ✏️ Edit
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
