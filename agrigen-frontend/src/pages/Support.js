import React, { useState } from "react";
import { Phone, MessageCircle, Mail, Clock } from "lucide-react";
import { toast } from "react-toastify";
import "./Support.css";

const expertsData = [
  {
    id: 1,
    name: "Dr. Ramesh Kumar",
    specialty: "Crop Disease Expert",
    experience: "15 years",
    price: 500,
    photo: "👨‍🔬",
    phone: "+91-9876543210",
    whatsapp: "+919876543210",
  },
  {
    id: 2,
    name: "Dr. Priya Sharma",
    specialty: "Soil & Fertilizer Specialist",
    experience: "12 years",
    price: 450,
    photo: "👩‍🔬",
    phone: "+91-9876543211",
    whatsapp: "+919876543211",
  },
  {
    id: 3,
    name: "Vijay Patel",
    specialty: "Irrigation Expert",
    experience: "10 years",
    price: 400,
    photo: "👨‍🌾",
    phone: "+91-9876543212",
    whatsapp: "+919876543212",
  },
];

const Support = () => {
  const [showBooking, setShowBooking] = useState(null);

  const handleCall = (phone) => {
    window.location.href = `tel:${phone}`;
  };

  const handleWhatsApp = (phone) => {
    window.open(`https://wa.me/${phone}`, "_blank");
  };

  const handleBooking = (expertName) => {
    toast.success(`Booking request sent to ${expertName}!`);
    setShowBooking(null);
  };

  return (
    <div className="support-page">
      <div className="support-container">
        <div className="support-header">
          <h1>🤝 Connect with Experts</h1>
          <p>Get professional guidance from agricultural specialists</p>
        </div>

        <div className="experts-grid">
          {expertsData.map((expert) => (
            <div key={expert.id} className="expert-card">
              <div className="expert-photo">{expert.photo}</div>
              <h3>{expert.name}</h3>
              <p className="specialty">{expert.specialty}</p>
              <div className="expert-details">
                <span className="experience">
                  <Clock size={16} />
                  {expert.experience}
                </span>
                <span className="price">₹{expert.price}/hour</span>
              </div>
              <div className="contact-buttons">
                <button
                  className="call-btn"
                  onClick={() => handleCall(expert.phone)}
                >
                  <Phone size={18} />
                  Call
                </button>
                <button
                  className="whatsapp-btn"
                  onClick={() => handleWhatsApp(expert.whatsapp)}
                >
                  <MessageCircle size={18} />
                  WhatsApp
                </button>
              </div>
              <button
                className="book-btn"
                onClick={() => setShowBooking(expert.id)}
              >
                Book Appointment
              </button>
            </div>
          ))}
        </div>

        <div className="faq-section">
          <h2>Frequently Asked Questions</h2>
          <div className="faq-grid">
            <div className="faq-item">
              <h4>How does the AI analysis work?</h4>
              <p>
                Upload a plant image and our AI model analyzes genotype,
                diseases, and recommends breeding partners based on 92.85%
                accurate predictions.
              </p>
            </div>
            <div className="faq-item">
              <h4>How accurate are the recommendations?</h4>
              <p>
                Our ML models achieve 92.85% accuracy in genotype prediction and
                trait analysis, trained on thousands of plant images.
              </p>
            </div>
            <div className="faq-item">
              <h4>Can I buy seeds directly?</h4>
              <p>
                Yes! Browse our crop database and add seeds to cart. We deliver
                across India.
              </p>
            </div>
            <div className="faq-item">
              <h4>Do experts provide on-site visits?</h4>
              <p>
                Consultations start online. On-site visits can be arranged
                separately with the expert.
              </p>
            </div>
          </div>
        </div>

        <div className="contact-section">
          <h2>Still Have Questions?</h2>
          <div className="contact-info">
            <div className="contact-item">
              <Mail size={24} />
              <div>
                <strong>Email Us</strong>
                <p>support@agrigenai.com</p>
              </div>
            </div>
            <div className="contact-item">
              <Phone size={24} />
              <div>
                <strong>Call Us</strong>
                <p>1800-123-4567 (Toll-free)</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {showBooking && (
        <div className="modal-overlay" onClick={() => setShowBooking(null)}>
          <div className="booking-modal" onClick={(e) => e.stopPropagation()}>
            <h3>Book Appointment</h3>
            <p>
              Feature coming soon! For now, please call or WhatsApp the expert
              directly.
            </p>
            <button onClick={() => setShowBooking(null)}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Support;
