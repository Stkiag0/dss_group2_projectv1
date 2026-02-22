"""
Hybrid DSS Engine: Combines Rule-Based + Machine Learning
"""

import pandas as pd
import pickle
import os
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import sys

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from logic.decision_rules import (
    compute_total_risk,
    classify_risk,
    recommend_intervention,
)


class HybridStudentDSS:
    """
    Hybrid Decision Support System
    Combines traditional rule-based reasoning with machine learning
    """
    
    def __init__(self, dataset_path, model_path=None):
        """
        Initialize Hybrid DSS
        
        Args:
            dataset_path: Path to CSV file with student data
            model_path: Path to save/load trained model (optional)
        """
        self.dataset_path = dataset_path
        self.model_path = model_path or os.path.join(project_root, 'models', 'trained_model.pkl')
        self.data = None
        self.model = None
        self.model_trained = False
    
    # ============================
    # DATA LOADING
    # ============================
    
    def load_data(self):
        """Load dataset from CSV file"""
        try:
            # Try semicolon separator first (common in European datasets)
            self.data = pd.read_csv(self.dataset_path, sep=';')
            print(f"✓ Loaded {len(self.data)} student records (sep=';')")
            return True
        except:
            try:
                # Fallback to comma separator
                self.data = pd.read_csv(self.dataset_path)
                print(f"✓ Loaded {len(self.data)} student records (sep=',')")
                return True
            except Exception as e:
                print(f"✗ Error loading data: {e}")
                return False
    
    # ============================
    # MACHINE LEARNING MODEL
    # ============================
    
    def train_model(self, test_size=0.2):
        """
        Train logistic regression model
        Predicts probability of failure (G3 < 10)
        
        Args:
            test_size: Proportion of data to use for testing
        """
        print("\n📊 Training ML model...")
        
        # Check if G3 column exists
        if 'G3' not in self.data.columns:
            print("⚠️ Warning: G3 column not found. ML predictions disabled.")
            print("   ML requires final grades to train. Using rules only.")
            return False
        
        # Define features
        required_features = ["failures", "absences", "studytime", "G1", "G2"]
        
        # Check all features exist
        missing = [f for f in required_features if f not in self.data.columns]
        if missing:
            print(f"⚠️ Warning: Missing features {missing}. ML predictions disabled.")
            return False
        
        # Prepare data
        X = self.data[required_features].copy()
        
        # Handle missing values
        X = X.fillna(X.median())
        
        # Create target: at risk if final grade < 10
        y = (self.data["G3"] < 10).astype(int)
        
        # Train model
        self.model = LogisticRegression(max_iter=1000, random_state=42)
        self.model.fit(X, y)
        
        # Calculate accuracy
        y_pred = self.model.predict(X)
        accuracy = accuracy_score(y, y_pred)
        
        print(f"✓ Model trained successfully")
        print(f"  Accuracy: {accuracy:.2%}")
        print(f"  Features used: {', '.join(required_features)}")
        
        # Show class distribution
        at_risk_count = y.sum()
        not_at_risk_count = len(y) - at_risk_count
        print(f"  Training data: {at_risk_count} at-risk, {not_at_risk_count} not at-risk")
        
        # Save model
        self._save_model()
        self.model_trained = True
        
        return True
    
    def _save_model(self):
        """Save trained model to disk"""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.model, f)
            print(f"✓ Model saved to {self.model_path}")
        except Exception as e:
            print(f"⚠️ Could not save model: {e}")
    
    def _load_model(self):
        """Load pre-trained model from disk"""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                print(f"✓ Loaded pre-trained model from {self.model_path}")
                self.model_trained = True
                return True
            except Exception as e:
                print(f"⚠️ Could not load model: {e}")
                return False
        return False
    
    # ============================
    # RULE-BASED ANALYSIS
    # ============================
    
    def apply_rules(self):
        """Apply traditional rule-based risk scoring"""
        print("\n📋 Applying rule-based analysis...")
        
        self.data["RiskScore"] = self.data.apply(compute_total_risk, axis=1)
        self.data["RiskLevel"] = self.data["RiskScore"].apply(classify_risk)
        
        # Show distribution
        rule_dist = self.data["RiskLevel"].value_counts()
        print("✓ Rules applied")
        print("  Rule-based distribution:")
        for level, count in rule_dist.items():
            pct = (count / len(self.data)) * 100
            print(f"    {level}: {count} ({pct:.1f}%)")
    
    # ============================
    # ML PREDICTIONS
    # ============================
    
    def apply_ml_predictions(self):
        """Generate ML-based risk probabilities"""
        if self.model is None or not self.model_trained:
            print("⚠️ No ML model available. Skipping ML predictions.")
            self.data["ML_Risk_Probability"] = 0.0
            return
        
        print("\n🤖 Generating ML predictions...")
        
        features = ["failures", "absences", "studytime", "G1", "G2"]
        
        try:
            X = self.data[features].fillna(self.data[features].median())
            probs = self.model.predict_proba(X)[:, 1]
            self.data["ML_Risk_Probability"] = probs
            
            # Show distribution
            high_ml_risk = (probs > 0.65).sum()
            mod_ml_risk = ((probs > 0.4) & (probs <= 0.65)).sum()
            low_ml_risk = (probs <= 0.4).sum()
            
            print("✓ ML predictions generated")
            print("  ML-based distribution:")
            print(f"    High probability (>65%): {high_ml_risk}")
            print(f"    Moderate probability (40-65%): {mod_ml_risk}")
            print(f"    Low probability (<40%): {low_ml_risk}")
            
        except Exception as e:
            print(f"⚠️ ML prediction error: {e}")
            self.data["ML_Risk_Probability"] = 0.0
    
    # ============================
    # HYBRID DECISION LOGIC
    # ============================
    
    def hybrid_decision(self):
        """
        Combine rule-based and ML predictions
        
        Decision Logic:
        - High Risk if: ML probability > 0.65 OR rule score >= 8
        - Moderate Risk if: ML probability > 0.4 OR rule score >= 4
        - Low Risk: Otherwise
        
        This OR logic ensures we catch students flagged by either system
        """
        print("\n🔄 Combining rule-based + ML decisions...")
        
        def combine(row):
            ml_prob = row.get("ML_Risk_Probability", 0)
            rule_score = row["RiskScore"]
            
            # High risk if EITHER system flags as high
            if ml_prob > 0.65 or rule_score >= 8:
                return "High Risk"
            # Moderate risk if EITHER system flags as moderate
            elif ml_prob > 0.4 or rule_score >= 4:
                return "Moderate Risk"
            # Otherwise low risk
            return "Low Risk"
        
        self.data["FinalRiskLevel"] = self.data.apply(combine, axis=1)
        
        # Show distribution
        final_dist = self.data["FinalRiskLevel"].value_counts()
        print("✓ Hybrid decisions complete")
        print("  Final hybrid distribution:")
        for level, count in final_dist.items():
            pct = (count / len(self.data)) * 100
            print(f"    {level}: {count} ({pct:.1f}%)")
        
        # Show how many were changed by hybrid approach
        if self.model_trained:
            changed = (self.data["RiskLevel"] != self.data["FinalRiskLevel"]).sum()
            print(f"  Classifications changed by ML: {changed}")
    
    # ============================
    # RECOMMENDATIONS
    # ============================
    
    def generate_recommendations(self):
        """Generate personalized intervention recommendations"""
        print("\n💡 Generating recommendations...")
        
        def get_recs(row):
            recs = recommend_intervention(row, row["FinalRiskLevel"])
            
            # Add ML-specific note if high ML probability
            ml_prob = row.get("ML_Risk_Probability", 0)
            if ml_prob > 0.7:
                recs.append(f"🤖 ML model predicts {ml_prob*100:.1f}% failure probability - close monitoring advised")
            
            return recs
        
        self.data["Recommendations"] = self.data.apply(get_recs, axis=1)
        print("✓ Recommendations generated")
    
    # ============================
    # SINGLE STUDENT PREDICTION
    # ============================
    
    def predict_single(self, student_data):
        """
        Predict risk for a single student (for web form input)
        
        Args:
            student_data: dict with student attributes
                Required keys: G1, G2, absences, studytime, failures
                Optional: famsup, Medu, Fedu, Dalc, Walc, goout
            
        Returns:
            dict with complete analysis results
        """
        # Rule-based score
        rule_score = compute_total_risk(student_data)
        rule_level = classify_risk(rule_score)
        
        # ML prediction (if model available)
        ml_prob = 0.0
        ml_available = False
        
        if self.model is not None and self.model_trained:
            features = ["failures", "absences", "studytime", "G1", "G2"]
            try:
                # Create feature vector
                X = pd.DataFrame([{
                    'failures': student_data.get('failures', 0),
                    'absences': student_data.get('absences', 0),
                    'studytime': student_data.get('studytime', 2),
                    'G1': student_data.get('G1', 0),
                    'G2': student_data.get('G2', 0)
                }])
                
                ml_prob = self.model.predict_proba(X)[0, 1]
                ml_available = True
            except Exception as e:
                print(f"⚠️ ML prediction error: {e}")
                ml_prob = 0.0
        
        # Hybrid decision
        if ml_prob > 0.65 or rule_score >= 8:
            final_level = "High Risk"
        elif ml_prob > 0.4 or rule_score >= 4:
            final_level = "Moderate Risk"
        else:
            final_level = "Low Risk"
        
        # Recommendations
        recommendations = recommend_intervention(student_data, final_level)
        
        # Add ML note if applicable
        if ml_available and ml_prob > 0.7:
            recommendations.append(f"🤖 ML model predicts {ml_prob*100:.1f}% failure probability")
        
        return {
            'rule_score': rule_score,
            'rule_level': rule_level,
            'ml_probability': ml_prob,
            'ml_available': ml_available,
            'final_level': final_level,
            'recommendations': recommendations,
            'breakdown': {
                'Rule Score': rule_score,
                'ML Probability': round(ml_prob * 100, 1) if ml_available else 'N/A'
            }
        }
    
    # ============================
    # FULL PIPELINE
    # ============================
    
    def run(self, train_new_model=False):
        """
        Run complete hybrid DSS pipeline
        
        Args:
            train_new_model: bool
                If True, trains new model
                If False, tries to load existing model first
        
        Returns:
            DataFrame with complete analysis results
        """
        print("\n" + "="*70)
        print("🚀 HYBRID STUDENT DSS - FULL ANALYSIS PIPELINE")
        print("="*70)
        
        # Step 1: Load data
        if not self.load_data():
            print("❌ Failed to load data. Exiting.")
            return None
        
        # Step 2: ML model setup
        if train_new_model:
            print("\n🎓 Training new ML model...")
            self.train_model()
        else:
            print("\n🔍 Looking for existing model...")
            if not self._load_model():
                print("   No existing model found. Training new model...")
                self.train_model()
        
        # Step 3: Apply rule-based analysis
        self.apply_rules()
        
        # Step 4: Apply ML predictions
        self.apply_ml_predictions()
        
        # Step 5: Hybrid decision
        self.hybrid_decision()
        
        # Step 6: Generate recommendations
        self.generate_recommendations()
        
        print("\n" + "="*70)
        print("✅ HYBRID ANALYSIS COMPLETE")
        print("="*70)
        
        return self.data
    
    # ============================
    # RESULTS EXPORT
    # ============================
    
    def save_results(self, output_path='hybrid_dss_results.csv'):
        """
        Save analysis results to CSV
        
        Args:
            output_path: Path for output CSV file
        """
        if self.data is None:
            print("⚠️ No data to save. Run analysis first.")
            return
        
        # Define columns to export
        base_cols = ['G1', 'G2', 'absences', 'failures', 'studytime', 
                     'famsup', 'Medu', 'Fedu']
        analysis_cols = ['RiskScore', 'RiskLevel', 'ML_Risk_Probability', 
                        'FinalRiskLevel', 'Recommendations']
        
        # Include G3 if available
        if 'G3' in self.data.columns:
            base_cols.insert(2, 'G3')
        
        # Filter to existing columns
        all_cols = base_cols + analysis_cols
        existing_cols = [c for c in all_cols if c in self.data.columns]
        
        # Convert recommendations list to string
        export_data = self.data[existing_cols].copy()
        if 'Recommendations' in export_data.columns:
            export_data['Recommendations'] = export_data['Recommendations'].apply(
                lambda x: ' | '.join(x) if isinstance(x, list) else str(x)
            )
        
        # Save
        export_data.to_csv(output_path, index=False)
        print(f"\n✓ Results saved to {output_path}")
        print(f"  Exported {len(export_data)} records with {len(existing_cols)} columns")
    
    def get_at_risk_students(self):
        """
        Get list of students requiring intervention
        
        Returns:
            DataFrame of high and moderate risk students, sorted by severity
        """
        if self.data is None:
            return pd.DataFrame()
        
        # Filter for at-risk students
        at_risk = self.data[
            self.data['FinalRiskLevel'].isin(['High Risk', 'Moderate Risk'])
        ].copy()
        
        # Sort by risk (High first, then by score)
        at_risk['_sort_key'] = at_risk.apply(
            lambda row: (0 if row['FinalRiskLevel'] == 'High Risk' else 1, 
                        -row['RiskScore']), 
            axis=1
        )
        at_risk = at_risk.sort_values('_sort_key').drop('_sort_key', axis=1)
        
        return at_risk
    
    def get_summary_statistics(self):
        """
        Get summary statistics of risk distribution
        
        Returns:
            dict with summary metrics
        """
        if self.data is None:
            return {}
        
        total = len(self.data)
        
        # Count by final risk level
        high = (self.data['FinalRiskLevel'] == 'High Risk').sum()
        moderate = (self.data['FinalRiskLevel'] == 'Moderate Risk').sum()
        low = (self.data['FinalRiskLevel'] == 'Low Risk').sum()
        
        return {
            'total_students': total,
            'high_risk': int(high),
            'moderate_risk': int(moderate),
            'low_risk': int(low),
            'high_risk_pct': round((high / total) * 100, 1) if total > 0 else 0,
            'moderate_risk_pct': round((moderate / total) * 100, 1) if total > 0 else 0,
            'low_risk_pct': round((low / total) * 100, 1) if total > 0 else 0,
            'ml_enabled': self.model_trained
        }


# ============================
# COMMAND LINE INTERFACE
# ============================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("HYBRID STUDENT DSS - Command Line Tool")
    print("="*70)
    
    # Setup paths
    data_path = os.path.join(project_root, 'data', 'student-mat.csv')
    
    # Check if data file exists
    if not os.path.exists(data_path):
        print(f"\n❌ Error: Data file not found at {data_path}")
        print("   Please ensure student-mat.csv is in the data/ folder")
        sys.exit(1)
    
    # Initialize DSS
    dss = HybridStudentDSS(data_path)
    
    # Run full analysis
    # Set train_new_model=True to retrain, False to use existing model
    results = dss.run(train_new_model=True)
    
    if results is not None:
        # Save results
        dss.save_results()
        
        # Show sample of high-risk students
        at_risk = dss.get_at_risk_students()
        
        print("\n" + "="*70)
        print(f"📊 TOP 10 AT-RISK STUDENTS (out of {len(at_risk)} total)")
        print("="*70)
        
        for idx, (_, student) in enumerate(at_risk.head(10).iterrows(), 1):
            print(f"\n{idx}. Student (Row {student.name})")
            print(f"   Final Risk: {student['FinalRiskLevel']}")
            print(f"   Rule Score: {student['RiskScore']}/15")
            if dss.model_trained:
                print(f"   ML Probability: {student['ML_Risk_Probability']*100:.1f}%")
            print(f"   G2 Grade: {student['G2']}")
            print(f"   Absences: {student['absences']}")
            print(f"   Recommendations:")
            for rec in student['Recommendations']:
                print(f"      - {rec}")
        
        # Summary statistics
        stats = dss.get_summary_statistics()
        print("\n" + "="*70)
        print("📈 SUMMARY STATISTICS")
        print("="*70)
        print(f"Total Students: {stats['total_students']}")
        print(f"High Risk: {stats['high_risk']} ({stats['high_risk_pct']}%)")
        print(f"Moderate Risk: {stats['moderate_risk']} ({stats['moderate_risk_pct']}%)")
        print(f"Low Risk: {stats['low_risk']} ({stats['low_risk_pct']}%)")
        print(f"ML Model: {'Enabled' if stats['ml_enabled'] else 'Disabled'}")
        print("="*70)