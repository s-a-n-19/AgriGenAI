import React from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Sparkles,
  Brain,
  Leaf,
  TrendingUp,
  Shield,
  Zap,
  Upload,
  ScanLine,
  FileText,
  ShoppingBag,
  ArrowRight,
  CheckCircle,
} from "lucide-react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import "./Dashboard.css";

const Dashboard = () => {
  const features = [
    {
      icon: <Brain size={40} />,
      title: "AI-Powered Analysis",
      description:
        "Advanced machine learning models with 92.85% accuracy for precise trait prediction",
    },
    {
      icon: <Leaf size={40} />,
      title: "Genotype Prediction",
      description:
        "Identify plant genotypes and genetic traits from simple images",
    },
    {
      icon: <TrendingUp size={40} />,
      title: "Breeding Recommendations",
      description: "Get optimal cross-breeding suggestions for better yields",
    },
    {
      icon: <Shield size={40} />,
      title: "Disease Resistance",
      description: "Evaluate disease resistance and stress tolerance levels",
    },
    {
      icon: <Zap size={40} />,
      title: "Weather Integration",
      description:
        "Context-aware recommendations based on local weather conditions",
    },
    {
      icon: <ShoppingBag size={40} />,
      title: "Seed Marketplace",
      description: "Purchase recommended hybrid seeds and saplings directly",
    },
  ];

  const howItWorks = [
    {
      step: 1,
      icon: <Upload size={32} />,
      title: "Upload Plant Image",
      description:
        "Take a clear photo of your plant and upload it to our platform",
    },
    {
      step: 2,
      icon: <ScanLine size={32} />,
      title: "AI Analysis",
      description:
        "Our ML models analyze traits: yield, disease resistance, stress tolerance",
    },
    {
      step: 3,
      icon: <FileText size={32} />,
      title: "Get Recommendations",
      description:
        "Receive breeding suggestions and alternative hybrid options",
    },
    {
      step: 4,
      icon: <ShoppingBag size={32} />,
      title: "Purchase Seeds",
      description:
        "Buy recommended seeds/saplings and download detailed reports",
    },
  ];

  return (
    <div className="dashboard">
      <Navbar />

      {/* Hero Section */}
      <section className="hero">
        <div className="hero-background">
          <div className="hero-overlay"></div>
        </div>

        <div className="hero-content">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="hero-text"
          >
            <div className="hero-badge">
              <Sparkles size={16} />
              <span>Powered by AI & ML</span>
            </div>

            <h1 className="hero-title">
              <span className="gradient-text">Smart Farming,</span>
              <br />
              Better Yields
            </h1>

            <p className="hero-description">
              Transform your agricultural decisions with AI-powered plant
              phenotype analysis. Get accurate trait predictions, optimal
              breeding recommendations, and data-driven insights to maximize
              your crop yields.
            </p>

            <div className="hero-stats">
              <div className="stat">
                <div className="stat-value">92.85%</div>
                <div className="stat-label">Model Accuracy</div>
              </div>
              <div className="stat">
                <div className="stat-value">54K+</div>
                <div className="stat-label">Training Samples</div>
              </div>
              <div className="stat">
                <div className="stat-value">3</div>
                <div className="stat-label">Trait Models</div>
              </div>
            </div>

            <div className="hero-buttons">
              <Link to="/analysis" className="btn btn-primary">
                <Sparkles size={20} />
                Start Analysis
                <ArrowRight size={20} />
              </Link>
              <Link to="/crops" className="btn btn-secondary">
                Browse Crops
              </Link>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="hero-image"
          >
            <div className="hero-image-container">
              <img
                src="https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=800"
                alt="Plant Analysis"
                className="hero-img"
              />
              <div className="hero-image-overlay">
                <div className="floating-card">
                  <CheckCircle size={20} className="check-icon" />
                  <span>AI Analysis Complete</span>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features" id="features">
        <div className="section-container">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="section-header"
          >
            <h2 className="section-title">Why Choose AgriGenAI?</h2>
            <p className="section-subtitle">
              Comprehensive features designed for modern farmers
            </p>
          </motion.div>

          <div className="features-grid">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="feature-card"
              >
                <div className="feature-icon">{feature.icon}</div>
                <h3 className="feature-title">{feature.title}</h3>
                <p className="feature-description">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works" id="how-it-works">
        <div className="section-container">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="section-header"
          >
            <h2 className="section-title">How It Works</h2>
            <p className="section-subtitle">
              Simple 4-step process to get AI-powered recommendations
            </p>
          </motion.div>

          <div className="steps-container">
            {howItWorks.map((step, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.15 }}
                className="step-card"
              >
                <div className="step-number">{step.step}</div>
                <div className="step-icon">{step.icon}</div>
                <h3 className="step-title">{step.title}</h3>
                <p className="step-description">{step.description}</p>
                {index < howItWorks.length - 1 && (
                  <div className="step-connector">
                    <ArrowRight size={24} />
                  </div>
                )}
              </motion.div>
            ))}
          </div>

          <div className="cta-container">
            <Link to="/analysis" className="btn btn-large">
              <Sparkles size={24} />
              Get Started Now
              <ArrowRight size={24} />
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="section-container">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="cta-card"
          >
            <h2 className="cta-title">Ready to Transform Your Farming?</h2>
            <p className="cta-description">
              Join thousands of farmers already using AI to make smarter
              breeding decisions
            </p>
            <div className="cta-buttons">
              <Link to="/signup" className="btn btn-cta-primary">
                Create Free Account
              </Link>
              <Link to="/support" className="btn btn-cta-secondary">
                Talk to Expert
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default Dashboard;
