import React from "react";
import { Link } from "react-router-dom";
import { Mail, Phone, MapPin, Github, Linkedin, Twitter } from "lucide-react";
import "./Footer.css";

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer-container">
        {/* About Section */}
        <div className="footer-section">
          <h3 className="footer-title">
            <span className="footer-logo">🌱</span> AgriGenAI
          </h3>
          <p className="footer-description">
            AI-Powered Plant Phenotype Analysis & Hybrid Recommendations.
            Empowering farmers with intelligent breeding decisions.
          </p>
          <p className="footer-tagline">"Smart Farming, Better Yields"</p>
        </div>

        {/* Quick Links */}
        <div className="footer-section">
          <h4 className="footer-heading">Quick Links</h4>
          <ul className="footer-links">
            <li>
              <Link to="/">Home</Link>
            </li>
            <li>
              <Link to="/analysis">Analysis</Link>
            </li>
            <li>
              <Link to="/crops">Crop Database</Link>
            </li>
            <li>
              <Link to="/support">Support</Link>
            </li>
            <li>
              <Link to="/login">Login</Link>
            </li>
          </ul>
        </div>

        {/* Resources */}
        <div className="footer-section">
          <h4 className="footer-heading">Resources</h4>
          <ul className="footer-links">
            <li>
              <a href="#how-it-works">How It Works</a>
            </li>
            <li>
              <a href="#features">Features</a>
            </li>
            <li>
              <a href="#faq">FAQ</a>
            </li>
            <li>
              <a href="#privacy">Privacy Policy</a>
            </li>
            <li>
              <a href="#terms">Terms of Service</a>
            </li>
          </ul>
        </div>

        {/* Contact Info */}
        <div className="footer-section">
          <h4 className="footer-heading">Contact Us</h4>
          <ul className="footer-contact">
            <li>
              <Mail size={18} />
              <a href="mailto:support@agrigenai.com">support@agrigenai.com</a>
            </li>
            <li>
              <Phone size={18} />
              <a href="tel:+911234567890">+91 123 456 7890</a>
            </li>
            <li>
              <MapPin size={18} />
              <span>Mysuru, Karnataka, India</span>
            </li>
          </ul>

          {/* Social Links */}
          <div className="footer-social">
            <a
              href="https://github.com/agrigenai"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="GitHub"
            >
              <Github size={20} />
            </a>
            <a
              href="https://linkedin.com/company/agrigenai"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="LinkedIn"
            >
              <Linkedin size={20} />
            </a>
            <a
              href="https://twitter.com/agrigenai"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Twitter"
            >
              <Twitter size={20} />
            </a>
          </div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="footer-bottom">
        <div className="footer-bottom-container">
          <p className="footer-copyright">
            © {currentYear} AgriGenAI. All rights reserved.
          </p>
          <p className="footer-made-with">Made with ❤️ in India 🇮🇳</p>
          <p className="footer-tech">Powered by ML & AI | Accuracy: 92.85%</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
