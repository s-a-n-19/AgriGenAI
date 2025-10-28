import React, { useState, useContext } from "react";
import { CartContext } from "../context/CartContext";
import { useNavigate } from "react-router-dom";
import { CheckCircle, CreditCard, Truck } from "lucide-react";
import { toast } from "react-toastify";
import "./Payment.css";

const Payment = () => {
  const cartContext = useContext(CartContext);
  const navigate = useNavigate();
  const [orderPlaced, setOrderPlaced] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    address: "",
    city: "",
    state: "",
    pincode: "",
    paymentMethod: "cod",
  });

  // Safely destructure with defaults
  const { cart = [], getCartTotal, clearCart } = cartContext || {};

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!formData.name || !formData.phone || !formData.address) {
      toast.error("Please fill all required fields");
      return;
    }

    // Simulate order placement
    setTimeout(() => {
      setOrderPlaced(true);
      if (clearCart) clearCart();
      toast.success("Order placed successfully!");

      setTimeout(() => {
        navigate("/");
      }, 3000);
    }, 1000);
  };

  if (cart.length === 0 && !orderPlaced) {
    navigate("/cart");
    return null;
  }

  if (orderPlaced) {
    const total = getCartTotal ? getCartTotal() : 0;
    const shipping = 50;
    const tax = Math.round(total * 0.18);
    const grandTotal = total + shipping + tax;

    return (
      <div className="payment-page">
        <div className="payment-container">
          <div className="success-message">
            <CheckCircle size={80} className="success-icon" />
            <h1>Order Placed Successfully!</h1>
            <p>Your order has been confirmed and will be delivered soon.</p>
            <div className="order-details">
              <p>
                <strong>Order ID:</strong> AGR{Date.now().toString().slice(-8)}
              </p>
              <p>
                <strong>Total Amount:</strong> ₹{grandTotal}
              </p>
              <p>
                <strong>Delivery Address:</strong> {formData.address},{" "}
                {formData.city}
              </p>
            </div>
            <button onClick={() => navigate("/")}>Back to Home</button>
          </div>
        </div>
      </div>
    );
  }

  const total = getCartTotal ? getCartTotal() : 0;
  const shipping = 50;
  const tax = Math.round(total * 0.18);
  const grandTotal = total + shipping + tax;

  return (
    <div className="payment-page">
      <div className="payment-container">
        <h1>💳 Checkout</h1>

        <div className="payment-content">
          <div className="checkout-form">
            <form onSubmit={handleSubmit}>
              <div className="form-section">
                <h2>
                  <Truck size={24} /> Delivery Information
                </h2>

                <div className="form-group">
                  <label>Full Name *</label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    placeholder="Enter your full name"
                    required
                  />
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Email</label>
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      placeholder="your@email.com"
                    />
                  </div>
                  <div className="form-group">
                    <label>Phone *</label>
                    <input
                      type="tel"
                      name="phone"
                      value={formData.phone}
                      onChange={handleChange}
                      placeholder="10-digit mobile number"
                      required
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label>Address *</label>
                  <textarea
                    name="address"
                    value={formData.address}
                    onChange={handleChange}
                    placeholder="House no, Street, Landmark"
                    rows="3"
                    required
                  />
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>City *</label>
                    <input
                      type="text"
                      name="city"
                      value={formData.city}
                      onChange={handleChange}
                      placeholder="City"
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>State *</label>
                    <input
                      type="text"
                      name="state"
                      value={formData.state}
                      onChange={handleChange}
                      placeholder="State"
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>PIN Code *</label>
                    <input
                      type="text"
                      name="pincode"
                      value={formData.pincode}
                      onChange={handleChange}
                      placeholder="6-digit PIN"
                      maxLength="6"
                      required
                    />
                  </div>
                </div>
              </div>

              <div className="form-section">
                <h2>
                  <CreditCard size={24} /> Payment Method
                </h2>

                <div className="payment-methods">
                  <label className="payment-option">
                    <input
                      type="radio"
                      name="paymentMethod"
                      value="cod"
                      checked={formData.paymentMethod === "cod"}
                      onChange={handleChange}
                    />
                    <div className="option-content">
                      <strong>Cash on Delivery</strong>
                      <span>Pay when you receive</span>
                    </div>
                  </label>

                  <label className="payment-option disabled">
                    <input type="radio" disabled />
                    <div className="option-content">
                      <strong>UPI / Card Payment</strong>
                      <span className="coming-soon">Coming Soon</span>
                    </div>
                  </label>
                </div>
              </div>

              <button type="submit" className="place-order-btn">
                Place Order - ₹{grandTotal}
              </button>
            </form>
          </div>

          <div className="order-summary">
            <h2>Order Summary</h2>

            <div className="summary-items">
              {cart.map((item) => (
                <div key={item.id} className="summary-item">
                  <div className="item-info">
                    <span className="item-name">{item.name}</span>
                    <span className="item-qty">x{item.quantity}</span>
                  </div>
                  <span className="item-price">
                    ₹{item.price * item.quantity}
                  </span>
                </div>
              ))}
            </div>

            <div className="summary-divider"></div>

            <div className="summary-row">
              <span>Subtotal:</span>
              <span>₹{total}</span>
            </div>
            <div className="summary-row">
              <span>Shipping:</span>
              <span>₹{shipping}</span>
            </div>
            <div className="summary-row">
              <span>Tax (GST 18%):</span>
              <span>₹{tax}</span>
            </div>

            <div className="summary-divider"></div>

            <div className="summary-row total">
              <span>Total:</span>
              <span>₹{grandTotal}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Payment;
