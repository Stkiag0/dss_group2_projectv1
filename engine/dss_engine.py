"""
DSS Engine - Processes student data and generates risk assessments
"""

import pandas as pd
import sys
import os

current_file = os.path.abspath(__file__)
engine_dir = os.path.dirname(current_file)
project_root = os.path.dirname(engine_dir)

# Add parent directory to path
sys.path.insert(0, project_root)

print(f"Debug: Project root = {project_root}")
print(f"Debug: Looking for logic folder at: {os.path.join(project_root, 'logic')}")

from logic.desicion_rules import evaluate_risk

class StudentDSS:
    def __init__(self, data_path):
        self.data_path = data_path
        self.students_df = None
        
    def load_data(self):
        """Load student data from CSV"""
        try:
            # Try semicolon separator first
            self.students_df = pd.read_csv(self.data_path, sep=';')
            print(f"✓ Loaded {len(self.students_df)} student records")
            return True
        except:
            try:
                # Try comma separator
                self.students_df = pd.read_csv(self.data_path)
                print(f"✓ Loaded {len(self.students_df)} student records")
                return True
            except Exception as e:
                print(f"✗ Error loading data: {e}")
                return False
    
    def analyze_student(self, student_index):
        """
        Analyze a single student
        
        Args:
            student_index: Row index of student
            
        Returns:
            dict: Analysis results
        """
        if student_index >= len(self.students_df):
            return None
        
        # Get student data
        student_row = self.students_df.iloc[student_index]
        
        # Run through expert system
        risk_level, recommendations, risk_scores = evaluate_risk(student_row)
        
        # Calculate total risk score
        total_risk_score = sum(risk_scores.values())
        
        return {
            'index': student_index,
            'G1': student_row['G1'],
            'G2': student_row['G2'],
            'G3': student_row.get('G3', 'N/A'),
            'absences': student_row['absences'],
            'studytime': student_row['studytime'],
            'failures': student_row['failures'],
            'famsup': student_row['famsup'],
            'risk_scores': risk_scores,
            'total_risk_score': total_risk_score,
            'risk_level': risk_level,
            'recommendations': recommendations
        }
    
    def analyze_all_students(self):
        """Analyze all students and return results"""
        results = []
        
        for idx in range(len(self.students_df)):
            analysis = self.analyze_student(idx)
            if analysis:
                results.append(analysis)
        
        return results
    
    def get_at_risk_students(self):
        """Get students who need intervention (High or Moderate risk)"""
        all_results = self.analyze_all_students()
        
        # Filter for high and moderate risk
        at_risk = [
            student for student in all_results 
            if student['risk_level'] in ['High Risk', 'Moderate Risk']
        ]
        
        # Sort by total risk score (highest first)
        at_risk.sort(key=lambda x: x['total_risk_score'], reverse=True)
        
        return at_risk
    
    def get_summary_statistics(self):
        """Get summary statistics of risk distribution"""
        all_results = self.analyze_all_students()
        
        total = len(all_results)
        high_risk = len([s for s in all_results if s['risk_level'] == 'High Risk'])
        moderate_risk = len([s for s in all_results if s['risk_level'] == 'Moderate Risk'])
        low_risk = len([s for s in all_results if s['risk_level'] == 'Low Risk'])
        
        return {
            'total_students': total,
            'high_risk': high_risk,
            'moderate_risk': moderate_risk,
            'low_risk': low_risk,
            'high_risk_pct': round((high_risk / total) * 100, 1) if total > 0 else 0,
            'moderate_risk_pct': round((moderate_risk / total) * 100, 1) if total > 0 else 0,
            'low_risk_pct': round((low_risk / total) * 100, 1) if total > 0 else 0
        }
    
    def save_results(self, output_path='student_risk_results.csv'):
        """Save analysis results to CSV"""
        results = self.analyze_all_students()
        
        # Flatten for CSV
        flattened = []
        for r in results:
            flattened.append({
                'Index': r['index'],
                'G1': r['G1'],
                'G2': r['G2'],
                'G3': r['G3'],
                'Absences': r['absences'],
                'Study_Time': r['studytime'],
                'Failures': r['failures'],
                'Family_Support': r['famsup'],
                'APS': r['risk_scores']['APS'],
                'ARS': r['risk_scores']['ARS'],
                'FSR': r['risk_scores']['FSR'],
                'LRS': r['risk_scores']['LRS'],
                'Total_Risk_Score': r['total_risk_score'],
                'Risk_Level': r['risk_level'],
                'Recommendations': ' | '.join(r['recommendations'])
            })
        
        results_df = pd.DataFrame(flattened)
        results_df.to_csv(output_path, index=False)
        print(f"\n✓ Results saved to {output_path}")
        
        return output_path


# ========== COMMAND LINE INTERFACE ==========

def run_dss(dataset_path):
    """
    Run DSS from command line
    
    Args:
        dataset_path: Path to student CSV file
        
    Returns:
        list: Analysis results
    """
    dss = StudentDSS(dataset_path)
    
    if not dss.load_data():
        return []
    
    # Analyze all students
    results = dss.analyze_all_students()
    
    # Print summary
    stats = dss.get_summary_statistics()
    print("\n" + "="*50)
    print("STUDENT RISK ASSESSMENT SUMMARY")
    print("="*50)
    print(f"Total Students: {stats['total_students']}")
    print(f"High Risk: {stats['high_risk']} ({stats['high_risk_pct']}%)")
    print(f"Moderate Risk: {stats['moderate_risk']} ({stats['moderate_risk_pct']}%)")
    print(f"Low Risk: {stats['low_risk']} ({stats['low_risk_pct']}%)")
    print("="*50 + "\n")
    
    # Save results
    dss.save_results()
    
    return results


if __name__ == "__main__":
    # Test the engine
    results = run_dss("data/student-mat.csv")
    
    # Show only HIGH RISK students
    high_risk_students = [s for s in results if s['risk_level'] == 'High Risk']

    print(f"\n=== ALL {len(high_risk_students)} HIGH RISK STUDENTS ===\n")

    for i, student in enumerate(high_risk_students, 1):
        print(f"{i}. Student #{student['index']}")
        print(f"   Risk Level: {student['risk_level']}")
        print(f"   Total Score: {student['total_risk_score']}")
        print(f"   G2 Grade: {student['G2']}")
        print(f"   Absences: {student['absences']}")
        print(f"   Recommendations:")
        for rec in student['recommendations']:
            print(f"      - {rec}")
        print()