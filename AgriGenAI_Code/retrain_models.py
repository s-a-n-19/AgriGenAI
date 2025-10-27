"""
AgriGenAI - MODEL RETRAINING SCRIPT
=====================================
Combines PlantVillage + Laboro datasets
Creates proper trait labels for field images with fruits
Trains models that will work with your existing backend
"""

import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from PIL import Image
import cv2
import json
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib
import warnings
import shutil
from datetime import datetime
warnings.filterwarnings('ignore')

# TensorFlow
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input

print("="*70)
print("🔄 AgriGenAI - MODEL RETRAINING")
print("="*70)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ============================================
# CONFIGURATION
# ============================================

class Config:
    # Input paths
    BASE_PATH = Path('C:/Users/sahan/Desktop/AgriGenAI2/AgriGenAI_Dataset')
    PLANTVILLAGE_PATH = BASE_PATH / 'PlantVillage/images'
    LABORO_PATH = BASE_PATH / 'Laboro'
    
    # Output paths
    OUTPUT_PATH = Path('C:/Users/sahan/Desktop/AgriGenAI2/AgriGenAI_Output')
    
    # Settings
    IMG_SIZE = (224, 224)
    RANDOM_STATE = 42
    MAX_IMAGES_PER_CATEGORY = None  # Use ALL images
    AUGMENT_LABORO = True  # Create augmented versions of Laboro (better than duplicating!)
    LABORO_AUGMENTATION_FACTOR = 50  # Create 50 variations per Laboro image

# Verify paths exist
print("\n📂 Verifying dataset paths...")
if not Config.PLANTVILLAGE_PATH.exists():
    print(f"❌ ERROR: PlantVillage not found at {Config.PLANTVILLAGE_PATH}")
    exit(1)
if not Config.LABORO_PATH.exists():
    print(f"❌ ERROR: Laboro not found at {Config.LABORO_PATH}")
    exit(1)
print("✅ All dataset paths verified")

# Fix .jppg files (common typo in Laboro dataset)
print("\n🔧 Checking for .jppg files (should be .jpg)...")
laboro_images_path = Config.LABORO_PATH / 'images'
if laboro_images_path.exists():
    jppg_files = list(laboro_images_path.glob('*.jppg'))
    if jppg_files:
        print(f"   Found {len(jppg_files)} files with .jppg extension")
        print("   Renaming to .jpg...")
        renamed_count = 0
        for jppg_file in jppg_files:
            try:
                jpg_file = jppg_file.with_suffix('.jpg')
                jppg_file.rename(jpg_file)
                renamed_count += 1
            except Exception as e:
                print(f"   ⚠️  Could not rename {jppg_file.name}: {e}")
        print(f"   ✅ Renamed {renamed_count}/{len(jppg_files)} files to .jpg")
    else:
        print("   ✅ No .jppg files found - all good!")
else:
    print("   ⚠️  Laboro images folder not found")


# Create backup
print("\n🛡️  Creating backup...")
backup_path = Config.OUTPUT_PATH / 'backup_before_retrain'
backup_path.mkdir(parents=True, exist_ok=True)

models_path = Config.OUTPUT_PATH / 'models'
if models_path.exists():
    for file in models_path.glob('*.pkl'):
        shutil.copy2(file, backup_path / file.name)
        print(f"   ✅ Backed up: {file.name}")
else:
    print("   ℹ️  No existing models to backup")

# ============================================
# LOAD RESNET50
# ============================================

print("\n📦 Loading ResNet50 feature extractor...")
try:
    feature_extractor = ResNet50(
        weights='imagenet',
        include_top=False,
        pooling='avg',
        input_shape=(224, 224, 3)
    )
    print("✅ ResNet50 loaded successfully")
except Exception as e:
    print(f"❌ ERROR loading ResNet50: {e}")
    exit(1)

# ============================================
# TRAIT LABELING LOGIC
# ============================================

class SmartTraitMapper:
    """
    Maps images to realistic trait combinations
    """
    
    @staticmethod
    def label_plantvillage(category):
        """Label PlantVillage disease images"""
        
        if category == 'healthy':
            return {
                'yield': 'High',
                'disease_resistance': 'Resistant',
                'stress_tolerance': 'High',
                'source': 'PlantVillage-Healthy'
            }
        
        elif category in ['Bacterial_spot', 'Leaf_Mold', 'Septoria_leaf_spot', 
                         'Target_Spot', 'Two-spotted_spider_mite']:
            return {
                'yield': 'Medium',
                'disease_resistance': 'Moderate',
                'stress_tolerance': 'Medium',
                'source': f'PlantVillage-Moderate'
            }
        
        elif category in ['Early_blight', 'Late_blight', 'Tomato_mosaic_virus',
                         'Tomato_Yellow_Leaf_Curl_Virus']:
            return {
                'yield': 'Low',
                'disease_resistance': 'Susceptible',
                'stress_tolerance': 'Low',
                'source': f'PlantVillage-Severe'
            }
        
        else:
            return {
                'yield': 'Medium',
                'disease_resistance': 'Moderate',
                'stress_tolerance': 'Medium',
                'source': 'PlantVillage-Other'
            }
    
    @staticmethod
    def label_laboro(img_path):
        """
        Analyze Laboro field image
        Detects: fruits, green foliage, disease indicators
        """
        try:
            # Load image
            img = cv2.imread(str(img_path))
            if img is None:
                return None
            
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            
            # Analyze green (healthy foliage)
            green_mask = cv2.inRange(img_hsv, 
                                     np.array([35, 40, 40]), 
                                     np.array([85, 255, 255]))
            green_ratio = np.count_nonzero(green_mask) / green_mask.size
            
            # Detect fruits (red/orange)
            red_mask1 = cv2.inRange(img_hsv, np.array([0, 50, 50]), np.array([10, 255, 255]))
            red_mask2 = cv2.inRange(img_hsv, np.array([170, 50, 50]), np.array([180, 255, 255]))
            orange_mask = cv2.inRange(img_hsv, np.array([10, 50, 50]), np.array([25, 255, 255]))
            
            fruit_mask = cv2.bitwise_or(cv2.bitwise_or(red_mask1, red_mask2), orange_mask)
            fruit_ratio = np.count_nonzero(fruit_mask) / fruit_mask.size
            
            # Detect disease (brown/yellowing)
            disease_mask = cv2.inRange(img_hsv, 
                                      np.array([15, 40, 40]), 
                                      np.array([35, 255, 200]))
            disease_ratio = np.count_nonzero(disease_mask) / disease_mask.size
            
            # Brightness
            brightness = np.mean(img_hsv[:,:,2]) / 255
            
            # LABELING LOGIC
            has_fruits = fruit_ratio > 0.05
            is_green = green_ratio > 0.40
            has_disease = disease_ratio > 0.15
            is_bright = brightness > 0.50
            
            # HEALTHY with fruits
            if has_fruits and is_green and not has_disease and is_bright:
                return {
                    'yield': 'High',
                    'disease_resistance': 'Resistant',
                    'stress_tolerance': 'High',
                    'source': 'Laboro-Healthy-Fruiting'
                }
            
            # HEALTHY foliage (no fruits yet)
            elif is_green and is_bright and not has_disease:
                return {
                    'yield': 'High',
                    'disease_resistance': 'Resistant',
                    'stress_tolerance': 'Medium',
                    'source': 'Laboro-Healthy-Vegetative'
                }
            
            # Some disease visible
            elif has_disease and is_green:
                return {
                    'yield': 'Medium',
                    'disease_resistance': 'Moderate',
                    'stress_tolerance': 'Medium',
                    'source': 'Laboro-Moderate-Disease'
                }
            
            # Poor health
            elif has_disease or not is_green:
                return {
                    'yield': 'Low',
                    'disease_resistance': 'Susceptible',
                    'stress_tolerance': 'Low',
                    'source': 'Laboro-Diseased'
                }
            
            # Default
            else:
                return {
                    'yield': 'Medium',
                    'disease_resistance': 'Moderate',
                    'stress_tolerance': 'Medium',
                    'source': 'Laboro-Average'
                }
        
        except Exception as e:
            print(f"      ⚠️  Error analyzing {img_path.name}: {e}")
            return None

# ============================================
# LOAD PLANTVILLAGE
# ============================================

print("\n📂 Loading PlantVillage dataset...")
mapper = SmartTraitMapper()
plantvillage_data = []

categories_found = []
for category_folder in Config.PLANTVILLAGE_PATH.iterdir():
    if category_folder.is_dir():
        category = category_folder.name
        categories_found.append(category)
        
        images = list(category_folder.glob('*.jpg'))
        if Config.MAX_IMAGES_PER_CATEGORY:
            images = images[:Config.MAX_IMAGES_PER_CATEGORY]
        
        for img_path in images:
            traits = mapper.label_plantvillage(category)
            plantvillage_data.append({
                'image_path': str(img_path),
                'category': category,
                'dataset': 'PlantVillage',
                **traits
            })
        
        print(f"   ✅ {category}: {len(images)} images")

print(f"\n   Total PlantVillage: {len(plantvillage_data)} images")
print(f"   Categories: {', '.join(categories_found)}")

# ============================================
# LOAD LABORO
# ============================================

print("\n📂 Loading Laboro dataset...")
laboro_data = []
laboro_images = list(Config.LABORO_PATH.glob('images/*.jpg'))

# ===== ADD THIS DEBUG CODE =====
print(f"\n🔍 DEBUG: Validating {len(laboro_images)} Laboro image paths...")
bad_paths = []
for img_path in laboro_images:
    if img_path.suffix.lower() != '.jpg':
        bad_paths.append(str(img_path))
        print(f"   ⚠️  NON-JPG: {img_path}")

if bad_paths:
    print(f"\n❌ Found {len(bad_paths)} non-.jpg files! Stopping.")
    for p in bad_paths[:10]:
        print(f"      {p}")
    exit(1)
else:
    print("   ✅ All {len(laboro_images)} paths are .jpg!")
# ===== END DEBUG CODE =====

print(f"   Found: {len(laboro_images)} images")
print("   Analyzing visual health...")

for i, img_path in enumerate(laboro_images):
    if i % 50 == 0 and i > 0:
        print(f"      Progress: {i}/{len(laboro_images)}")
    
    traits = mapper.label_laboro(img_path)
    if traits:
        laboro_data.append({
            'image_path': str(img_path),
            'category': 'field_image',
            'dataset': 'Laboro',
            **traits
        })

print(f"\n   Total Laboro: {len(laboro_data)} images")

# ============================================
# AUGMENT LABORO IMAGES
# ============================================

def augment_image(img_path, augmentation_id):
    """
    Create augmented version of an image
    Returns: augmented image array
    """
    import random
    
    try:
        # Load image
        img = cv2.imread(str(img_path))
        if img is None:
            return None
        
        # Validate image
        if img.size == 0 or len(img.shape) != 3:
            return None
        
        # Seed random for reproducibility per augmentation_id
        random.seed(int(augmentation_id))
        np.random.seed(int(augmentation_id))
        
        # Get original dimensions and FORCE to Python int
        h, w = img.shape[:2]
        h = int(h)
        w = int(w)
        
        # Apply random augmentations
        
        # 1. Random rotation (-20 to +20 degrees)
        angle = float(random.uniform(-20, 20))
        center = (int(w // 2), int(h // 2))
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        img = cv2.warpAffine(img, M, (int(w), int(h)), borderMode=cv2.BORDER_REFLECT)
        
        # 2. Random flip (50% chance horizontal, 25% chance vertical)
        if random.random() < 0.5:
            img = cv2.flip(img, 1)  # Horizontal flip
        if random.random() < 0.25:
            img = cv2.flip(img, 0)  # Vertical flip
        
        # 3. Random brightness (0.7 to 1.3)
        brightness_factor = float(random.uniform(0.7, 1.3))
        img = img.astype(np.float32)
        img = img * brightness_factor
        img = np.clip(img, 0, 255).astype(np.uint8)
        
        # 4. Random contrast (0.8 to 1.2)
        contrast_factor = float(random.uniform(0.8, 1.2))
        img = img.astype(np.float32)
        img = (img - 128.0) * contrast_factor + 128.0
        img = np.clip(img, 0, 255).astype(np.uint8)
        
        # 5. Random zoom/crop - DISABLED (to avoid complex type issues)
        pass
        
        # 6. Random hue shift (for color variation)
        if img.shape[0] > 0 and img.shape[1] > 0:
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            hsv = hsv.astype(np.float32)
            hue_shift = float(random.uniform(-10, 10))
            
            # Apply hue shift with explicit float conversion
            hsv[:, :, 0] = np.float32((hsv[:, :, 0] + hue_shift) % 180.0)
            
            # Safely convert back
            hsv = np.clip(hsv, 0, 255).astype(np.uint8)
            img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        return img
        
    except Exception as e:
        # Silent fail - just return None
        return None

if Config.AUGMENT_LABORO and len(laboro_data) > 0:
    print(f"\n🔄 Augmenting Laboro images...")
    pv_count = len(plantvillage_data)
    laboro_original_count = len(laboro_data)
    
    print(f"   PlantVillage: {pv_count} images")
    print(f"   Laboro (original): {laboro_original_count} images")
    print(f"   Creating {Config.LABORO_AUGMENTATION_FACTOR} variations per Laboro image...")
    
    augmented_laboro = []
    
    # Keep original Laboro images
    augmented_laboro.extend(laboro_data)
    
    # Create augmented versions
    for aug_round in range(1, Config.LABORO_AUGMENTATION_FACTOR):
        if aug_round % 10 == 0:
            print(f"      Progress: {aug_round}/{Config.LABORO_AUGMENTATION_FACTOR}")
        
        for original_item in laboro_data:
            # Create augmented version
            augmented_laboro.append({
                **original_item,
                'augmentation_id': aug_round,
                'source': f"{original_item['source']}-Aug{aug_round}"
            })
    
    print(f"   Laboro (with augmentation): {len(augmented_laboro)} images")
    print(f"   ✅ Each original image has {Config.LABORO_AUGMENTATION_FACTOR} unique variations!")
    
    # Replace laboro_data
    laboro_data = augmented_laboro

# ============================================
# COMBINE & ANALYZE
# ============================================

print("\n🔗 Combining datasets...")
all_data = plantvillage_data + laboro_data
df = pd.DataFrame(all_data)

print(f"\n📊 Combined Dataset:")
print(f"   Total images: {len(df)}")
print(f"   PlantVillage: {len(plantvillage_data)}")
print(f"   Laboro: {len(laboro_data)}")

print(f"\n   Trait Distributions:")
print(f"\n   Yield:")
for val, count in df['yield'].value_counts().items():
    print(f"      {val}: {count} ({count/len(df)*100:.1f}%)")

print(f"\n   Disease Resistance:")
for val, count in df['disease_resistance'].value_counts().items():
    print(f"      {val}: {count} ({count/len(df)*100:.1f}%)")

print(f"\n   Stress Tolerance:")
for val, count in df['stress_tolerance'].value_counts().items():
    print(f"      {val}: {count} ({count/len(df)*100:.1f}%)")

# Save metadata
metadata_path = Config.OUTPUT_PATH / 'metadata'
metadata_path.mkdir(exist_ok=True)
metadata_file = metadata_path / 'combined_training_data.csv'
df.to_csv(metadata_file, index=False)
print(f"\n💾 Saved metadata: {metadata_file}")

# ============================================
# EXTRACT FEATURES
# ============================================

print("\n🔬 Extracting ResNet50 features...")
print("   (This may take 30-60 minutes depending on dataset size)")

features_list = []
valid_indices = []

for idx, row in df.iterrows():
    if idx % 100 == 0:
        print(f"   Progress: {idx}/{len(df)} ({idx/len(df)*100:.1f}%)")
    
    try:
        # Check if this is an augmented Laboro image
        if 'augmentation_id' in row and row['dataset'] == 'Laboro' and row.get('augmentation_id'):
            # Apply augmentation to the image
            original_path = row['image_path']
            aug_id = row['augmentation_id']
            img_array_bgr = augment_image(original_path, aug_id)
            
            if img_array_bgr is None:
                print(f"   ⚠️  Augmentation failed for: {original_path}")
                continue
            
            # Validate image dimensions
            if img_array_bgr.shape[0] == 0 or img_array_bgr.shape[1] == 0:
                print(f"   ⚠️  Invalid dimensions after augmentation: {original_path}")
                continue
            
            # Convert BGR to RGB and resize
            img_array_rgb = cv2.cvtColor(img_array_bgr, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img_array_rgb)
            img = img.resize(Config.IMG_SIZE)
        else:
            # Load original image normally
            img = Image.open(row['image_path']).convert('RGB')
            img = img.resize(Config.IMG_SIZE)
        
        img_array = np.array(img)
        
        # Validate array
        if img_array.size == 0:
            print(f"   ⚠️  Empty array: {row['image_path']}")
            continue
        
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        
        # Extract features
        features = feature_extractor.predict(img_array, verbose=0)
        features_list.append(features[0])
        valid_indices.append(idx)
        
    except Exception as e:
        print(f"   ⚠️  Failed: {row['image_path']} - {str(e)}")

features_array = np.array(features_list)
df_valid = df.loc[valid_indices].reset_index(drop=True)

print(f"\n✅ Feature extraction complete!")
print(f"   Features shape: {features_array.shape}")
print(f"   Valid samples: {len(df_valid)}")

# Save features
features_path = Config.OUTPUT_PATH / 'features'
features_path.mkdir(exist_ok=True)
features_file = features_path / 'retrained_features.npy'
np.save(features_file, features_array)
print(f"💾 Saved features: {features_file}")

# ============================================
# TRAIN MODELS
# ============================================

print("\n🤖 Training machine learning models...")

models = {}
results = {}

trait_configs = {
    'yield_trait': ('yield', df_valid['yield']),
    'disease_resistance_trait': ('disease_resistance', df_valid['disease_resistance']),
    'stress_tolerance_trait': ('stress_tolerance', df_valid['stress_tolerance'])
}

for model_name, (trait_display, trait_labels) in trait_configs.items():
    print(f"\n   Training: {trait_display}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        features_array, trait_labels,
        test_size=0.2,
        random_state=Config.RANDOM_STATE,
        stratify=trait_labels
    )
    
    print(f"      Train: {len(X_train)}, Test: {len(X_test)}")
    
    # Train Random Forest
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=20,
        min_samples_split=5,
        random_state=Config.RANDOM_STATE,
        n_jobs=-1,
        class_weight='balanced'  # Handle class imbalance
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"      ✅ Accuracy: {accuracy:.2%}")
    print(f"\n      Per-class performance:")
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    for class_name, metrics in report.items():
        if class_name not in ['accuracy', 'macro avg', 'weighted avg']:
            print(f"         {class_name}: Precision={metrics['precision']:.2%}, Recall={metrics['recall']:.2%}")
    
    # Save model
    models_output = Config.OUTPUT_PATH / 'models'
    models_output.mkdir(exist_ok=True)
    model_file = models_output / f'{model_name}_model.pkl'
    joblib.dump(model, model_file)
    print(f"      💾 Saved: {model_file}")
    
    models[model_name] = model
    results[model_name] = {
        'accuracy': accuracy,
        'y_test': y_test,
        'y_pred': y_pred
    }

# ============================================
# SAVE GENOTYPE PREDICTOR
# ============================================

print("\n💾 Saving genotype predictor (27 genotypes)...")

class GenotypePredictorSimulator:
    def __init__(self, hybrid_database=None):
        self.hybrid_db = hybrid_database or {}
        self.genotype_map = self._build_complete_genotype_map()
    
    def _build_complete_genotype_map(self):
        return {
            ('High', 'Resistant', 'High'): {'genotype_id': 'G1', 'genes': ['fw2.2-AA', 'HSP-High', 'Tm-2a-Present'], 'description': 'Superior genotype'},
            ('High', 'Resistant', 'Medium'): {'genotype_id': 'G2', 'genes': ['fw2.2-Aa', 'HSP-Medium', 'Tm-2a-Present'], 'description': 'Excellent genotype'},
            ('High', 'Resistant', 'Low'): {'genotype_id': 'G9', 'genes': ['fw2.2-AA', 'HSP-Low', 'Tm-2a-Present'], 'description': 'High yield, resistant'},
            ('High', 'Moderate', 'High'): {'genotype_id': 'G10', 'genes': ['fw2.2-Aa', 'HSP-High', 'Tm-2-Partial'], 'description': 'High yield, stress tolerant'},
            ('High', 'Moderate', 'Medium'): {'genotype_id': 'G3', 'genes': ['fw2.2-Aa', 'HSP-Medium', 'Tm-2-Absent'], 'description': 'Good all-rounder'},
            ('High', 'Moderate', 'Low'): {'genotype_id': 'G11', 'genes': ['fw2.2-AA', 'HSP-Low', 'Tm-2-Absent'], 'description': 'High yield'},
            ('High', 'Susceptible', 'High'): {'genotype_id': 'G12', 'genes': ['fw2.2-Aa', 'HSP-High', 'Tm-2-Absent'], 'description': 'High yield, susceptible'},
            ('High', 'Susceptible', 'Medium'): {'genotype_id': 'G13', 'genes': ['fw2.2-AA', 'HSP-Medium', 'Tm-2-Absent'], 'description': 'Needs protection'},
            ('High', 'Susceptible', 'Low'): {'genotype_id': 'G14', 'genes': ['fw2.2-Aa', 'HSP-Low', 'Tm-2-Absent'], 'description': 'Vulnerable'},
            ('Medium', 'Resistant', 'High'): {'genotype_id': 'G5', 'genes': ['fw2.2-AA', 'HSP-High', 'Tm-2a-Present'], 'description': 'Balanced genotype'},
            ('Medium', 'Resistant', 'Medium'): {'genotype_id': 'G6', 'genes': ['fw2.2-Aa', 'HSP-Medium', 'Tm-2a-Present'], 'description': 'Good resistance'},
            ('Medium', 'Resistant', 'Low'): {'genotype_id': 'G15', 'genes': ['fw2.2-aa', 'HSP-Low', 'Tm-2a-Present'], 'description': 'Resistant, stress sensitive'},
            ('Medium', 'Moderate', 'High'): {'genotype_id': 'G4', 'genes': ['fw2.2-aa', 'HSP-High', 'Tm-2-Absent'], 'description': 'Stress tolerant'},
            ('Medium', 'Moderate', 'Medium'): {'genotype_id': 'G7', 'genes': ['fw2.2-Aa', 'HSP-Medium', 'Tm-2-Partial'], 'description': 'Average genotype'},
            ('Medium', 'Moderate', 'Low'): {'genotype_id': 'G16', 'genes': ['fw2.2-aa', 'HSP-Low', 'Tm-2-Absent'], 'description': 'Below average'},
            ('Medium', 'Susceptible', 'High'): {'genotype_id': 'G17', 'genes': ['fw2.2-Aa', 'HSP-High', 'Tm-2-Absent'], 'description': 'Stress tolerant'},
            ('Medium', 'Susceptible', 'Medium'): {'genotype_id': 'G18', 'genes': ['fw2.2-aa', 'HSP-Medium', 'Tm-2-Absent'], 'description': 'Needs protection'},
            ('Medium', 'Susceptible', 'Low'): {'genotype_id': 'G19', 'genes': ['fw2.2-aa', 'HSP-Low', 'Tm-2-Absent'], 'description': 'Poor traits'},
            ('Low', 'Resistant', 'High'): {'genotype_id': 'G20', 'genes': ['fw2.2-aa', 'HSP-High', 'Tm-2a-Present'], 'description': 'Low yield, resistant'},
            ('Low', 'Resistant', 'Medium'): {'genotype_id': 'G21', 'genes': ['fw2.2-aa', 'HSP-Medium', 'Tm-2a-Present'], 'description': 'Low yield'},
            ('Low', 'Resistant', 'Low'): {'genotype_id': 'G22', 'genes': ['fw2.2-aa', 'HSP-Low', 'Tm-2a-Present'], 'description': 'Only resistance favorable'},
            ('Low', 'Moderate', 'High'): {'genotype_id': 'G23', 'genes': ['fw2.2-aa', 'HSP-High', 'Tm-2-Absent'], 'description': 'Stress tolerant only'},
            ('Low', 'Moderate', 'Medium'): {'genotype_id': 'G24', 'genes': ['fw2.2-aa', 'HSP-Medium', 'Tm-2-Absent'], 'description': 'Below average'},
            ('Low', 'Moderate', 'Low'): {'genotype_id': 'G25', 'genes': ['fw2.2-aa', 'HSP-Low', 'Tm-2-Absent'], 'description': 'Poor performance'},
            ('Low', 'Susceptible', 'High'): {'genotype_id': 'G26', 'genes': ['fw2.2-aa', 'HSP-High', 'Tm-2-Absent'], 'description': 'Limited value'},
            ('Low', 'Susceptible', 'Medium'): {'genotype_id': 'G27', 'genes': ['fw2.2-aa', 'HSP-Medium', 'Tm-2-Absent'], 'description': 'Poor genotype'},
            ('Low', 'Susceptible', 'Low'): {'genotype_id': 'G8', 'genes': ['fw2.2-aa', 'HSP-Low', 'Tm-2-Absent'], 'description': 'Inferior genotype'},
        }
    
    def predict_genotype(self, predicted_traits):
        trait_key = (
            predicted_traits.get('yield'),
            predicted_traits.get('disease_resistance'),
            predicted_traits.get('stress_tolerance')
        )
        return self.genotype_map.get(trait_key, self.genotype_map[('Medium', 'Moderate', 'Medium')])

predictor = GenotypePredictorSimulator()
predictor_file = Config.OUTPUT_PATH / 'models' / 'genotype_predictor.pkl'
joblib.dump(predictor, predictor_file)
print(f"✅ Saved: {predictor_file}")

# ============================================
# FINAL SUMMARY
# ============================================

print("\n" + "="*70)
print("✅ RETRAINING COMPLETE!")
print("="*70)

print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

print(f"\n📊 Dataset Summary:")
print(f"   Total samples: {len(df_valid)}")
print(f"   PlantVillage: {len(plantvillage_data)}")
print(f"   Laboro: {len(laboro_data)}")

print(f"\n🎯 Model Performance:")
for model_name, result in results.items():
    print(f"   {model_name.replace('_trait', '')}: {result['accuracy']:.2%}")

print(f"\n📁 Files Saved:")
print(f"   ✅ Models → {Config.OUTPUT_PATH / 'models'}")
print(f"   ✅ Features → {features_file}")
print(f"   ✅ Metadata → {metadata_file}")
print(f"   ✅ Backup → {backup_path}")

print(f"\n🚀 NEXT STEPS:")
print(f"   1. Your backend will automatically use the NEW models")
print(f"   2. Restart backend:")
print(f"      cd C:\\Users\\sahan\\Desktop\\AgriGenAI2\\AgriGenAI_Code")
print(f"      python day4_backend_api.py")
print(f"   3. Test with images:")
print(f"      • Healthy plants with fruits → Should predict G1, G2, G5")
print(f"      • Diseased leaves → Should predict G8, G18, G19")

print(f"\n🔄 IF MODELS DON'T WORK:")
print(f"   Restore from backup:")
print(f"   copy {backup_path}\\*.pkl {Config.OUTPUT_PATH / 'models'}\\")

print("\n" + "="*70)
print("🎉 SUCCESS! Models trained with PlantVillage + Laboro data!")
print("="*70)