import React, { useState } from "react";
import { Search, Droplet, Sun, Sprout, ShoppingCart, X } from "lucide-react";
import { useContext } from "react";
import { CartContext } from "../context/CartContext";
import { AuthContext } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import "./CropDatabase.css";

// Sample crop data (you can move this to a JSON file later)
const cropsData = [
  {
    id: 1,
    name: "Tomato - Roma",
    scientificName: "Solanum lycopersicum",
    category: "Vegetable",
    water: "Medium",
    soil: "Loamy",
    ph: "6.0-6.8",
    sunlight: "Full Sun",
    description:
      "Roma tomatoes are determinate, which means the fruit ripens at one time, instead of continually throughout the season.",
    price: 299,
    image: "🍅",
    regions: ["Karnataka", "Maharashtra", "Tamil Nadu"],
    hybrids: ["Roma VF", "San Marzano", "Plum Perfect"],
    growingTime: "75-85 days",
  },
  {
    id: 2,
    name: "Tomato - Cherry",
    scientificName: "Solanum lycopersicum var. cerasiforme",
    category: "Vegetable",
    water: "Medium",
    soil: "Loamy",
    ph: "6.0-6.8",
    sunlight: "Full Sun",
    description:
      "Small, sweet tomatoes perfect for snacking. Indeterminate variety that produces fruit throughout the season.",
    price: 349,
    image: "🍒",
    regions: ["All India"],
    hybrids: ["Sweet 100", "Sun Gold", "Black Cherry"],
    growingTime: "60-70 days",
  },
  {
    id: 3,
    name: "Rice - Basmati",
    scientificName: "Oryza sativa",
    category: "Grain",
    water: "High",
    soil: "Clay Loam",
    ph: "5.5-6.5",
    sunlight: "Full Sun",
    description:
      "Premium long-grain aromatic rice. Requires flooded conditions for optimal growth.",
    price: 499,
    image: "🌾",
    regions: ["Punjab", "Haryana", "UP"],
    hybrids: ["Pusa Basmati 1121", "Pusa Basmati 1509", "CSR 30"],
    growingTime: "120-150 days",
  },
  {
    id: 4,
    name: "Wheat - Durum",
    scientificName: "Triticum durum",
    category: "Grain",
    water: "Low-Medium",
    soil: "Well-drained Loam",
    ph: "6.0-7.0",
    sunlight: "Full Sun",
    description:
      "Hard wheat used primarily for pasta and bread making. Drought-resistant variety.",
    price: 399,
    image: "🌾",
    regions: ["MP", "Rajasthan", "Gujarat"],
    hybrids: ["HI 8627", "PDW 291", "GW 322"],
    growingTime: "110-130 days",
  },
  {
    id: 5,
    name: "Maize - Sweet Corn",
    scientificName: "Zea mays",
    category: "Grain",
    water: "Medium",
    soil: "Loamy",
    ph: "5.8-7.0",
    sunlight: "Full Sun",
    description:
      "Sweet corn variety with high sugar content. Perfect for fresh consumption.",
    price: 279,
    image: "🌽",
    regions: ["Karnataka", "AP", "Bihar"],
    hybrids: ["Sugar 75", "Madhuri", "Sweet Wonder"],
    growingTime: "65-90 days",
  },
  {
    id: 6,
    name: "Chili - Green",
    scientificName: "Capsicum annuum",
    category: "Vegetable",
    water: "Medium",
    soil: "Sandy Loam",
    ph: "6.0-6.5",
    sunlight: "Full Sun",
    description:
      "Hot chili pepper variety. High yielding with good disease resistance.",
    price: 249,
    image: "🌶️",
    regions: ["Andhra Pradesh", "Karnataka", "Telangana"],
    hybrids: ["Pusa Jwala", "Byadagi", "Guntur Sannam"],
    growingTime: "60-80 days",
  },
];

const CropDatabase = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedWater, setSelectedWater] = useState("all");
  const [selectedSoil, setSelectedSoil] = useState("all");
  const [selectedCrop, setSelectedCrop] = useState(null);

  const { addToCart } = useContext(CartContext);
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();

  // Filter crops
  const filteredCrops = cropsData.filter((crop) => {
    const matchesSearch =
      crop.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      crop.scientificName.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesWater =
      selectedWater === "all" || crop.water === selectedWater;
    const matchesSoil = selectedSoil === "all" || crop.soil === selectedSoil;

    return matchesSearch && matchesWater && matchesSoil;
  });

  const handleAddToCart = (crop) => {
    if (!user) {
      toast.error("Please login to add items to cart");
      navigate("/login");
      return;
    }

    const product = {
      id: `crop-${crop.id}`,
      name: `${crop.name} Seeds`,
      type: "Seeds",
      price: crop.price,
      quantity: 1,
      description: crop.description,
      image: crop.image,
    };

    addToCart(product);
    toast.success(`${crop.name} seeds added to cart!`);
  };

  return (
    <div className="crop-database-page">
      <div className="crop-database-container">
        <div className="database-header">
          <h1>🌱 Crop Database</h1>
          <p>
            Explore our comprehensive collection of crops and their growing
            requirements
          </p>
        </div>

        {/* Search and Filters */}
        <div className="filters-section">
          <div className="search-box">
            <Search size={20} />
            <input
              type="text"
              placeholder="Search crops..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <div className="filter-group">
            <label>Water Need:</label>
            <select
              value={selectedWater}
              onChange={(e) => setSelectedWater(e.target.value)}
            >
              <option value="all">All</option>
              <option value="Low">Low</option>
              <option value="Low-Medium">Low-Medium</option>
              <option value="Medium">Medium</option>
              <option value="High">High</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Soil Type:</label>
            <select
              value={selectedSoil}
              onChange={(e) => setSelectedSoil(e.target.value)}
            >
              <option value="all">All</option>
              <option value="Loamy">Loamy</option>
              <option value="Sandy Loam">Sandy Loam</option>
              <option value="Clay Loam">Clay Loam</option>
              <option value="Well-drained Loam">Well-drained Loam</option>
            </select>
          </div>
        </div>

        {/* Crops Grid */}
        <div className="crops-grid">
          {filteredCrops.map((crop) => (
            <div key={crop.id} className="crop-card">
              <div className="crop-image">{crop.image}</div>
              <h3>{crop.name}</h3>
              <p className="scientific-name">{crop.scientificName}</p>

              <div className="crop-requirements">
                <div className="requirement">
                  <Droplet size={16} />
                  <span>{crop.water}</span>
                </div>
                <div className="requirement">
                  <Sun size={16} />
                  <span>{crop.sunlight}</span>
                </div>
                <div className="requirement">
                  <Sprout size={16} />
                  <span>pH {crop.ph}</span>
                </div>
              </div>

              <div className="crop-card-footer">
                <span className="price">₹{crop.price}/pack</span>
                <button
                  className="view-details-btn"
                  onClick={() => setSelectedCrop(crop)}
                >
                  View Details
                </button>
              </div>
            </div>
          ))}
        </div>

        {filteredCrops.length === 0 && (
          <div className="no-results">
            <p>No crops found matching your criteria</p>
          </div>
        )}
      </div>

      {/* Modal */}
      {selectedCrop && (
        <div className="modal-overlay" onClick={() => setSelectedCrop(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button
              className="close-modal"
              onClick={() => setSelectedCrop(null)}
            >
              <X size={24} />
            </button>

            <div className="modal-header">
              <div className="modal-image">{selectedCrop.image}</div>
              <div className="modal-title">
                <h2>{selectedCrop.name}</h2>
                <p className="scientific-name">{selectedCrop.scientificName}</p>
                <span className="category-badge">{selectedCrop.category}</span>
              </div>
            </div>

            <div className="modal-body">
              <div className="info-section">
                <h3>Description</h3>
                <p>{selectedCrop.description}</p>
              </div>

              <div className="info-grid">
                <div className="info-item">
                  <h4>
                    <Droplet size={18} /> Water Requirement
                  </h4>
                  <p>{selectedCrop.water}</p>
                </div>
                <div className="info-item">
                  <h4>
                    <Sun size={18} /> Sunlight
                  </h4>
                  <p>{selectedCrop.sunlight}</p>
                </div>
                <div className="info-item">
                  <h4>
                    <Sprout size={18} /> Soil Type
                  </h4>
                  <p>{selectedCrop.soil}</p>
                </div>
                <div className="info-item">
                  <h4>📊 pH Range</h4>
                  <p>{selectedCrop.ph}</p>
                </div>
                <div className="info-item">
                  <h4>⏱️ Growing Time</h4>
                  <p>{selectedCrop.growingTime}</p>
                </div>
                <div className="info-item">
                  <h4>📍 Best Regions</h4>
                  <p>{selectedCrop.regions.join(", ")}</p>
                </div>
              </div>

              <div className="info-section">
                <h3>Available Hybrids</h3>
                <div className="hybrids-list">
                  {selectedCrop.hybrids.map((hybrid, index) => (
                    <span key={index} className="hybrid-badge">
                      {hybrid}
                    </span>
                  ))}
                </div>
              </div>

              <div className="modal-footer">
                <div className="price-section">
                  <span className="price-label">Price:</span>
                  <span className="price-value">
                    ₹{selectedCrop.price}/pack
                  </span>
                </div>
                <button
                  className="add-to-cart-btn"
                  onClick={() => {
                    handleAddToCart(selectedCrop);
                    setSelectedCrop(null);
                  }}
                >
                  <ShoppingCart size={20} />
                  Add to Cart
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CropDatabase;
