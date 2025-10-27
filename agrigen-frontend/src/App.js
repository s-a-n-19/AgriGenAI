import React, { useState } from "react";
import axios from "axios";
import { useDropzone } from "react-dropzone";
import {
  Upload,
  Loader,
  CheckCircle,
  AlertCircle,
  Cloud,
  Thermometer,
  Droplets,
} from "lucide-react";
import "./App.css";

const API_BASE_URL = "http://localhost:5000";

function App() {
  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [location, setLocation] = useState("Mysuru,IN");

  // Handle file drop
  const onDrop = (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      setImage(file);
      setImagePreview(URL.createObjectURL(file));
      setResults(null);
      setError(null);
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
    } catch (err) {
      setError(
        err.response?.data?.error ||
          "Failed to analyze image. Please try again."
      );
      console.error("Error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      {/* Header */}
      <header className="app-header">
        <h1>🌱 AgriGenAI</h1>
        <p>AI-Powered Plant Phenotype Analysis & Hybrid Recommendations</p>
      </header>

      <div className="container">
        {/* Upload Section */}
        <div className="upload-section">
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

          {/* Location Input */}
          <div className="location-input">
            <label>📍 Location (for weather & recommendations):</label>
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g., Bangalore,IN"
            />
          </div>

          {/* Analyze Button */}
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

          {/* Error Message */}
          {error && (
            <div className="error-message">
              <AlertCircle size={20} />
              {error}
            </div>
          )}
        </div>

        {/* Results Section */}
        {results && (
          <div className="results-section">
            {/* Predicted Traits */}
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

            {/* Predicted Genotype */}
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

            {/* Weather Information */}
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

            {/* BREEDING RECOMMENDATIONS */}
            {results.breeding_recommendations &&
              results.breeding_recommendations.length > 0 && (
                <div className="card recommendations-card">
                  <h2>🧬 Breeding Recommendations</h2>
                  <p className="recommendation-subtitle">
                    Cross YOUR plant (genotype{" "}
                    {results.predicted_genotype.genotype_id}) with these
                    partners:
                  </p>
                  <div className="recommendations-list">
                    {results.breeding_recommendations.map((rec, index) => (
                      <div key={index} className="recommendation-item breeding">
                        <div className="rec-header">
                          <span className="rec-rank">#{index + 1}</span>
                          <h3>{rec.hybrid_name}</h3>
                          <span className="rec-score">
                            {rec.total_score}/100
                          </span>
                        </div>
                        <div className="rec-details">
                          <p className="breeding-formula">
                            <strong>🌱 Your Plant ({rec.your_genotype})</strong>{" "}
                            × <strong>Partner ({rec.partner_genotype})</strong>{" "}
                            = <strong>{rec.hybrid_name}</strong>
                          </p>
                          <p>
                            <strong>Maturity:</strong> {rec.maturity_days} days
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
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

            {/* REPLACEMENT RECOMMENDATIONS */}
            {results.replacement_recommendations &&
              results.replacement_recommendations.length > 0 && (
                <div className="card recommendations-card">
                  <h2>🌾 Alternative Hybrids to Plant</h2>
                  <p className="recommendation-subtitle">
                    Or plant these superior hybrids instead of your current
                    crop:
                  </p>
                  <div className="recommendations-list">
                    {results.replacement_recommendations.map((rec, index) => (
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
                            <strong>Maturity:</strong> {rec.maturity_days} days
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
                            <span>Trait Match: {rec.compatibility_score}</span>
                            <span>Weather Score: {rec.weather_score}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
