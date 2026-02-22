"""
Unit tests for Hybrid DSS
"""

import sys
import os
import pandas as pd

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from logic.decision_rules import (
    compute_total_risk,
    classify_risk,
    recommend_intervention
)
from engine.dss_engine_hybrid import HybridStudentDSS


def test_rule_scoring():
    """Test rule-based scoring functions"""
    print("\n=== Testing Rule-Based Scoring ===")
    
    # High risk student
    high_risk_student = {
        'G2': 5,
        'absences': 20,
        'failures': 3,
        'studytime': 1,
        'famsup': 'no',
        'Medu': 1,
        'Fedu': 1,
        'Dalc': 5,
        'Walc': 5,
        'goout': 5
    }
    
    score = compute_total_risk(high_risk_student)
    level = classify_risk(score)
    
    print(f"High-risk student score: {score}")
    print(f"Classification: {level}")
    assert score >= 8, f"Expected score >= 8, got {score}"
    assert level == "High Risk", f"Expected 'High Risk', got '{level}'"
    print("✓ High-risk test passed")
    
    # Low risk student
    low_risk_student = {
        'G2': 18,
        'absences': 0,
        'failures': 0,
        'studytime': 4,
        'famsup': 'yes',
        'Medu': 4,
        'Fedu': 4,
        'Dalc': 1,
        'Walc': 1,
        'goout': 2
    }
    
    score = compute_total_risk(low_risk_student)
    level = classify_risk(score)
    
    print(f"\nLow-risk student score: {score}")
    print(f"Classification: {level}")
    assert score < 4, f"Expected score < 4, got {score}"
    assert level == "Low Risk", f"Expected 'Low Risk', got '{level}'"
    print("✓ Low-risk test passed")


def test_recommendations():
    """Test recommendation generation"""
    print("\n=== Testing Recommendations ===")
    
    student = {
        'G2': 8,
        'absences': 12,
        'failures': 2,
        'studytime': 1,
        'famsup': 'no'
    }
    
    recs = recommend_intervention(student, "Moderate Risk")
    
    print(f"Recommendations generated: {len(recs)}")
    for rec in recs:
        print(f"  - {rec}")
    
    assert len(recs) > 0, "Expected at least one recommendation"
    print("✓ Recommendation test passed")


def test_hybrid_dss():
    """Test hybrid DSS pipeline"""
    print("\n=== Testing Hybrid DSS ===")
    
    # Create test data
    test_data = pd.DataFrame({
        'G1': [10, 15, 8, 18, 6],
        'G2': [9, 14, 7, 17, 5],
        'G3': [8, 15, 9, 18, 7],
        'absences': [10, 2, 15, 0, 20],
        'failures': [1, 0, 2, 0, 3],
        'studytime': [2, 3, 1, 4, 1],
        'famsup': ['yes', 'yes', 'no', 'yes', 'no'],
        'Medu': [2, 4, 1, 4, 1],
        'Fedu': [2, 4, 1, 4, 1],
        'Dalc': [1, 1, 3, 1, 5],
        'Walc': [2, 1, 4, 1, 5],
        'goout': [3, 2, 4, 2, 5]
    })
    
    # Save test data
    test_path = os.path.join(project_root, 'data', 'test_data.csv')
    test_data.to_csv(test_path, index=False)
    
    # Initialize DSS
    dss = HybridStudentDSS(test_path)
    
    # Run pipeline
    results = dss.run(train_new_model=True)
    
    assert results is not None, "DSS run failed"
    assert 'FinalRiskLevel' in results.columns, "Missing FinalRiskLevel column"
    assert len(results) == 5, f"Expected 5 results, got {len(results)}"
    
    print(f"✓ Processed {len(results)} students successfully")
    
    # Test single prediction
    print("\n=== Testing Single Prediction ===")
    
    test_student = {
        'G1': 8,
        'G2': 7,
        'absences': 15,
        'failures': 2,
        'studytime': 1,
        'famsup': 'no',
        'Medu': 2,
        'Fedu': 2,
        'Dalc': 3,
        'Walc': 4,
        'goout': 4
    }
    
    prediction = dss.predict_single(test_student)
    
    print(f"Rule Score: {prediction['rule_score']}")
    print(f"ML Probability: {prediction['ml_probability']:.2%}")
    print(f"Final Level: {prediction['final_level']}")
    print(f"Recommendations: {len(prediction['recommendations'])}")
    
    assert 'final_level' in prediction, "Missing final_level in prediction"
    assert prediction['final_level'] in ['High Risk', 'Moderate Risk', 'Low Risk']
    
    print("✓ Single prediction test passed")
    
    # Cleanup
    os.remove(test_path)
    print("\n✓ All hybrid DSS tests passed")


if __name__ == "__main__":
    print("="*60)
    print("Running Hybrid DSS Tests")
    print("="*60)
    
    try:
        test_rule_scoring()
        test_recommendations()
        test_hybrid_dss()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60)
    
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()