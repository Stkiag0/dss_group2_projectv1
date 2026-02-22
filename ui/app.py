"""
Flask Web Application for Student DSS
Supports both pure rule-based and hybrid ML modes
"""

from flask import Flask, render_template, request, redirect, url_for, flash
import sys
import os
import pandas as pd

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# ============================
# CONFIGURATION
# ============================

# Toggle between pure rules and hybrid ML
USE_HYBRID_ML = True  # Set to False for pure rule-based mode

# ============================
# IMPORTS BASED ON MODE
# ============================

if USE_HYBRID_ML:
    from engine.dss_engine_hybrid import HybridStudentDSS
    print("🤖 MODE: Hybrid ML + Rules")
else:
    from engine.dss_engine import StudentDSS
    from logic.experta_rules import evaluate_risk
    print("📋 MODE: Pure Rule-Based (Experta)")

# ============================
# FLASK APP SETUP
# ============================

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

# Initialize DSS
data_path = os.path.join(project_root, 'data', 'student-mat.csv')

if USE_HYBRID_ML:
    print("\n🤖 Initializing Hybrid DSS...")
    dss = HybridStudentDSS(data_path)
    
    # Load data
    if not dss.load_data():
        print("❌ Failed to load data. Exiting.")
        sys.exit(1)
    
    # Load or train model
    if not dss._load_model():
        print("📊 No existing model found. Training new model...")
        dss.train_model()
    
    # Run full analysis pipeline to populate all columns
    print("🔄 Running initial analysis...")
    dss.apply_rules()
    dss.apply_ml_predictions()
    dss.hybrid_decision()
    dss.generate_recommendations()
    print("✅ Initial analysis complete")
    
else:
    print("\n📋 Initializing Rule-Based DSS...")
    dss = StudentDSS(data_path)
    if not dss.load_data():
        print("❌ Failed to load data. Exiting.")
        sys.exit(1)
# ============================
# HELPER FUNCTIONS
# ============================

def evaluate_student_form(form_data):
    """
    Analyze student from web form submission
    Handles both hybrid ML and pure rule modes
    
    Args:
        form_data: dict from Flask request.form
        
    Returns:
        dict with analysis results
    """
    # Build student data dictionary
    student_data = {
        'G1': int(form_data.get('G1', 0)),
        'G2': int(form_data.get('G2', 0)),
        'absences': int(form_data.get('absences', 0)),
        'studytime': int(form_data.get('studytime', 2)),
        'failures': int(form_data.get('failures', 0)),
        'famsup': form_data.get('famsup', 'yes'),
        'Medu': int(form_data.get('Medu', 2)),
        'Fedu': int(form_data.get('Fedu', 2)),
        'Dalc': int(form_data.get('Dalc', 1)),
        'Walc': int(form_data.get('Walc', 1)),
        'goout': int(form_data.get('goout', 2)),
        'health': int(form_data.get('health', 3)),
        'internet': form_data.get('internet', 'yes')
    }
    
    if USE_HYBRID_ML:
        # Hybrid ML mode
        result = dss.predict_single(student_data)
        
        return {
            'level': result['final_level'],
            'score': result['rule_score'],
            'probability': result['ml_probability'],
            'recommendations': result['recommendations'],
            'risk_scores': result['breakdown'],
            'student_data': student_data,
            'mode': 'hybrid',
            'ml_available': result['ml_available']
        }
    else:
        # Pure rule-based mode
        student_row = pd.Series(student_data)
        risk_level, recommendations, risk_scores = evaluate_risk(student_row)
        
        total_score = sum(risk_scores.values())
        probability = min(total_score / 15.0, 1.0)
        
        return {
            'level': risk_level,
            'score': total_score,
            'probability': probability,
            'recommendations': recommendations,
            'risk_scores': risk_scores,
            'student_data': student_data,
            'mode': 'rules',
            'ml_available': False
        }

# ============================
# ROUTES
# ============================

@app.route("/")
def home():
    """Landing page with input form"""
    return render_template(
        "index.html", 
        mode='hybrid' if USE_HYBRID_ML else 'rules',
        ml_enabled=USE_HYBRID_ML
    )

@app.route("/predict", methods=["POST"])
def predict():
    """Process form submission and show results"""
    try:
        # Get form data
        form_data = request.form.to_dict()
        
        # Run evaluation
        result = evaluate_student_form(form_data)
        
        return render_template(
            "results.html",
            level=result["level"],
            score=result["score"],
            probability=round(result["probability"] * 100, 2),
            recommendations=result["recommendations"],
            risk_scores=result["risk_scores"],
            student_data=result["student_data"],
            mode=result.get('mode', 'rules'),
            ml_available=result.get('ml_available', False)
        )
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return render_template(
            "error.html",
            message=f"Error analyzing student: {str(e)}"
        )

@app.route("/dashboard")
def dashboard():
    """Dashboard showing overall statistics"""
    try:
        if USE_HYBRID_ML:
            stats = dss.get_summary_statistics()
            at_risk_df = dss.get_at_risk_students()
            at_risk = at_risk_df.head(10).to_dict('records') if not at_risk_df.empty else []
        else:
            stats = dss.get_summary_statistics()
            at_risk = dss.get_at_risk_students()[:10]
        
        return render_template(
            'dashboard.html',
            stats=stats,
            at_risk=at_risk,
            mode='hybrid' if USE_HYBRID_ML else 'rules'
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return render_template(
            "error.html",
            message=f"Dashboard error: {str(e)}"
        )

@app.route("/student/<int:index>")
def student_detail(index):
    """Individual student detail page"""
    try:
        if USE_HYBRID_ML:
            # Get student from dataframe
            if index >= len(dss.data):
                return render_template("error.html", message="Student not found")
            
            student_row = dss.data.iloc[index]
            student_dict = student_row.to_dict()
            
            result = {
                'index': index,
                'risk_level': student_dict.get('FinalRiskLevel', 'Unknown'),
                'total_risk_score': student_dict.get('RiskScore', 0),
                'ml_probability': student_dict.get('ML_Risk_Probability', 0),
                'data': student_dict,
                'recommendations': student_dict.get('Recommendations', [])
            }
        else:
            result = dss.analyze_student(index)
            if result is None:
                return render_template("error.html", message="Student not found")
        
        return render_template('student_detail.html', student=result)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return render_template(
            "error.html",
            message=f"Error loading student: {str(e)}"
        )

@app.route("/at-risk")
def at_risk_list():
    """List all at-risk students"""
    try:
        if USE_HYBRID_ML:
            at_risk_df = dss.get_at_risk_students()
            students = []
            for idx, row in at_risk_df.iterrows():
                students.append({
                    'index': idx,
                    'risk_level': row['FinalRiskLevel'],
                    'total_risk_score': row['RiskScore'],
                    'G2': row.get('G2', 'N/A'),
                    'absences': row.get('absences', 'N/A')
                })
        else:
            students = dss.get_at_risk_students()
        
        return render_template('at_risk.html', students=students)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return render_template(
            "error.html",
            message=f"Error loading at-risk list: {str(e)}"
        )

@app.route("/about")
def about():
    """About page explaining the system"""
    return render_template("about.html", mode='hybrid' if USE_HYBRID_ML else 'rules')

# ============================
# ERROR HANDLERS
# ============================

@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", message="Page not found"), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template("error.html", message="Internal server error"), 500

# ============================
# RUN APPLICATION
# ============================

if __name__ == "__main__":
    mode_name = "Hybrid ML + Rules" if USE_HYBRID_ML else "Pure Rule-Based"
    
    print("\n" + "="*60)
    print("🚀 Student DSS Web Interface")
    print("="*60)
    print(f"📊 Mode: {mode_name}")
    print(f"🌐 Access at: http://localhost:5000")
    print("\nAvailable routes:")
    print("  - /           Form input")
    print("  - /dashboard  Overall statistics")
    print("  - /at-risk    At-risk student list")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000, host='0.0.0.0')