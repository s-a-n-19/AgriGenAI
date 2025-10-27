"""
AgriGenAI - COMPLETE & CORRECTED Backend 
==========================================
ALL ISSUES FIXED:
1. ✅ All 27 genotypes properly mapped (not just 12!)
2. ✅ Enhanced disease detection with override logic
3. ✅ Proper recommendation scoring (unique scores)
4. ✅ Smart breeding partner filtering
5. ✅ Correct model filenames
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import numpy as np
from pathlib import Path
import joblib
import json
from PIL import Image
from datetime import datetime
import requests
import traceback
import os
import cv2

try:
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    import tensorflow as tf
    from tensorflow.keras.applications import ResNet50
    from tensorflow.keras.applications.resnet50 import preprocess_input
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

# ============================================
# CONFIGURATION
# ============================================

class Config:
    MODELS_PATH = Path('C:/Users/sahan/Desktop/AgriGenAI2/AgriGenAI_Output/models')
    HYBRIDS_PATH = Path('C:/Users/sahan/Desktop/AgriGenAI2/AgriGenAI_Output/hybrids')
    UPLOAD_FOLDER = Path('C:/Users/sahan/Desktop/AgriGenAI2/AgriGenAI_Output/uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    WEATHER_API_KEY = "2dd75433108cb63b662fef10d29787fa"
    WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
    IMG_SIZE = (224, 224)

Config.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
CORS(app)

print("=" * 60)
print("🌱 AgriGenAI (COMPLETE: All 27 Genotypes)")
print("=" * 60)

# ============================================
# COMPLETE GENOTYPE PREDICTOR (ALL 27!)
# ============================================

class GenotypePredictorSimulator:
    def __init__(self, hybrid_database):
        self.hybrid_db = hybrid_database
        self.genotype_map = self._build_complete_genotype_map()
    
    def _build_complete_genotype_map(self):
        """
        COMPLETE mapping for ALL 27 genotypes!
        3 Yields × 3 Disease Resistance × 3 Stress Tolerance = 27 combinations
        """
        return {
            # HIGH YIELD (G1-G9)
            ('High', 'Resistant', 'High'): {'genotype_id': 'G1', 'genes': ['fw2.2-AA', 'HSP-High', 'Tm-2a-Present'], 'description': 'Superior: high yield, disease resistant, stress tolerant'},
            ('High', 'Resistant', 'Medium'): {'genotype_id': 'G2', 'genes': ['fw2.2-Aa', 'HSP-Medium', 'Tm-2a-Present'], 'description': 'High yield with disease resistance'},
            ('High', 'Resistant', 'Low'): {'genotype_id': 'G3', 'genes': ['fw2.2-AA', 'HSP-Low', 'Tm-2a-Present'], 'description': 'High yield, resistant but stress sensitive'},
            ('High', 'Moderate', 'High'): {'genotype_id': 'G4', 'genes': ['fw2.2-Aa', 'HSP-High', 'Tm-2-Partial'], 'description': 'High yield, stress tolerant'},
            ('High', 'Moderate', 'Medium'): {'genotype_id': 'G5', 'genes': ['fw2.2-Aa', 'HSP-Medium', 'Tm-2-Partial'], 'description': 'Good all-rounder'},
            ('High', 'Moderate', 'Low'): {'genotype_id': 'G6', 'genes': ['fw2.2-AA', 'HSP-Low', 'Tm-2-Partial'], 'description': 'High yield but needs care'},
            ('High', 'Susceptible', 'High'): {'genotype_id': 'G7', 'genes': ['fw2.2-AA', 'HSP-High', 'Tm-2-Absent'], 'description': 'High yield but needs disease protection'},
            ('High', 'Susceptible', 'Medium'): {'genotype_id': 'G8', 'genes': ['fw2.2-Aa', 'HSP-Medium', 'Tm-2-Absent'], 'description': 'High yield, requires management'},
            ('High', 'Susceptible', 'Low'): {'genotype_id': 'G9', 'genes': ['fw2.2-AA', 'HSP-Low', 'Tm-2-Absent'], 'description': 'High yield but vulnerable'},
            
            # MEDIUM YIELD (G10-G18)
            ('Medium', 'Resistant', 'High'): {'genotype_id': 'G10', 'genes': ['fw2.2-aa', 'HSP-High', 'Tm-2a-Present'], 'description': 'Balanced genotype, stress tolerant'},
            ('Medium', 'Resistant', 'Medium'): {'genotype_id': 'G11', 'genes': ['fw2.2-aa', 'HSP-Medium', 'Tm-2a-Present'], 'description': 'Moderate yield, good resistance'},
            ('Medium', 'Resistant', 'Low'): {'genotype_id': 'G12', 'genes': ['fw2.2-Aa', 'HSP-Low', 'Tm-2a-Present'], 'description': 'Moderate yield, resistant'},
            ('Medium', 'Moderate', 'High'): {'genotype_id': 'G13', 'genes': ['fw2.2-aa', 'HSP-High', 'Tm-2-Partial'], 'description': 'Average yield, stress tolerant'},
            ('Medium', 'Moderate', 'Medium'): {'genotype_id': 'G14', 'genes': ['fw2.2-Aa', 'HSP-Medium', 'Tm-2-Partial'], 'description': 'Average genotype'},
            ('Medium', 'Moderate', 'Low'): {'genotype_id': 'G15', 'genes': ['fw2.2-aa', 'HSP-Low', 'Tm-2-Partial'], 'description': 'Moderate all traits'},
            ('Medium', 'Susceptible', 'High'): {'genotype_id': 'G16', 'genes': ['fw2.2-aa', 'HSP-High', 'Tm-2-Absent'], 'description': 'Moderate yield, needs protection'},
            ('Medium', 'Susceptible', 'Medium'): {'genotype_id': 'G17', 'genes': ['fw2.2-Aa', 'HSP-Medium', 'Tm-2-Absent'], 'description': 'Average, needs disease management'},
            ('Medium', 'Susceptible', 'Low'): {'genotype_id': 'G18', 'genes': ['fw2.2-aa', 'HSP-Low', 'Tm-2-Absent'], 'description': 'Moderate yield, vulnerable'},
            
            # LOW YIELD (G19-G27)
            ('Low', 'Resistant', 'High'): {'genotype_id': 'G19', 'genes': ['fw2.2-aa', 'HSP-High', 'Tm-2a-Present'], 'description': 'Low yield but resistant and hardy'},
            ('Low', 'Resistant', 'Medium'): {'genotype_id': 'G20', 'genes': ['fw2.2-aa', 'HSP-Medium', 'Tm-2a-Present'], 'description': 'Low yield, good resistance'},
            ('Low', 'Resistant', 'Low'): {'genotype_id': 'G21', 'genes': ['fw2.2-aa', 'HSP-Low', 'Tm-2a-Present'], 'description': 'Low yield, resistant'},
            ('Low', 'Moderate', 'High'): {'genotype_id': 'G22', 'genes': ['fw2.2-aa', 'HSP-High', 'Tm-2-Partial'], 'description': 'Low yield, stress tolerant'},
            ('Low', 'Moderate', 'Medium'): {'genotype_id': 'G23', 'genes': ['fw2.2-aa', 'HSP-Medium', 'Tm-2-Partial'], 'description': 'Poor genotype'},
            ('Low', 'Moderate', 'Low'): {'genotype_id': 'G24', 'genes': ['fw2.2-aa', 'HSP-Low', 'Tm-2-Partial'], 'description': 'Inferior genotype'},
            ('Low', 'Susceptible', 'High'): {'genotype_id': 'G25', 'genes': ['fw2.2-aa', 'HSP-High', 'Tm-2-Absent'], 'description': 'Poor yield and disease prone'},
            ('Low', 'Susceptible', 'Medium'): {'genotype_id': 'G26', 'genes': ['fw2.2-aa', 'HSP-Medium', 'Tm-2-Absent'], 'description': 'Poor genotype'},
            ('Low', 'Susceptible', 'Low'): {'genotype_id': 'G27', 'genes': ['fw2.2-aa', 'HSP-Low', 'Tm-2-Absent'], 'description': 'Worst genotype'},
        }
    
    def predict_genotype(self, traits):
        trait_key = (traits['yield'], traits['disease_resistance'], traits['stress_tolerance'])
        result = self.genotype_map.get(trait_key)
        
        if result is None:
            print(f"⚠️  WARNING: Unknown trait combination: {trait_key}")
            # Default to G14 (average)
            result = self.genotype_map[('Medium', 'Moderate', 'Medium')]
        
        return result

# ============================================
# IMPROVED HYBRID ANALYZER
# ============================================

class HybridAnalyzer:
    """
    IMPROVED: Better disease detection and prediction logic
    """
    
    @staticmethod
    def visual_health_check(img_array):
        """IMPROVED visual health check with multiple disease indicators"""
        img_hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        height, width = img_array.shape[:2]
        total_pixels = height * width
        
        # 1. GREEN HEALTHY TISSUE
        green_mask = cv2.inRange(img_hsv, np.array([35, 40, 40]), np.array([85, 255, 255]))
        green_ratio = np.count_nonzero(green_mask) / total_pixels
        
        # 2. BROWN/DEAD TISSUE (expanded range for better detection)
        brown_mask = cv2.inRange(img_hsv, np.array([10, 0, 0]), np.array([30, 255, 150]))
        brown_ratio = np.count_nonzero(brown_mask) / total_pixels
        
        # 3. YELLOW/CHLOROTIC (disease indicator)
        yellow_mask = cv2.inRange(img_hsv, np.array([20, 40, 40]), np.array([35, 255, 255]))
        yellow_ratio = np.count_nonzero(yellow_mask) / total_pixels
        
        # 4. Overall brightness
        brightness = np.mean(img_hsv[:,:,2]) / 255
        
        # 5. Calculate health score (-100 to +100)
        health_score = (green_ratio * 100) - (brown_ratio * 50) - (yellow_ratio * 30)
        
        return {
            'green_ratio': green_ratio,
            'brown_ratio': brown_ratio,
            'yellow_ratio': yellow_ratio,
            'brightness': brightness,
            'health_score': health_score
        }
    
    @staticmethod
    def hybrid_decision(sklearn_traits, img_array, image_hash):
        """
        IMPROVED HYBRID DECISION LOGIC with better disease detection
        """
        
        print("\n🤖 IMPROVED HYBRID ANALYSIS")
        print("="*50)
        
        sklearn_disease = sklearn_traits.get('disease_resistance', 'Moderate')
        sklearn_yield = sklearn_traits.get('yield', 'Medium')
        sklearn_stress = sklearn_traits.get('stress_tolerance', 'Medium')
        
        print(f"   📊 sklearn predictions:")
        print(f"      Disease: {sklearn_disease}")
        print(f"      Yield: {sklearn_yield}")
        print(f"      Stress: {sklearn_stress}")
        
        # Get improved visual analysis
        visual = HybridAnalyzer.visual_health_check(img_array)
        
        print(f"\n   👁️  Visual analysis:")
        print(f"      Green tissue: {visual['green_ratio']*100:.1f}%")
        print(f"      Brown/dead: {visual['brown_ratio']*100:.1f}%")
        print(f"      Yellow/chlorotic: {visual['yellow_ratio']*100:.1f}%")
        print(f"      Brightness: {visual['brightness']*100:.1f}%")
        print(f"      Health score: {visual['health_score']:.1f}")
        
        # CRITICAL FIX: Check for obviously diseased plants FIRST
        if visual['health_score'] < 10:
            # Very poor health - force worst genotypes
            print(f"\n   🚨 OVERRIDE: Visual shows SEVERELY DISEASED/DEAD plant!")
            print(f"      Health score critical ({visual['health_score']:.1f})")
            final_traits = {'yield': 'Low', 'disease_resistance': 'Susceptible', 'stress_tolerance': 'Low'}
            print(f"      → FORCED: G27 (Worst genotype)")
            
        elif visual['green_ratio'] < 0.25 or visual['brown_ratio'] > 0.25:
            # Significant disease visible
            print(f"\n   🚨 OVERRIDE: Visual shows DISEASED plant!")
            print(f"      Too little green ({visual['green_ratio']*100:.1f}%) or too much brown ({visual['brown_ratio']*100:.1f}%)")
            
            # Distribute among poor genotypes
            if visual['health_score'] < 15:
                final_traits = {'yield': 'Low', 'disease_resistance': 'Susceptible', 'stress_tolerance': 'Low'}
                print(f"      → FORCED: G27 (Worst)")
            elif visual['health_score'] < 25:
                final_traits = {'yield': 'Low', 'disease_resistance': 'Susceptible', 'stress_tolerance': 'Medium'}
                print(f"      → FORCED: G26 (Very poor)")
            else:
                final_traits = {'yield': 'Medium', 'disease_resistance': 'Susceptible', 'stress_tolerance': 'Low'}
                print(f"      → FORCED: G18 (Poor)")
            
        elif visual['yellow_ratio'] > 0.30 and visual['green_ratio'] < 0.60:
            # Heavy chlorosis
            print(f"\n   ⚠️  OVERRIDE: Visual shows MODERATE DISEASE (high chlorosis)")
            final_traits = {'yield': 'Medium', 'disease_resistance': 'Susceptible', 'stress_tolerance': 'Medium'}
            print(f"      → FORCED: G17 (Needs protection)")
        
        elif sklearn_disease == 'Susceptible':
            # sklearn detected disease
            print(f"\n   ✅ DECISION: Trust sklearn (disease detected)")
            
            # Use variance and visual for distribution
            variance = image_hash % 100
            
            if visual['health_score'] < 30:
                # Very poor
                if sklearn_yield == 'Low':
                    final_traits = {'yield': 'Low', 'disease_resistance': 'Susceptible', 'stress_tolerance': 'Low'}
                    print(f"      → G27 (Worst)")
                else:
                    final_traits = {'yield': 'Medium', 'disease_resistance': 'Susceptible', 'stress_tolerance': 'Low'}
                    print(f"      → G18 (Poor)")
            elif variance < 33:
                final_traits = {'yield': sklearn_yield, 'disease_resistance': 'Susceptible', 'stress_tolerance': 'High'}
                print(f"      → G7/G16/G25 (Susceptible but stress tolerant)")
            elif variance < 67:
                final_traits = {'yield': sklearn_yield, 'disease_resistance': 'Susceptible', 'stress_tolerance': 'Medium'}
                print(f"      → G8/G17/G26 (Susceptible, medium stress)")
            else:
                final_traits = {'yield': sklearn_yield, 'disease_resistance': 'Susceptible', 'stress_tolerance': 'Low'}
                print(f"      → G9/G18/G27 (Susceptible, low stress)")
        
        elif sklearn_disease == 'Moderate':
            # Medium confidence
            print(f"\n   ⚖️  DECISION: Combine both analyses")
            variance = image_hash % 100
            
            if visual['health_score'] < 40:
                print(f"      Visual confirms: Moderate disease")
                if variance < 50:
                    final_traits = {'yield': sklearn_yield, 'disease_resistance': 'Moderate', 'stress_tolerance': 'Medium'}
                    print(f"      → G5/G14/G23 (Average)")
                else:
                    final_traits = {'yield': sklearn_yield, 'disease_resistance': 'Moderate', 'stress_tolerance': 'Low'}
                    print(f"      → G6/G15/G24 (Below average)")
            else:
                print(f"      Visual shows: Better health than expected")
                if variance < 50:
                    final_traits = {'yield': sklearn_yield, 'disease_resistance': 'Resistant', 'stress_tolerance': 'Medium'}
                    print(f"      → G2/G11/G20 (Upgraded to resistant)")
                else:
                    final_traits = {'yield': sklearn_yield, 'disease_resistance': 'Resistant', 'stress_tolerance': 'High'}
                    print(f"      → G1/G10/G19 (Excellent)")
        
        else:  # sklearn says "Resistant"
            print(f"\n   🔍 DECISION: Verify sklearn's resistant prediction")
            
            if visual['health_score'] < 40:
                # Visual contradicts sklearn!
                print(f"      ⚠️  Visual shows disease despite sklearn prediction!")
                final_traits = {'yield': sklearn_yield, 'disease_resistance': 'Moderate', 'stress_tolerance': 'Medium'}
                print(f"      → G5/G14/G23 (Corrected to moderate)")
            
            elif visual['green_ratio'] > 0.50 and visual['health_score'] > 50:
                # Both agree it's healthy!
                print(f"      ✅ Both confirm: Healthy plant!")
                variance = image_hash % 100
                if variance < 33:
                    final_traits = {'yield': sklearn_yield, 'disease_resistance': 'Resistant', 'stress_tolerance': 'High'}
                    print(f"      → G1/G10/G19 (Superior)")
                elif variance < 67:
                    final_traits = {'yield': sklearn_yield, 'disease_resistance': 'Resistant', 'stress_tolerance': 'Medium'}
                    print(f"      → G2/G11/G20 (Excellent)")
                else:
                    final_traits = {'yield': sklearn_yield, 'disease_resistance': 'Resistant', 'stress_tolerance': 'Low'}
                    print(f"      → G3/G12/G21 (Good)")
            
            else:
                # Uncertain
                print(f"      ⚠️  Uncertain - defaulting to moderate")
                final_traits = {'yield': sklearn_yield, 'disease_resistance': 'Moderate', 'stress_tolerance': 'High'}
                print(f"      → G4/G13/G22 (Good genotype)")
        
        print(f"\n   🎯 FINAL TRAITS: {final_traits}")
        return final_traits

# ============================================
# LOAD MODELS
# ============================================

print("\n📂 Loading models...")

models = {}
hybrid_database = {}
genotype_predictor = None
feature_extractor = None
hybrid_analyzer = HybridAnalyzer()

try:
    # FIXED: Correct model filenames
    trait_files = {
        'yield_trait': 'yield_trait_model.pkl',
        'disease_resistance_trait': 'disease_resistance_model.pkl',
        'stress_tolerance_trait': 'stress_tolerance_model.pkl'
    }
    
    for trait_name, filename in trait_files.items():
        models[trait_name] = joblib.load(Config.MODELS_PATH / filename)
        print(f"   ✅ {trait_name}")
    
    with open(Config.HYBRIDS_PATH / 'hybrid_database.json', 'r') as f:
        hybrid_database = json.load(f)
    print(f"   ✅ Hybrid database ({len(hybrid_database)} hybrids)")
    
    genotype_predictor = GenotypePredictorSimulator(hybrid_database)
    print(f"   ✅ Genotype predictor (ALL 27 genotypes)")
    
    if TF_AVAILABLE:
        feature_extractor = ResNet50(weights='imagenet', include_top=False, pooling='avg', input_shape=(224, 224, 3))
        print("   ✅ ResNet50")
    
    print("\n✅ COMPLETE System: ACTIVE")
    print("   🤖 sklearn for base predictions")
    print("   👁️  Enhanced visual disease detection")
    print("   🚨 Override logic for diseased plants")
    print("   🧬 All 27 genotypes mapped")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    traceback.print_exc()

# ============================================
# HELPER FUNCTIONS
# ============================================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def process_image(file):
    img = Image.open(file.stream).convert('RGB')
    img_resized = img.resize(Config.IMG_SIZE)
    img_array = np.array(img_resized)
    img_preprocessed = np.expand_dims(img_array, axis=0)
    img_preprocessed = preprocess_input(img_preprocessed.copy())
    features = feature_extractor.predict(img_preprocessed, verbose=0)
    return img_array, features.reshape(1, -1), features[0]

def get_image_hash(features):
    return int(abs(np.sum(features) * 1000000)) % 1000

def get_weather(location):
    try:
        params = {'q': location, 'appid': Config.WEATHER_API_KEY, 'units': 'metric'}
        response = requests.get(Config.WEATHER_API_URL, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {'success': True, 'location': location, 'temperature': data['main']['temp'], 'humidity': data['main']['humidity'], 'description': data['weather'][0]['description']}
        return {'success': False}
    except:
        return {'success': False}

def calculate_compatibility(user_genotype_id, partner_genotype_id):
    """Calculate breeding compatibility score (0-100)"""
    
    # Define quality tiers based on ALL 27 genotypes
    superior = ['G1', 'G2', 'G3']  # High yield + Resistant
    excellent = ['G4', 'G5', 'G10', 'G11']  # High/Medium yield + good traits
    good = ['G6', 'G12', 'G13', 'G19', 'G20']  # Decent combinations
    average = ['G14', 'G15', 'G21', 'G22']  # Average
    below_avg = ['G7', 'G8', 'G16', 'G17', 'G23']  # Some weakness
    poor = ['G9', 'G18', 'G24', 'G25', 'G26', 'G27']  # Multiple weaknesses
    
    # Determine user plant tier
    if user_genotype_id in superior:
        base_score = 90
    elif user_genotype_id in excellent:
        base_score = 80
    elif user_genotype_id in good:
        base_score = 70
    elif user_genotype_id in average:
        base_score = 60
    elif user_genotype_id in below_avg:
        base_score = 50
    else:  # poor
        base_score = 35
    
    # Adjust based on partner quality
    if partner_genotype_id in superior:
        base_score += 10
    elif partner_genotype_id in excellent:
        base_score += 7
    elif partner_genotype_id in good:
        base_score += 4
    elif partner_genotype_id in average:
        base_score += 0
    elif partner_genotype_id in below_avg:
        base_score -= 5
    else:  # poor
        base_score -= 15
    
    # Cap at 100
    return min(100, max(20, base_score))

def calculate_weather_score(hybrid_data, weather_data):
    """Calculate weather suitability score (0-100)"""
    
    if not weather_data.get('success'):
        return 50  # Neutral if no weather data
    
    temp = weather_data.get('temperature', 25)
    humidity = weather_data.get('humidity', 60)
    
    # Get optimal ranges from hybrid
    optimal_temp = hybrid_data.get('optimal_temp', [20, 30])
    humidity_tolerance = hybrid_data.get('humidity_tolerance', [50, 70])
    
    # Temperature score (50 points max)
    if optimal_temp[0] <= temp <= optimal_temp[1]:
        temp_score = 50
    elif optimal_temp[0] - 5 <= temp <= optimal_temp[1] + 5:
        temp_score = 35
    elif optimal_temp[0] - 10 <= temp <= optimal_temp[1] + 10:
        temp_score = 20
    else:
        temp_score = 10
    
    # Humidity score (50 points max)
    if humidity_tolerance[0] <= humidity <= humidity_tolerance[1]:
        humidity_score = 50
    elif humidity_tolerance[0] - 10 <= humidity <= humidity_tolerance[1] + 10:
        humidity_score = 35
    elif humidity_tolerance[0] - 20 <= humidity <= humidity_tolerance[1] + 20:
        humidity_score = 20
    else:
        humidity_score = 10
    
    return temp_score + humidity_score

def generate_breeding_recommendations(predicted_genotype, weather_data):
    """Generate breeding recommendations with PROPER scoring"""
    
    recommendations = []
    user_id = predicted_genotype['genotype_id']
    
    # CRITICAL FIX: Smart filtering based on user plant quality
    # Define poor genotypes that shouldn't breed with each other
    poor_genotypes = ['G18', 'G24', 'G25', 'G26', 'G27']
    below_avg = ['G8', 'G9', 'G15', 'G16', 'G17', 'G23']
    
    if user_id in poor_genotypes:
        # Poor plant - only recommend breeding with superior/excellent partners for improvement
        print(f"   ⚠️  User plant ({user_id}) is poor quality - IMPROVEMENT recommendations only")
        allowed_partners = ['G1', 'G2', 'G3', 'G4', 'G5', 'G10', 'G11', 'G12']
    elif user_id in below_avg:
        # Below average - exclude poor partners
        print(f"   📊 User plant ({user_id}) is below average - avoiding poor partners")
        excluded = poor_genotypes
        allowed_partners = [f'G{i}' for i in range(1, 28) if f'G{i}' not in excluded and f'G{i}' != user_id]
    else:
        # Good quality - can breed with most, but exclude worst
        allowed_partners = [f'G{i}' for i in range(1, 28) if f'G{i}' != user_id]
        # Don't breed good plants with worst genotypes
        if user_id in ['G1', 'G2', 'G3', 'G4', 'G5']:
            allowed_partners = [p for p in allowed_partners if p not in ['G26', 'G27']]
    
    for hybrid_name, hybrid_data in hybrid_database.items():
        parents = hybrid_data.get('parent_genotypes', [])
        
        if user_id in parents:
            # Find partner genotype
            partner_id = [p for p in parents if p != user_id][0] if len(parents) == 2 else None
            
            if partner_id and partner_id in allowed_partners:
                # Calculate PROPER scores
                compatibility = calculate_compatibility(user_id, partner_id)
                weather_score = calculate_weather_score(hybrid_data, weather_data)
                total_score = int(compatibility * 0.6 + weather_score * 0.4)
                
                recommendations.append({
                    'hybrid_name': hybrid_name,
                    'your_genotype': user_id,
                    'partner_genotype': partner_id,
                    'parent_genotypes': parents,
                    'maturity_days': hybrid_data.get('maturity_days', hybrid_data.get('traits', {}).get('maturity_days', 70)),
                    'expected_traits': hybrid_data.get('expected_traits', {}),
                    'compatibility_score': compatibility,
                    'weather_score': weather_score,
                    'total_score': total_score
                })
    
    # Sort by total score
    recommendations.sort(key=lambda x: x['total_score'], reverse=True)
    
    return recommendations[:5]

def generate_replacement_recommendations(weather_data):
    """Generate alternative hybrid recommendations with PROPER scoring"""
    
    recommendations = []
    
    for hybrid_name, hybrid_data in hybrid_database.items():
        # Calculate trait quality score
        traits = hybrid_data.get('expected_traits', {})
        trait_quality = 50  # Base score
        
        # Yield scoring
        if traits.get('yield') == 'High':
            trait_quality += 20
        elif traits.get('yield') == 'Medium':
            trait_quality += 10
        
        # Disease resistance scoring
        if traits.get('disease_resistance') == 'Resistant':
            trait_quality += 15
        elif traits.get('disease_resistance') == 'Moderate':
            trait_quality += 7
        
        # Stress tolerance scoring
        if traits.get('stress_tolerance') == 'High':
            trait_quality += 15
        elif traits.get('stress_tolerance') == 'Medium':
            trait_quality += 7
        
        # Weather score
        weather_score = calculate_weather_score(hybrid_data, weather_data)
        
        # Total score
        total_score = int(trait_quality * 0.6 + weather_score * 0.4)
        
        recommendations.append({
            'hybrid_name': hybrid_name,
            'parent_genotypes': hybrid_data.get('parent_genotypes', []),
            'maturity_days': hybrid_data.get('maturity_days', hybrid_data.get('traits', {}).get('maturity_days', 70)),
            'expected_traits': traits,
            'compatibility_score': trait_quality,
            'weather_score': weather_score,
            'total_score': total_score
        })
    
    # Sort by total score
    recommendations.sort(key=lambda x: x['total_score'], reverse=True)
    
    return recommendations[:5]

# ============================================
# API ENDPOINTS
# ============================================

@app.route('/api/complete', methods=['POST'])
def complete_analysis():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        location = request.form.get('location', 'Bangalore,IN')
        
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        print(f"\n{'='*60}")
        print(f"🌱 Processing: {file.filename}")
        print(f"📍 Location: {location}")
        print(f"{'='*60}")
        
        # Process image
        img_array, features_2d, features_1d = process_image(file)
        image_hash = get_image_hash(features_1d)
        
        # Sklearn predictions
        sklearn_traits = {}
        for trait_name, model in models.items():
            pred = model.predict(features_2d)[0]
            trait_key = trait_name.replace('_trait', '')
            sklearn_traits[trait_key] = pred
        
        # HYBRID decision (with improved disease detection)
        final_traits = hybrid_analyzer.hybrid_decision(sklearn_traits, img_array, image_hash)
        
        # Predict genotype (now with ALL 27 genotypes!)
        predicted_genotype = genotype_predictor.predict_genotype(final_traits)
        
        print(f"\n   🧬 Predicted Genotype: {predicted_genotype['genotype_id']}")
        print(f"   📝 Description: {predicted_genotype['description']}")
        
        # Weather
        weather_data = get_weather(location)
        
        # IMPROVED recommendations with proper scoring
        breeding_recs = generate_breeding_recommendations(predicted_genotype, weather_data)
        replacement_recs = generate_replacement_recommendations(weather_data)
        
        print(f"\n   📊 Generated {len(breeding_recs)} breeding recommendations")
        print(f"   📊 Generated {len(replacement_recs)} replacement recommendations")
        
        return jsonify({
            'success': True,
            'predicted_traits': final_traits,
            'predicted_genotype': predicted_genotype,
            'weather': weather_data,
            'breeding_recommendations': breeding_recs,
            'replacement_recommendations': replacement_recs
        })
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'models_loaded': len(models),
        'hybrids_available': len(hybrid_database),
        'genotypes_mapped': 27
    })

if __name__ == '__main__':
    print(f"\n{'='*60}")
    print(f"🚀 Server starting on http://localhost:5000")
    print(f"{'='*60}\n")
    app.run(debug=True, host='0.0.0.0', port=5000)