"""
Flask Web Application for Student DSS
Provides form-based input and dashboard views
"""

from flask import Flask, render_template, request, redirect, url_for
import sys
import os

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# Import your existing engine
from engine.dss_engine import StudentDSS

app = Flask(__name__)

# Initialize DSS with your data
data_path = os.path.join(project_root, 'data', 'student-mat.csv')
dss = StudentDSS(data_path)
dss.load_data()

# ========== HELPER FUNCTION ==========

def evaluate_student(form_data):
    """
    Convert form data to format your expert system expects
    
    Args:
        form_data: Dict from the form with keys like 'absences', 'G2', etc.
        
    Returns:
        Dict with risk analysis results
    """
    # Create a pseudo-student row (mimicking DataFrame row)
    import pandas as pd
    
    # Build complete student data with defaults
    student_row = pd.Series({
        'G1': int(form_data.get('G1', 0)),
        'G2': int(form_data.get('G2', 0)),
        'G3': int(form_data.get('G3', 0)),  # Optional
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
    })
    
    # Import your evaluation function
    from logic.desicion_rules import evaluate_risk
    
    # Run through expert system
    risk_level, recommendations, risk_scores = evaluate_risk(student_row)
    
    # Calculate probability (simple conversion from score)
    total_score = sum(risk_scores.values())
    # Convert to probability (higher score = higher failure probability)
    # Scale: 0-15 score range to 0-1 probability
    probability = min(total_score / 15.0, 1.0)
    
    return {
        'level': risk_level,
        'score': total_score,
        'probability': probability,
        'recommendations': recommendations,
        'risk_scores': risk_scores,
        'student_data': student_row.to_dict()
    }

# ========== ROUTES ==========

@app.route("/")
def home():
    """Landing page with input form"""
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    """Process form submission and show results"""
    try:
        # Get form data
        form_data = request.form.to_dict()
        
        # Run evaluation
        result = evaluate_student(form_data)
        
        return render_template(
            "results.html",
            level=result["level"],
            score=result["score"],
            probability=round(result["probability"] * 100, 2),
            recommendations=result["recommendations"],
            risk_scores=result["risk_scores"],
            student_data=result["student_data"]
        )
    
    except Exception as e:
        return render_template(
            "error.html",
            message=f"Error analyzing student: {str(e)}"
        )

@app.route("/dashboard")
def dashboard():
    """Dashboard showing all students (your existing view)"""
    stats = dss.get_summary_statistics()
    at_risk = dss.get_at_risk_students()[:10]
    
    return render_template(
        'dashboard.html',
        stats=stats,
        at_risk=at_risk
    )

@app.route("/student/<int:index>")
def student_detail(index):
    """Individual student from dataset (your existing view)"""
    result = dss.analyze_student(index)
    
    if result is None:
        return render_template(
            "error.html",
            message="Student not found"
        )
    
    return render_template('student_detail.html', student=result)

@app.route("/at-risk")
def at_risk_list():
    """List all at-risk students from dataset"""
    at_risk = dss.get_at_risk_students()
    return render_template('at_risk.html', students=at_risk)

# ========== RUN APP ==========

if __name__ == "__main__":
    print("\n🚀 Starting Student DSS Web Interface...")
    print("📊 Access at:")
    print("   - Form input: http://localhost:5000")
    print("   - Dashboard: http://localhost:5000/dashboard")
    print("=" * 50 + "\n")
    app.run(debug=True, port=5000)