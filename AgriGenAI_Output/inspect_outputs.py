"""
Script to Inspect Day 1 Output Files
=====================================
This helps you understand what's stored in .npy and .npz files
"""

import numpy as np
import pandas as pd
from pathlib import Path

print("=" * 60)
print("🔍 Inspecting Day 1 Output Files")
print("=" * 60)

# Paths
FEATURES_FILE = Path('features/phenotype_features.npy')
STATS_FILE = Path('features/feature_statistics.npz')
METADATA_FILE = Path('metadata/image_metadata.csv')


# ============================================
# 1. PHENOTYPE FEATURES (.npy)
# ============================================

print("\n📊 1. phenotype_features.npy")
print("-" * 60)

features = np.load(FEATURES_FILE)

print(f"✅ File loaded successfully!")
print(f"   Shape: {features.shape}")
print(f"   - Number of images: {features.shape[0]}")
print(f"   - Features per image: {features.shape[1]} (ResNet50 output)")
print(f"   Data type: {features.dtype}")
print(f"   File size: {FEATURES_FILE.stat().st_size / (1024*1024):.2f} MB")

print(f"\n🔢 Sample Feature Vector (first 10 values of image #1):")
print(features[0, :10])

print(f"\n📈 Feature Statistics:")
print(f"   Mean across all features: {features.mean():.4f}")
print(f"   Std across all features: {features.std():.4f}")
print(f"   Min value: {features.min():.4f}")
print(f"   Max value: {features.max():.4f}")

print(f"\n💡 What this means:")
print(f"   Each of your {features.shape[0]} images is represented as a")
print(f"   2048-dimensional vector. These numbers encode phenotype traits:")
print(f"   - Leaf shape, texture, color patterns")
print(f"   - Fruit size, roundness, color intensity")
print(f"   - Visual features that correlate with genotype!")

# ============================================
# 2. FEATURE STATISTICS (.npz)
# ============================================

print("\n\n📊 2. feature_statistics.npz")
print("-" * 60)

stats = np.load(STATS_FILE)

print(f"✅ File loaded successfully!")
print(f"   Contains {len(stats.files)} arrays: {stats.files}")

for key in stats.files:
    arr = stats[key]
    print(f"\n   '{key}': shape {arr.shape}")
    print(f"      First 5 values: {arr[:5]}")

print(f"\n💡 What this means:")
print(f"   These statistics help normalize new images:")
print(f"   - 'mean': Average value for each of 2048 features")
print(f"   - 'std': How much each feature varies")
print(f"   - 'min/max': Range of values")
print(f"   Used in Day 2 for feature preprocessing!")

# ============================================
# 3. IMAGE METADATA (.csv)
# ============================================

print("\n\n📊 3. image_metadata.csv")
print("-" * 60)

df = pd.read_csv(METADATA_FILE)

print(f"✅ File loaded successfully!")
print(f"   Rows (images): {len(df)}")
print(f"   Columns: {list(df.columns)}")

print(f"\n📋 First 5 rows:")
print(df.head())

print(f"\n📊 Data Summary:")
print(f"   Total images: {len(df)}")
print(f"   - PlantVillage (leaves): {len(df[df['source']=='PlantVillage'])}")
print(f"   - Laboro (fruits): {len(df[df['source']=='Laboro'])}")

print(f"\n   Leaf categories:")
for cat in df[df['organ']=='leaf']['category'].unique():
    count = len(df[df['category']==cat])
    print(f"      - {cat}: {count} images")

print(f"\n💡 What this means:")
print(f"   This CSV links each feature vector to its original image.")
print(f"   In Day 2, you'll use this to:")
print(f"   - Map features → traits (disease resistance, yield, etc.)")
print(f"   - Train ML models for genotype prediction")

# ============================================
# 4. HOW TO USE THESE FILES
# ============================================

print("\n\n" + "=" * 60)
print("🎯 How to Use These Files in Day 2")
print("=" * 60)

print("""
Day 2 Workflow:
--------------
1. Load phenotype_features.npy → These are your X (input features)
2. Load image_metadata.csv → Match features to image categories
3. Create labels for traits:
   - High yield / Medium / Low (from disease categories)
   - Heat tolerance (infer from leaf health patterns)
   - Disease resistance (directly from categories)
4. Train Random Forest: features → trait predictions
5. Save trained model for Day 3 hybrid recommendations

Example Code Snippet:
--------------------
# Load features
features = np.load('phenotype_features.npy')

# Load metadata
df = pd.read_csv('image_metadata.csv')

# Create trait labels (simplified mapping)
df['yield_trait'] = df['category'].map({
    'healthy': 'High',
    'Early_blight': 'Medium',
    'Late_blight': 'Low',
    # ... etc
})

# Train model
from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier()
model.fit(features, df['yield_trait'])
""")

# ============================================
# 5. VERIFY DATA ALIGNMENT
# ============================================

print("\n" + "=" * 60)
print("✅ Data Alignment Verification")
print("=" * 60)

print(f"\n✅ Features shape: {features.shape}")
print(f"✅ Metadata rows: {len(df)}")

if features.shape[0] == len(df):
    print(f"\n🎉 PERFECT ALIGNMENT!")
    print(f"   Each of {len(df)} rows in metadata matches")
    print(f"   a feature vector in phenotype_features.npy")
else:
    print(f"\n⚠️  MISMATCH DETECTED!")
    print(f"   Features: {features.shape[0]}")
    print(f"   Metadata: {len(df)}")

# ============================================
# 6. EXAMPLE: View Specific Image Data
# ============================================

print("\n" + "=" * 60)
print("🔍 Example: View Data for Specific Image")
print("=" * 60)

sample_idx = 0
sample_row = df.iloc[sample_idx]
sample_features = features[sample_idx]

print(f"\nImage #{sample_idx}:")
print(f"   Path: {sample_row['image_path']}")
print(f"   Source: {sample_row['source']}")
print(f"   Category: {sample_row['category']}")
print(f"   Organ: {sample_row['organ']}")
print(f"\n   Feature vector preview (first 10):")
print(f"   {sample_features[:10]}")
print(f"\n   Feature vector stats:")
print(f"   - Mean: {sample_features.mean():.4f}")
print(f"   - Std: {sample_features.std():.4f}")
print(f"   - Min: {sample_features.min():.4f}")
print(f"   - Max: {sample_features.max():.4f}")

print("\n" + "=" * 60)
print("✅ Inspection Complete!")
print("=" * 60)
print("\n🚀 You're ready for Day 2: Genotype-Trait Mapping!")
print("   These files contain all the phenotype data you need.")