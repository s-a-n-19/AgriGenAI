"""
AgriGenAI - Additional Visualizations (Quick & High-Value)
===========================================================
Generates:
1. Class Distribution (per trait) - 5 minutes
2. Error Analysis Template - for future use
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (15, 10)

# ============================================================================
# SECTION 1: CLASS DISTRIBUTION (Per Trait)
# ============================================================================

def plot_class_distribution():
    """
    Show how training data is distributed across classes
    This helps explain per-class performance differences
    """
    
    # Based on your training data (53,905 samples)
    # These are ESTIMATED distributions - replace with actual if available
    
    distributions = {
        'Yield': {
            'classes': ['High', 'Medium', 'Low'],
            'counts': [18000, 25000, 10905],  # Estimated
            'colors': ['#2ecc71', '#f39c12', '#e74c3c']
        },
        'Disease Resistance': {
            'classes': ['Resistant', 'Moderate', 'Susceptible'],
            'counts': [20000, 22000, 11905],  # Estimated
            'colors': ['#2ecc71', '#f39c12', '#e74c3c']
        },
        'Stress Tolerance': {
            'classes': ['High', 'Medium', 'Low'],
            'counts': [15000, 28000, 10905],  # Estimated
            'colors': ['#2ecc71', '#f39c12', '#e74c3c']
        }
    }
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    for idx, (trait, data) in enumerate(distributions.items()):
        ax = axes[idx]
        
        # Bar chart
        bars = ax.bar(data['classes'], data['counts'], color=data['colors'], alpha=0.8)
        
        # Add value labels and percentages
        total = sum(data['counts'])
        for bar, count in zip(bars, data['counts']):
            height = bar.get_height()
            percentage = (count / total) * 100
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(count):,}\n({percentage:.1f}%)',
                    ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        ax.set_ylabel('Number of Samples', fontsize=12, fontweight='bold')
        ax.set_title(f'📊 {trait}\nClass Distribution', fontsize=13, fontweight='bold')
        ax.set_ylim(0, max(data['counts']) * 1.15)
        
        # Add total annotation
        ax.text(0.5, 0.95, f'Total: {total:,} samples', 
                transform=ax.transAxes, ha='center', va='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                fontsize=10)
    
    plt.tight_layout()
    plt.savefig('class_distribution_per_trait.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: class_distribution_per_trait.png")
    plt.close()


# ============================================================================
# SECTION 2: CONFUSION MATRICES (Optional but Quick)
# ============================================================================

def plot_confusion_matrices_template():
    """
    Template for confusion matrices - replace with actual data if available
    """
    
    # EXAMPLE DATA - Replace with actual confusion matrices if available
    confusion_data = {
        'Yield': np.array([
            [9200, 600, 200],    # High: 92% correct
            [400, 8900, 700],    # Medium: 89% correct
            [100, 500, 9400]     # Low: 94% correct
        ]),
        'Disease Resistance': np.array([
            [8800, 900, 300],
            [500, 9200, 300],
            [200, 600, 9200]
        ]),
        'Stress Tolerance': np.array([
            [7000, 2500, 500],   # High: Only 70% - conservative!
            [300, 9200, 500],
            [100, 400, 9500]
        ])
    }
    
    classes = {
        'Yield': ['High', 'Medium', 'Low'],
        'Disease Resistance': ['Resistant', 'Moderate', 'Susceptible'],
        'Stress Tolerance': ['High', 'Medium', 'Low']
    }
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    for idx, (trait, matrix) in enumerate(confusion_data.items()):
        ax = axes[idx]
        
        # Normalize to percentages
        matrix_pct = matrix.astype('float') / matrix.sum(axis=1)[:, np.newaxis] * 100
        
        # Create heatmap
        sns.heatmap(matrix_pct, annot=True, fmt='.1f', cmap='RdYlGn', 
                   center=50, vmin=0, vmax=100, linewidths=1, ax=ax,
                   xticklabels=classes[trait], yticklabels=classes[trait],
                   cbar_kws={'label': 'Percentage (%)'})
        
        ax.set_title(f'🎯 {trait}\nConfusion Matrix (%)', fontsize=13, fontweight='bold')
        ax.set_ylabel('True Class', fontsize=11, fontweight='bold')
        ax.set_xlabel('Predicted Class', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('confusion_matrices_estimated.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: confusion_matrices_estimated.png")
    print("⚠️  Note: This uses ESTIMATED data - replace with actual confusion matrices for accuracy")
    plt.close()


# ============================================================================
# SECTION 3: ERROR ANALYSIS TEMPLATE
# ============================================================================

def create_error_analysis_template():
    """
    Create a template markdown file for documenting error analysis
    """
    
    template = """# 🔍 Error Analysis - AgriGenAI Models

## Overview
This document tracks misclassified samples to understand model weaknesses and guide improvements.

## Statistics
- Total Test Samples: 10,781
- Total Errors: ~770 (7.15%)
- Breakdown by Trait:
  - Yield: ~757 errors (7.02%)
  - Disease Resistance: ~779 errors (7.23%)
  - Stress Tolerance: ~775 errors (7.19%)

---

## 🔴 HIGH PRIORITY ERRORS (Fix First)

### Type 1: Diseased Plants Predicted as Healthy
**Impact:** HIGH - Dangerous for farmers
**Frequency:** ?
**Examples:**
- [ ] Image ID: ___ | True: Susceptible | Predicted: Resistant | Reason: ___

### Type 2: Healthy Plants Predicted as Diseased
**Impact:** MEDIUM - Causes unnecessary concern
**Frequency:** ?
**Examples:**
- [ ] Image ID: ___ | True: Resistant | Predicted: Susceptible | Reason: ___

---

## 🟡 MEDIUM PRIORITY ERRORS

### Type 3: High ↔ Medium Confusion (Yield)
**Impact:** MEDIUM
**Pattern:** Model conservative on "High" predictions (85% recall)
**Examples:**
- [ ] Image ID: ___ | True: High | Predicted: Medium | Reason: ___

### Type 4: High ↔ Medium Confusion (Stress Tolerance)
**Impact:** MEDIUM
**Pattern:** Model VERY conservative on "High" (70% recall)
**Examples:**
- [ ] Image ID: ___ | True: High | Predicted: Medium | Reason: ___

---

## 🟢 LOW PRIORITY ERRORS

### Type 5: Medium ↔ Low Confusion
**Impact:** LOW
**Frequency:** Rare
**Examples:**
- [ ] Image ID: ___ | True: Medium | Predicted: Low | Reason: ___

---

## 📊 ERROR PATTERNS IDENTIFIED

### Pattern 1: [Name]
**Description:** ___
**Frequency:** ___
**Root Cause:** ___
**Proposed Fix:** ___

### Pattern 2: [Name]
**Description:** ___
**Frequency:** ___
**Root Cause:** ___
**Proposed Fix:** ___

---

## 💡 RECOMMENDATIONS FOR V2.0

### Data Collection
1. [ ] Collect more severely diseased/dead plant images (current weakness)
2. [ ] Add more "High stress tolerance" samples (70% recall)
3. [ ] Balance class distribution if needed

### Model Improvements
1. [ ] Implement stronger visual disease detection
2. [ ] Add confidence scoring
3. [ ] Ensemble with specialized disease model

### System Improvements
1. [ ] Add user feedback loop
2. [ ] Flag low-confidence predictions for review
3. [ ] A/B test new model vs current

---

## 📝 SAMPLE ANALYSIS (To Be Filled)

### Sample Error 1
- **Image:** [image_path]
- **True Labels:** Yield=High, Disease=Resistant, Stress=High
- **Predicted:** Yield=Medium, Disease=Resistant, Stress=Medium
- **Visual Analysis:** [describe what you see]
- **Possible Reason:** [lighting/angle/disease present/etc]
- **Fix Priority:** [High/Medium/Low]

### Sample Error 2
...

---

## 🎯 NEXT STEPS

1. [ ] Run model on test set and save misclassified image IDs
2. [ ] Manually review 50 random errors
3. [ ] Categorize errors by type
4. [ ] Identify top 3 error patterns
5. [ ] Create action plan for v2.0
6. [ ] Track metrics after fixes deployed

---

Last Updated: [Date]
Analyzed By: [Name]
"""
    
    with open('error_analysis_template.md', 'w', encoding='utf-8') as f:
        f.write(template)
    
    print("✅ Saved: error_analysis_template.md")
    print("   Use this to document misclassified samples after deployment")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("🚀 Generating Additional Visualizations...\n")
    
    try:
        print("📊 [1/3] Creating class distribution chart...")
        plot_class_distribution()
        
        print("📊 [2/3] Creating confusion matrices (estimated)...")
        plot_confusion_matrices_template()
        
        print("📝 [3/3] Creating error analysis template...")
        create_error_analysis_template()
        
        print("\n" + "="*80)
        print("✅ ALL ADDITIONAL VISUALIZATIONS GENERATED!")
        print("="*80)
        print("\n📁 Generated Files:")
        print("   1. class_distribution_per_trait.png")
        print("   2. confusion_matrices_estimated.png (optional)")
        print("   3. error_analysis_template.md (for future use)")
        
        print("\n💡 NOTES:")
        print("   • Class distribution uses ESTIMATED data")
        print("   • Confusion matrices use ESTIMATED data")
        print("   • Replace with actual data from your training for accuracy")
        print("   • Error analysis template is for documenting issues after deployment")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()