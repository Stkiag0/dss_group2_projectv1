"""
Rule-based decision system using Experta
Analyzes student risk based on academic, attendance, family, and lifestyle factors
"""

from experta import *

class StudentFact(Fact):
    """Facts about a student"""
    pass

class StudentRiskExpertSystem(KnowledgeEngine):
    """Expert system for student risk assessment"""
    
    def __init__(self):
        super().__init__()
        self.risk_scores = {
            'APS': 0,  # Academic Performance Score
            'ARS': 0,  # Attendance Risk Score
            'FSR': 0,  # Family Support Risk
            'LRS': 0   # Lifestyle Risk Score
        }
        self.risk_level = None
        self.recommendations = []
    
    # ========== ACADEMIC PERFORMANCE RULES ==========
    
    @Rule(StudentFact(G2=P(lambda x: x < 10)))
    def critical_academic_performance(self):
        """Rule: G2 grade below 10 is critical"""
        self.risk_scores['APS'] += 4
        self.recommendations.append("📚 Critical academic performance - immediate tutoring required")
    
    @Rule(StudentFact(G2=P(lambda x: 10 <= x <= 11)))
    def concerning_academic_performance(self):
        """Rule: G2 grade between 10-11 needs attention"""
        self.risk_scores['APS'] += 2
        self.recommendations.append("📖 Academic performance needs improvement")
    
    # ========== ATTENDANCE RULES ==========
    
    @Rule(StudentFact(absences=P(lambda x: x > 15)))
    def excessive_absences(self):
        """Rule: More than 15 absences is high risk"""
        self.risk_scores['ARS'] += 3
        self.recommendations.append("⚠️ Excessive absences detected - attendance intervention needed")
    
    @Rule(StudentFact(absences=P(lambda x: 5 <= x <= 15)))
    def moderate_absences(self):
        """Rule: 5-15 absences is moderate concern"""
        self.risk_scores['ARS'] += 1
        self.recommendations.append("⏰ Monitor attendance - trending toward excessive")
    
    # ========== FAMILY SUPPORT RULES ==========
    
    @Rule(StudentFact(famsup='no'))
    def no_family_support(self):
        """Rule: Lack of family academic support"""
        self.risk_scores['FSR'] += 2
        self.recommendations.append("👨‍👩‍👧 Lack of family support - engage parents/guardians")
    
    @Rule(StudentFact(parent_edu=P(lambda x: x <= 2)))
    def low_parent_education(self):
        """Rule: Low parent education level"""
        self.risk_scores['FSR'] += 1
        self.recommendations.append("📚 Provide additional academic resources (low parental education)")
    
    # ========== LIFESTYLE RISK RULES ==========
    
    @Rule(StudentFact(avg_alcohol=P(lambda x: x >= 4)))
    def high_alcohol_consumption(self):
        """Rule: High alcohol consumption"""
        self.risk_scores['LRS'] += 2
        self.recommendations.append("🚨 Substance use concern - counseling recommended")
    
    @Rule(StudentFact(goout=P(lambda x: x >= 4)))
    def frequent_going_out(self):
        """Rule: Frequent social outings"""
        self.risk_scores['LRS'] += 1
        self.recommendations.append("⚖️ Balance social life with academics")
    
    @Rule(StudentFact(studytime=1))
    def very_low_study_time(self):
        """Rule: Very low study time"""
        self.risk_scores['LRS'] += 2
        self.recommendations.append("⏱️ Study time critically low - create study schedule")
    
    # ========== COMBINED RISK ASSESSMENT ==========
    
    @Rule(
        StudentFact(G2=P(lambda x: x < 10)),
        StudentFact(absences=P(lambda x: x > 15))
    )
    def critical_combination(self):
        """Rule: Failing grades + high absences = critical"""
        self.recommendations.append("🚨 CRITICAL: Multiple high-risk factors - immediate intervention required")
    
    @Rule(
        StudentFact(famsup='no'),
        StudentFact(G2=P(lambda x: x < 12))
    )
    def no_support_struggling(self):
        """Rule: No family support while struggling academically"""
        self.recommendations.append("👥 Assign mentor/peer support - lacks family backing")
    
    # ========== DETERMINE RISK LEVEL ==========
    
    def calculate_total_risk(self):
        """Calculate total risk score"""
        return sum(self.risk_scores.values())
    
    def determine_risk_level(self):
        """Determine overall risk level based on total score"""
        total = self.calculate_total_risk()
        
        if total >= 8:
            self.risk_level = "High Risk"
            if "🚨 CRITICAL" not in str(self.recommendations):
                self.recommendations.append("⚠️ Immediate counseling & parental engagement required")
        elif total >= 4:
            self.risk_level = "Moderate Risk"
            self.recommendations.append("📊 Academic monitoring & support recommended")
        else:
            self.risk_level = "Low Risk"
            self.recommendations.append("✅ Continue current trajectory")
        
        return self.risk_level
    
    def reset_state(self):
        """Reset for new analysis"""
        self.risk_scores = {'APS': 0, 'ARS': 0, 'FSR': 0, 'LRS': 0}
        self.risk_level = None
        self.recommendations = []
        self.reset()


def evaluate_risk(row):
    """
    Evaluate student risk using expert system
    
    Args:
        row: Pandas Series or dict with student data
        
    Returns:
        tuple: (risk_level, recommendations, risk_scores)
    """
    # Create expert system instance
    engine = StudentRiskExpertSystem()
    engine.reset_state()
    
    # Calculate derived values
    parent_avg_edu = (row['Medu'] + row['Fedu']) / 2
    avg_alcohol = (row['Dalc'] + row['Walc']) / 2
    
    # Declare facts
    engine.declare(
        StudentFact(
            G2=row['G2'],
            absences=row['absences'],
            famsup=row['famsup'],
            parent_edu=parent_avg_edu,
            avg_alcohol=avg_alcohol,
            goout=row['goout'],
            studytime=row['studytime']
        )
    )
    
    # Run inference engine
    engine.run()
    
    # Determine final risk level
    risk_level = engine.determine_risk_level()
    
    return risk_level, engine.recommendations, engine.risk_scores