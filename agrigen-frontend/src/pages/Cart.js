import React, { useContext } from "react";
import { CartContext } from "../context/CartContext";
import { AuthContext } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { Trash2, Plus, Minus, ShoppingBag } from "lucide-react";
import "./Cart.css";

const Cart = () => {
  const cartContext = useContext(CartContext);
  const authContext = useContext(AuthContext);
  const navigate = useNavigate();

  // Safely destructure with defaults
  const {
    cart = [],
    removeFromCart,
    updateQuantity,
    getCartTotal,
  } = cartContext || {};
  const { user } = authContext || {};

  if (!user) {
    return (
      <div className="cart-page">
        <div className="cart-container">
          <div className="empty-cart">
            <ShoppingBag size={64} />
            <h2>Please Login</h2>
            <p>You need to login to view your cart</p>
            <button onClick={() => navigate("/login")}>Go to Login</button>
          </div>
        </div>
      </div>
    );
  }

  if (cart.length === 0) {
    return (
      <div className="cart-page">
        <div className="cart-container">
          <div className="empty-cart">
            <ShoppingBag size={64} />
            <h2>Your Cart is Empty</h2>
            <p>Start adding seeds and products to your cart!</p>
            <button onClick={() => navigate("/analysis")}>
              Start Analysis
            </button>
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
    <div className="cart-page">
      <div className="cart-container">
        <h1>🛒 Your Shopping Cart</h1>

        <div className="cart-content">
          <div className="cart-items">
            {cart.map((item) => (
              <div key={item.id} className="cart-item">
                <div className="item-image">{item.image || "📦"}</div>
                <div className="item-details">
                  <h3>{item.name}</h3>
                  <p className="item-type">{item.type}</p>
                  <p className="item-description">{item.description}</p>
                </div>
                <div className="item-quantity">
                  <button
                    onClick={() =>
                      updateQuantity &&
                      updateQuantity(item.id, item.quantity - 1)
                    }
                  >
                    <Minus size={16} />
                  </button>
                  <span>{item.quantity}</span>
                  <button
                    onClick={() =>
                      updateQuantity &&
                      updateQuantity(item.id, item.quantity + 1)
                    }
                  >
                    <Plus size={16} />
                  </button>
                </div>
                <div className="item-price">
                  <p className="unit-price">₹{item.price} each</p>
                  <p className="total-price">₹{item.price * item.quantity}</p>
                </div>
                <button
                  className="remove-btn"
                  onClick={() => removeFromCart && removeFromCart(item.id)}
                >
                  <Trash2 size={20} />
                </button>
              </div>
            ))}
          </div>

          <div className="cart-summary">
            <h2>Order Summary</h2>
            <div className="summary-row">
              <span>Subtotal ({cart.length} items):</span>
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
            <button
              className="checkout-btn"
              onClick={() => navigate("/payment")}
            >
              Proceed to Checkout
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Cart;
