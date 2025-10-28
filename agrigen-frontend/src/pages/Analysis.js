import React, { useState, useContext } from "react";
import axios from "axios";
import { useDropzone } from "react-dropzone";
import { useNavigate } from "react-router-dom";
import {
  Upload,
  Loader,
  CheckCircle,
  AlertCircle,
  Cloud,
  Thermometer,
  Droplets,
  Download,
  Plus,
  Minus,
  ShoppingCart,
} from "lucide-react";
import { CartContext } from "../context/CartContext";
import { AuthContext } from "../context/AuthContext";
import { toast } from "react-toastify";
import jsPDF from "jspdf";
import "./Analysis.css";

const API_BASE_URL = "http://localhost:5000";

function Analysis() {
  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [location, setLocation] = useState("Mysuru,IN");
  const [selectedCrop, setSelectedCrop] = useState("tomato");
  const [quantities, setQuantities] = useState({});

  const { addToCart } = useContext(CartContext);
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();

  // Available crops
  const crops = [
    { id: "tomato", name: "Tomato", active: true },
    { id: "rice", name: "Rice", active: false },
    { id: "wheat", name: "Wheat", active: false },
    { id: "maize", name: "Maize", active: false },
  ];

  // Handle file drop
  const onDrop = (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      setImage(file);
      setImagePreview(URL.createObjectURL(file));
      setResults(null);
      setError(null);
      setQuantities({});
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "image/*": [".jpeg", ".jpg", ".png"],
    },
    multiple: false,
  });

  // Analyze image
  const handleAnalyze = async () => {
    if (!image) {
      setError("Please upload an image first!");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", image);
      formData.append("location", location);

      const response = await axios.post(
        `${API_BASE_URL}/api/complete`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setResults(response.data);
      toast.success("Analysis complete!");
    } catch (err) {
      setError(
        err.response?.data?.error ||
          "Failed to analyze image. Please try again."
      );
      console.error("Error:", err);
      toast.error("Analysis failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // Handle quantity change
  const updateQuantity = (itemId, change) => {
    setQuantities((prev) => {
      const newQty = (prev[itemId] || 0) + change;
      if (newQty <= 0) {
        const { [itemId]: removed, ...rest } = prev;
        return rest;
      }
      return { ...prev, [itemId]: newQty };
    });
  };

  // Add all selected items to cart
  const addSelectedToCart = () => {
    if (!user) {
      toast.error("Please login to add items to cart");
      navigate("/login");
      return;
    }

    let itemsAdded = 0;

    // Add breeding recommendations
    if (
      !isSeverelyDiseased() &&
      results.breeding_recommendations &&
      results.breeding_recommendations.length > 0
    ) {
      results.breeding_recommendations.forEach((rec, index) => {
        const itemId = `breeding-${index}`;
        const qty = quantities[itemId] || 0;

        if (qty > 0) {
          const product = {
            id: `${itemId}-${Date.now()}`,
            name: `${rec.hybrid_name} Seeds`,
            type: "Breeding Partner Seeds",
            price: 299,
            quantity: qty,
            description: `${rec.hybrid_name} - Maturity: ${rec.maturity_days} days`,
            image: "🌱",
          };
          addToCart(product);
          itemsAdded += qty;
        }
      });
    }

    // Add replacement recommendations
    if (
      results.replacement_recommendations &&
      results.replacement_recommendations.length > 0
    ) {
      results.replacement_recommendations.forEach((rec, index) => {
        const itemId = `replacement-${index}`;
        const qty = quantities[itemId] || 0;

        if (qty > 0) {
          const product = {
            id: `${itemId}-${Date.now()}`,
            name: `${rec.hybrid_name} Seeds`,
            type: "Hybrid Seeds",
            price: 299,
            quantity: qty,
            description: `${rec.hybrid_name} - Maturity: ${rec.maturity_days} days`,
            image: "🌾",
          };
          addToCart(product);
          itemsAdded += qty;
        }
      });
    }

    if (itemsAdded > 0) {
      toast.success(`${itemsAdded} items added to cart!`);
      navigate("/cart");
    } else {
      toast.warning("Please select at least one item to add to cart");
    }
  };

  // Download PDF Report
  const downloadPDF = () => {
    if (!results) return;

    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.width;

    doc.setFontSize(20);
    doc.setTextColor(102, 126, 234);
    doc.text("AgriGenAI Analysis Report", pageWidth / 2, 20, {
      align: "center",
    });

    doc.setFontSize(10);
    doc.setTextColor(100);
    doc.text(
      `Generated: ${new Date().toLocaleDateString()}`,
      pageWidth / 2,
      28,
      {
        align: "center",
      }
    );

    doc.setDrawColor(102, 126, 234);
    doc.line(20, 32, pageWidth - 20, 32);

    let yPos = 45;

    doc.setFontSize(14);
    doc.setTextColor(0);
    doc.text("Predicted Genotype:", 20, yPos);
    doc.setFontSize(12);
    doc.setTextColor(60);
    doc.text(results.predicted_genotype.genotype_id || "N/A", 20, yPos + 7);
    yPos += 20;

    doc.setFontSize(14);
    doc.setTextColor(0);
    doc.text("Predicted Traits:", 20, yPos);
    yPos += 10;

    doc.setFontSize(11);
    Object.entries(results.predicted_traits).forEach(([trait, value]) => {
      doc.setTextColor(0);
      doc.text(`${trait.replace("_", " ")}:`, 25, yPos);
      doc.setTextColor(60);
      doc.text(value, 80, yPos);
      yPos += 7;
    });

    yPos += 10;

    if (
      !isSeverelyDiseased() &&
      results.breeding_recommendations &&
      results.breeding_recommendations.length > 0
    ) {
      doc.setFontSize(14);
      doc.setTextColor(0);
      doc.text("Breeding Recommendations:", 20, yPos);
      yPos += 10;

      results.breeding_recommendations.slice(0, 5).forEach((rec, index) => {
        doc.setFontSize(11);
        doc.setTextColor(102, 126, 234);
        doc.text(`${index + 1}. ${rec.hybrid_name}`, 25, yPos);
        yPos += 6;
        doc.setFontSize(9);
        doc.setTextColor(60);
        doc.text(
          `Score: ${rec.total_score}/100 | Maturity: ${rec.maturity_days} days`,
          30,
          yPos
        );
        yPos += 8;

        if (yPos > 270) {
          doc.addPage();
          yPos = 20;
        }
      });
    }

    if (
      results.replacement_recommendations &&
      results.replacement_recommendations.length > 0
    ) {
      if (yPos > 250) {
        doc.addPage();
        yPos = 20;
      }

      doc.setFontSize(14);
      doc.setTextColor(0);
      doc.text("Alternative Hybrid Recommendations:", 20, yPos);
      yPos += 10;

      results.replacement_recommendations.slice(0, 5).forEach((rec, index) => {
        doc.setFontSize(11);
        doc.setTextColor(245, 158, 11);
        doc.text(`${index + 1}. ${rec.hybrid_name}`, 25, yPos);
        yPos += 6;
        doc.setFontSize(9);
        doc.setTextColor(60);
        doc.text(
          `Score: ${rec.total_score}/100 | Maturity: ${rec.maturity_days} days`,
          30,
          yPos
        );
        yPos += 8;

        if (yPos > 270) {
          doc.addPage();
          yPos = 20;
        }
      });
    }

    yPos = doc.internal.pageSize.height - 20;
    doc.setFontSize(8);
    doc.setTextColor(150);
    doc.text(
      "Generated by AgriGenAI - Smart Farming, Better Yields",
      pageWidth / 2,
      yPos,
      { align: "center" }
    );

    doc.save("agrigenai-analysis-report.pdf");
    toast.success("PDF report downloaded successfully!");
  };

  // Check if plant is severely diseased
  const isSeverelyDiseased = () => {
    if (!results || !results.predicted_traits) return false;
    const diseaseResistance = results.predicted_traits.disease_resistance;
    return diseaseResistance === "Susceptible" || diseaseResistance === "Low";
  };

  // Calculate total selected items
  const getTotalSelected = () => {
    return Object.values(quantities).reduce((sum, qty) => sum + qty, 0);
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>🌱 AgriGenAI</h1>
        <p>AI-Powered Plant Phenotype Analysis & Hybrid Recommendations</p>
      </header>

      <div className="container">
        <div className="upload-section">
          <div className="crop-selector">
            <label>🌾 Select Crop Type:</label>
            <div className="crop-buttons">
              {crops.map((crop) => (
                <button
                  key={crop.id}
                  className={`crop-btn ${
                    selectedCrop === crop.id ? "active" : ""
                  } ${!crop.active ? "disabled" : ""}`}
                  onClick={() => crop.active && setSelectedCrop(crop.id)}
                  disabled={!crop.active}
                >
                  {crop.name}
                  {!crop.active && (
                    <span className="coming-soon">Coming Soon</span>
                  )}
                </button>
              ))}
            </div>
          </div>

          <div
            {...getRootProps()}
            className={`dropzone ${isDragActive ? "active" : ""}`}
          >
            <input {...getInputProps()} />
            {imagePreview ? (
              <img src={imagePreview} alt="Preview" className="image-preview" />
            ) : (
              <div className="dropzone-content">
                <Upload size={48} />
                <p>Drag & drop an image here, or click to select</p>
                <small>Supports: JPG, JPEG, PNG</small>
              </div>
            )}
          </div>

          <div className="location-input">
            <label>📍 Location (for weather & recommendations):</label>
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g., Bangalore,IN"
            />
          </div>

          <button
            onClick={handleAnalyze}
            disabled={!image || loading}
            className="analyze-button"
          >
            {loading ? (
              <>
                <Loader className="spinner" size={20} />
                Analyzing...
              </>
            ) : (
              <>
                <CheckCircle size={20} />
                Analyze Plant
              </>
            )}
          </button>

          {error && (
            <div className="error-message">
              <AlertCircle size={20} />
              {error}
            </div>
          )}
        </div>

        {results && (
          <div className="results-section">
            <div className="card">
              <h2>🔮 Predicted Traits</h2>
              <div className="traits-grid">
                {Object.entries(results.predicted_traits).map(
                  ([trait, value]) => (
                    <div key={trait} className="trait-item">
                      <span className="trait-label">
                        {trait.replace("_", " ")}:
                      </span>
                      <span className={`trait-value ${value.toLowerCase()}`}>
                        {value}
                      </span>
                    </div>
                  )
                )}
              </div>
            </div>

            <div className="card">
              <h2>🧬 Predicted Genotype</h2>
              <div className="genotype-info">
                <p>
                  <strong>ID:</strong> {results.predicted_genotype.genotype_id}
                </p>
                <p>
                  <strong>Genes:</strong>{" "}
                  {results.predicted_genotype.genes.join(", ")}
                </p>
                <p className="genotype-description">
                  {results.predicted_genotype.description}
                </p>
              </div>
            </div>

            {results.weather && results.weather.success && (
              <div className="card weather-card">
                <h2>🌤️ Current Weather</h2>
                <div className="weather-info">
                  <div className="weather-item">
                    <Cloud size={24} />
                    <span>{results.weather.description}</span>
                  </div>
                  <div className="weather-item">
                    <Thermometer size={24} />
                    <span>{results.weather.temperature}°C</span>
                  </div>
                  <div className="weather-item">
                    <Droplets size={24} />
                    <span>{results.weather.humidity}%</span>
                  </div>
                </div>
              </div>
            )}

            {isSeverelyDiseased() && (
              <div className="card warning-card">
                <h2>⚠️ Important Notice</h2>
                <div className="warning-content">
                  <p className="warning-main">
                    ❌{" "}
                    <strong>
                      This plant cannot be crossed with other plants
                    </strong>{" "}
                    due to low disease resistance.
                  </p>
                  <p className="warning-recommendation">
                    ✅ <strong>Recommendation:</strong> Please purchase healthy
                    hybrid saplings from the Alternative Hybrids section below.
                  </p>
                </div>
              </div>
            )}

            {!isSeverelyDiseased() &&
              results.breeding_recommendations &&
              results.breeding_recommendations.length > 0 && (
                <div className="card recommendations-card">
                  <h2>🧬 Breeding Recommendations</h2>
                  <p className="recommendation-subtitle">
                    Cross YOUR plant (genotype{" "}
                    {results.predicted_genotype.genotype_id}) with these
                    partners:
                  </p>
                  <div className="recommendations-list">
                    {results.breeding_recommendations.map((rec, index) => {
                      const itemId = `breeding-${index}`;
                      const qty = quantities[itemId] || 0;

                      return (
                        <div
                          key={index}
                          className="recommendation-item breeding"
                        >
                          <div className="rec-header">
                            <span className="rec-rank">#{index + 1}</span>
                            <h3>{rec.hybrid_name}</h3>
                            <span className="rec-score">
                              {rec.total_score}/100
                            </span>
                          </div>
                          <div className="rec-details">
                            <p className="breeding-formula">
                              <strong>
                                🌱 Your Plant ({rec.your_genotype})
                              </strong>{" "}
                              ×{" "}
                              <strong>Partner ({rec.partner_genotype})</strong>{" "}
                              = <strong>{rec.hybrid_name}</strong>
                            </p>
                            <p>
                              <strong>Maturity:</strong> {rec.maturity_days}{" "}
                              days
                            </p>
                            <p>
                              <strong>Expected Traits:</strong>
                            </p>
                            <div className="expected-traits">
                              <span>Yield: {rec.expected_traits.yield}</span>
                              <span>
                                Disease Resistance:{" "}
                                {rec.expected_traits.disease_resistance}
                              </span>
                              <span>
                                Stress Tolerance:{" "}
                                {rec.expected_traits.stress_tolerance}
                              </span>
                            </div>
                            <div className="rec-scores">
                              <span>Weather Score: {rec.weather_score}</span>
                            </div>

                            <div className="quantity-selector">
                              <span className="qty-label">
                                Select Quantity:
                              </span>
                              <div className="qty-controls">
                                <button
                                  className="qty-btn"
                                  onClick={() => updateQuantity(itemId, -1)}
                                  disabled={qty === 0}
                                >
                                  <Minus size={16} />
                                </button>
                                <span className="qty-value">{qty}</span>
                                <button
                                  className="qty-btn"
                                  onClick={() => updateQuantity(itemId, 1)}
                                >
                                  <Plus size={16} />
                                </button>
                              </div>
                              <span className="qty-price">₹299 per pack</span>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

            {results.replacement_recommendations &&
              results.replacement_recommendations.length > 0 && (
                <div className="card recommendations-card">
                  <h2>🌾 Alternative Hybrids to Plant</h2>
                  <p className="recommendation-subtitle">
                    {isSeverelyDiseased()
                      ? "Since your plant cannot be crossed, consider planting these superior hybrids instead:"
                      : "Or plant these superior hybrids instead of your current crop:"}
                  </p>
                  <div className="recommendations-list">
                    {results.replacement_recommendations.map((rec, index) => {
                      const itemId = `replacement-${index}`;
                      const qty = quantities[itemId] || 0;

                      return (
                        <div
                          key={index}
                          className="recommendation-item replacement"
                        >
                          <div className="rec-header">
                            <span className="rec-rank">#{index + 1}</span>
                            <h3>{rec.hybrid_name}</h3>
                            <span className="rec-score">
                              {rec.total_score}/100
                            </span>
                          </div>
                          <div className="rec-details">
                            <p>
                              <strong>Parents:</strong>{" "}
                              {rec.parent_genotypes.join(" × ")}
                            </p>
                            <p>
                              <strong>Maturity:</strong> {rec.maturity_days}{" "}
                              days
                            </p>
                            <p>
                              <strong>Expected Traits:</strong>
                            </p>
                            <div className="expected-traits">
                              <span>Yield: {rec.expected_traits.yield}</span>
                              <span>
                                Disease Resistance:{" "}
                                {rec.expected_traits.disease_resistance}
                              </span>
                              <span>
                                Stress Tolerance:{" "}
                                {rec.expected_traits.stress_tolerance}
                              </span>
                            </div>
                            <div className="rec-scores">
                              <span>
                                Trait Match: {rec.compatibility_score}
                              </span>
                              <span>Weather Score: {rec.weather_score}</span>
                            </div>

                            <div className="quantity-selector">
                              <span className="qty-label">
                                Select Quantity:
                              </span>
                              <div className="qty-controls">
                                <button
                                  className="qty-btn"
                                  onClick={() => updateQuantity(itemId, -1)}
                                  disabled={qty === 0}
                                >
                                  <Minus size={16} />
                                </button>
                                <span className="qty-value">{qty}</span>
                                <button
                                  className="qty-btn"
                                  onClick={() => updateQuantity(itemId, 1)}
                                >
                                  <Plus size={16} />
                                </button>
                              </div>
                              <span className="qty-price">₹299 per pack</span>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

            <div className="card farmer-summary">
              <h2>📊 Summary for Farmers</h2>
              <div className="summary-content">
                <p>
                  <strong>Your Plant:</strong>{" "}
                  {results.predicted_genotype.genotype_id}
                </p>
                <p>
                  <strong>Health Status:</strong>{" "}
                  {isSeverelyDiseased() ? (
                    <span className="status-bad">
                      ⚠️ Low disease resistance - Cannot be used for breeding
                    </span>
                  ) : (
                    <span className="status-good">
                      ✅ Suitable for breeding
                    </span>
                  )}
                </p>
                <p>
                  <strong>Recommendation:</strong>
                </p>
                {isSeverelyDiseased() ? (
                  <ul className="summary-list">
                    <li>
                      ❌ <strong>Do NOT cross</strong> this plant with others
                      due to poor disease resistance
                    </li>
                    <li>
                      ✅ <strong>Purchase healthy hybrid saplings</strong> from
                      the Alternative Hybrids section above
                    </li>
                  </ul>
                ) : (
                  <ul className="summary-list">
                    <li>
                      🌱 <strong>Option 1 (Breeding):</strong> Cross your plant
                      with the recommended partners above for better yields
                    </li>
                    <li>
                      🌾 <strong>Option 2 (Replacement):</strong> Plant the
                      alternative hybrids for superior traits
                    </li>
                  </ul>
                )}
                <p className="summary-note">
                  <strong>💡 Note:</strong> All recommendations are based on
                  your plant's genetic profile and current weather conditions in{" "}
                  {location}.
                </p>
              </div>
            </div>

            {getTotalSelected() > 0 && (
              <div className="card action-card">
                <div className="action-content">
                  <div className="cart-summary-info">
                    <ShoppingCart size={24} />
                    <span>{getTotalSelected()} items selected</span>
                  </div>
                  <button className="view-cart-btn" onClick={addSelectedToCart}>
                    <ShoppingCart size={20} />
                    View Cart & Checkout
                  </button>
                </div>
              </div>
            )}

            <div className="card download-card">
              <h2>📥 Download Analysis Report</h2>
              <p className="download-subtitle">
                Save your complete analysis report for future reference
              </p>
              <button className="download-pdf-btn" onClick={downloadPDF}>
                <Download size={18} />
                Download PDF Report
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Analysis;
