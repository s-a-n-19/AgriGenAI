import React, { useContext } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { ShoppingCart, User, LogOut, Menu, X } from "lucide-react";
import { AuthContext } from "../context/AuthContext";
import { CartContext } from "../context/CartContext";
import { LanguageContext } from "../context/LanguageContext";
import "./Navbar.css";

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = React.useState(false);
  const authContext = useContext(AuthContext);
  const cartContext = useContext(CartContext);
  const languageContext = useContext(LanguageContext);
  const navigate = useNavigate();
  const location = useLocation();

  // Safely destructure with defaults
  const { user, logout } = authContext || {};
  const { cart = [] } = cartContext || {};
  const { language = "en", setLanguage } = languageContext || {};

  const handleLogout = () => {
    if (logout) logout();
    navigate("/");
  };

  const isActive = (path) => {
    return location.pathname === path ? "active" : "";
  };

  // Safe cart count calculation
  const cartCount = cart.reduce(
    (total, item) => total + (item.quantity || 0),
    0
  );

  return (
    <nav className="navbar">
      <div className="navbar-container">
        {/* Logo - NO ANIMATION */}
        <Link to="/" className="navbar-logo">
          <span className="logo-icon">🌱</span>
          <span className="logo-text">AgriGenAI</span>
        </Link>

        {/* Mobile Menu Toggle */}
        <button
          className="mobile-menu-toggle"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
        >
          {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>

        {/* Navigation Links */}
        <ul className={`navbar-menu ${isMenuOpen ? "open" : ""}`}>
          <li>
            <Link
              to="/"
              className={isActive("/")}
              onClick={() => setIsMenuOpen(false)}
            >
              Home
            </Link>
          </li>
          <li>
            <Link
              to="/analysis"
              className={isActive("/analysis")}
              onClick={() => setIsMenuOpen(false)}
            >
              Analysis
            </Link>
          </li>
          <li>
            <Link
              to="/crops"
              className={isActive("/crops")}
              onClick={() => setIsMenuOpen(false)}
            >
              Crop Database
            </Link>
          </li>
          <li>
            <Link
              to="/support"
              className={isActive("/support")}
              onClick={() => setIsMenuOpen(false)}
            >
              Support
            </Link>
          </li>
        </ul>

        {/* Right Side Actions */}
        <div className="navbar-actions">
          {/* Language Selector */}
          <div className="language-selector">
            <select
              value={language}
              onChange={(e) => setLanguage && setLanguage(e.target.value)}
              className="language-dropdown"
            >
              <option value="en">🇬🇧 English</option>
              <option value="hi" disabled>
                🇮🇳 हिंदी (Coming Soon)
              </option>
              <option value="kn" disabled>
                🇮🇳 ಕನ್ನಡ (Coming Soon)
              </option>
              <option value="ta" disabled>
                🇮🇳 தமிழ் (Coming Soon)
              </option>
              <option value="te" disabled>
                🇮🇳 తెలుగు (Coming Soon)
              </option>
            </select>
          </div>

          {/* Cart */}
          {user && (
            <Link to="/cart" className="cart-button">
              <ShoppingCart size={20} />
              {cartCount > 0 && <span className="cart-badge">{cartCount}</span>}
            </Link>
          )}

          {/* User Actions */}
          {user ? (
            <div className="user-menu">
              <Link to="/profile" className="user-button">
                <User size={20} />
                <span className="user-name">{user.name}</span>
              </Link>
              <button onClick={handleLogout} className="logout-button">
                <LogOut size={18} />
                <span>Logout</span>
              </button>
            </div>
          ) : (
            <div className="auth-buttons">
              <Link to="/login" className="login-button">
                Login
              </Link>
              <Link to="/signup" className="signup-button">
                Sign Up
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
