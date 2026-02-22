"""
Traditional Rule-Based Decision Logic
Uses if/else statements (not experta)
"""

def aps_adjustment(row):
    """
    Academic Performance Score (APS)
    Based on second period grade (G2)
    
    Args:
        row: dict or pandas Series with 'G2' key
        
    Returns:
        int: Risk points (0-4)
    """
    g2 = row.get('G2', 0) if isinstance(row, dict) else row['G2']
    
    if g2 < 10:
        return 4
    elif 10 <= g2 <= 11:
        return 2
    return 0


def attendance_risk(row):
    """
    Attendance Risk Score (ARS)
    
    Args:
        row: dict or pandas Series with 'absences' key
        
    Returns:
        int: Risk points (0-3)
    """
    absences = row.get('absences', 0) if isinstance(row, dict) else row['absences']
    
    if absences > 15:
        return 3
    elif absences >= 5:
        return 1
    return 0


def family_support_risk(row):
    """
    Family Support Risk (FSR)
    
    Args:
        row: dict or pandas Series with family data
        
    Returns:
        int: Risk points (0-3)
    """
    score = 0
    
    # Handle dict or Series
    if isinstance(row, dict):
        famsup = row.get('famsup', 'yes')
        medu = row.get('Medu', 2)
        fedu = row.get('Fedu', 2)
    else:
        famsup = row['famsup']
        medu = row['Medu']
        fedu = row['Fedu']
    
    if famsup == 'no':
        score += 2
    
    parent_avg = (medu + fedu) / 2
    if parent_avg <= 2:
        score += 1
    
    return score


def lifestyle_risk(row):
    """
    Lifestyle Risk Score (LRS)
    
    Args:
        row: dict or pandas Series with lifestyle data
        
    Returns:
        int: Risk points (0-5)
    """
    score = 0
    
    if isinstance(row, dict):
        dalc = row.get('Dalc', 1)
        walc = row.get('Walc', 1)
        goout = row.get('goout', 2)
        studytime = row.get('studytime', 2)
    else:
        dalc = row['Dalc']
        walc = row['Walc']
        goout = row['goout']
        studytime = row['studytime']
    
    avg_alcohol = (dalc + walc) / 2
    if avg_alcohol >= 4:
        score += 2
    
    if goout >= 4:
        score += 1
    
    if studytime == 1:
        score += 2
    
    return score


def compute_total_risk(row):
    """
    Combine all risk components
    
    Args:
        row: dict or pandas Series with all student data
        
    Returns:
        int: Total risk score (0-15)
    """
    aps = aps_adjustment(row)
    ars = attendance_risk(row)
    fsr = family_support_risk(row)
    lrs = lifestyle_risk(row)
    
    return aps + ars + fsr + lrs


def classify_risk(score):
    """
    Classify risk level based on total score
    
    Args:
        score: int, total risk score (0-15)
        
    Returns:
        str: Risk level classification
    """
    if score >= 8:
        return "High Risk"
    elif score >= 4:
        return "Moderate Risk"
    return "Low Risk"

def evaluate_risk(row):
    """
    Wrapper function to satisfy the import in dss_engine.py.
    Calculates total score, classification, and recommendations.
    """
    # 1. Calculate the numeric score (0-15)
    total_score = compute_total_risk(row)
    
    # 2. Get the string classification (High/Moderate/Low)
    risk_level = classify_risk(total_score)
    
    # 3. Get the list of actionable advice
    recommendations = recommend_intervention(row, risk_level)
    
    # Return a dictionary containing all results
    return {
        "total_score": total_score,
        "risk_level": risk_level,
        "recommendations": recommendations
    }


def recommend_intervention(row, risk_level):
    """
    Provide actionable recommendations
    
    Args:
        row: Student data (dict or Series)
        risk_level: str, risk classification
        
    Returns:
        list: Intervention recommendations
    """
    recommendations = []
    
    # Handle dict or Series
    if isinstance(row, dict):
        absences = row.get('absences', 0)
        failures = row.get('failures', 0)
        studytime = row.get('studytime', 2)
        famsup = row.get('famsup', 'yes')
        g2 = row.get('G2', 10)
    else:
        absences = row.get('absences', 0)
        failures = row.get('failures', 0)
        studytime = row.get('studytime', 2)
        famsup = row.get('famsup', 'yes')
        g2 = row.get('G2', 10)
    
    # Specific interventions based on risk factors
    if absences > 15:
        recommendations.append("⚠️ Critical attendance issue - mandatory attendance counseling")
    elif absences > 5:
        recommendations.append("⏰ Monitor attendance closely")
    
    if failures > 1:
        recommendations.append("📚 Academic remediation program required")
    elif failures == 1:
        recommendations.append("📖 Academic support recommended")
    
    if studytime == 1:
        recommendations.append("⏱️ Study skills workshop - very low study time detected")
    
    if g2 < 10:
        recommendations.append("📉 Immediate tutoring for failing grades")
    
    if famsup == 'no':
        recommendations.append("👨‍👩‍👧 Parental engagement initiative")
    
    # General recommendations by risk level
    if risk_level == "High Risk":
        recommendations.append("🚨 URGENT: Schedule intervention meeting with counselor")
        recommendations.append("📞 Contact parents/guardians immediately")
    elif risk_level == "Moderate Risk":
        recommendations.append("📊 Regular monitoring and check-ins")
    else:
        if not recommendations:
            recommendations.append("✅ Continue current trajectory")
    
    return recommendations


# ============================
# RULE SUMMARY (for documentation)
# ============================

RULE_DESCRIPTIONS = {
    'APS': {
        'name': 'Academic Performance Score',
        'rules': [
            {'condition': 'G2 < 10', 'points': 4, 'severity': 'Critical'},
            {'condition': '10 ≤ G2 ≤ 11', 'points': 2, 'severity': 'Moderate'},
            {'condition': 'G2 > 11', 'points': 0, 'severity': 'Good'}
        ]
    },
    'ARS': {
        'name': 'Attendance Risk Score',
        'rules': [
            {'condition': 'absences > 15', 'points': 3, 'severity': 'High'},
            {'condition': '5 ≤ absences ≤ 15', 'points': 1, 'severity': 'Moderate'},
            {'condition': 'absences < 5', 'points': 0, 'severity': 'Good'}
        ]
    },
    'FSR': {
        'name': 'Family Support Risk',
        'rules': [
            {'condition': 'famsup = no', 'points': 2, 'severity': 'High'},
            {'condition': 'parent_edu ≤ 2', 'points': 1, 'severity': 'Moderate'}
        ]
    },
    'LRS': {
        'name': 'Lifestyle Risk Score',
        'rules': [
            {'condition': 'avg_alcohol ≥ 4', 'points': 2, 'severity': 'High'},
            {'condition': 'goout ≥ 4', 'points': 1, 'severity': 'Moderate'},
            {'condition': 'studytime = 1', 'points': 2, 'severity': 'High'}
        ]
    }
}