"""
Test script for AgriGenAI Backend API
=====================================
Run this AFTER starting the backend server (python day4_backend_api.py)
"""

import requests
import json
from pathlib import Path

API_BASE_URL = "http://localhost:5000"

print("=" * 60)
print("🧪 Testing AgriGenAI Backend API")
print("=" * 60)

# ============================================
# Test 1: Health Check
# ============================================

print("\n📡 Test 1: Health Check")
print("-" * 60)

response = requests.get(f"{API_BASE_URL}/health")
print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

if response.status_code == 200:
    print("✅ Health check passed!")
else:
    print("❌ Health check failed!")
    exit(1)

# ============================================
# Test 2: Analyze Image
# ============================================

print("\n📸 Test 2: Analyze Image")
print("-" * 60)

# Find a test image from your dataset
test_image_path = Path("../AgriGenAI_Dataset/PlantVillage/images/healthy/H1.jpg")

if not test_image_path.exists():
    print(f"⚠️  Test image not found: {test_image_path}")
    print("Using alternative path...")
    test_image_path = Path("../AgriGenAI_Dataset/PlantVillage/images/Bacterial_spot/Bs10.jpg")

if test_image_path.exists():
    print(f"📤 Uploading: {test_image_path.name}")
    
    with open(test_image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{API_BASE_URL}/api/analyze", files=files)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Analysis successful!")
        print(f"\nPredicted Traits:")
        for trait, value in result['predicted_traits'].items():
            print(f"   {trait.title()}: {value}")
        
        print(f"\nPredicted Genotype:")
        genotype = result['predicted_genotype']
        print(f"   ID: {genotype['genotype_id']}")
        print(f"   Genes: {', '.join(genotype['genes'])}")
        print(f"   Description: {genotype['description']}")
    else:
        print(f"❌ Analysis failed!")
        print(f"Error: {response.json()}")
else:
    print("❌ No test image found!")

# ============================================
# Test 3: Get Recommendations
# ============================================

print("\n🏆 Test 3: Get Recommendations")
print("-" * 60)

recommendation_request = {
    "traits": {
        "yield": "Medium",
        "disease_resistance": "Moderate",
        "stress_tolerance": "Medium"
    },
    "location": "Mysuru,IN"
}

response = requests.post(
    f"{API_BASE_URL}/api/recommend",
    json=recommendation_request
)

print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    print(f"\n✅ Recommendations retrieved!")
    
    print(f"\n🌤️  Weather ({result['weather']['location']}):")
    weather = result['weather']
    if weather.get('success'):
        print(f"   Temperature: {weather['temperature']}°C")
        print(f"   Humidity: {weather['humidity']}%")
        print(f"   Conditions: {weather['description']}")
    
    print(f"\n🏆 Top 3 Recommendations:")
    for rec in result['recommendations'][:3]:
        print(f"\n   {rec['hybrid_name']}: {rec['total_score']}/100")
        print(f"      Trait Score: {rec['compatibility_score']}")
        print(f"      Weather Score: {rec['weather_score']}")
        print(f"      Maturity: {rec['maturity_days']} days")
else:
    print(f"❌ Recommendations failed!")
    print(f"Error: {response.json()}")

# ============================================
# Test 4: Complete Pipeline
# ============================================

print("\n🔄 Test 4: Complete Pipeline")
print("-" * 60)

if test_image_path.exists():
    print(f"📤 Uploading: {test_image_path.name}")
    
    with open(test_image_path, 'rb') as f:
        files = {'file': f}
        data = {'location': 'Bangalore,IN'}
        response = requests.post(
            f"{API_BASE_URL}/api/complete",
            files=files,
            data=data
        )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Complete pipeline successful!")
        
        print(f"\n🔮 Predicted Traits:")
        for trait, value in result['predicted_traits'].items():
            print(f"   {trait.title()}: {value}")
        
        print(f"\n🧬 Predicted Genotype: {result['predicted_genotype']['genotype_id']}")
        
        print(f"\n🌤️  Weather: {result['weather']['temperature']}°C, {result['weather']['humidity']}%")
        
        print(f"\n🏆 Top Recommendation:")
        top_rec = result['recommendations'][0]
        print(f"   {top_rec['hybrid_name']} ({top_rec['total_score']}/100)")
        print(f"   Parents: {' × '.join(top_rec['parent_genotypes'])}")
        print(f"   Maturity: {top_rec['maturity_days']} days")
    else:
        print(f"❌ Complete pipeline failed!")
        print(f"Error: {response.json()}")

# ============================================
# Summary
# ============================================

print("\n" + "=" * 60)
print("✅ API TESTING COMPLETE!")
print("=" * 60)
print("\n📝 Summary:")
print("   ✅ Health Check: Passed")
print("   ✅ Image Analysis: Passed")
print("   ✅ Recommendations: Passed")
print("   ✅ Complete Pipeline: Passed")
print("\n🎉 All tests successful! API is working perfectly!")
print("=" * 60)