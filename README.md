# **Student DSS System - Complete Setup Guide for GitHub & Anaconda**

This guide will walk you through setting up the Student Decision Support System from scratch using GitHub and Anaconda.

---

## **📋 Prerequisites**

Before you begin, make sure you have:
- ✅ **Anaconda** or **Miniconda** installed ([Download here](https://www.anaconda.com/download))
- ✅ **Git** installed ([Download here](https://git-scm.com/downloads))
- ✅ A **GitHub account** (if you want to fork/clone the repository)
- ✅ Basic familiarity with command line/terminal

---

## **🚀 Part 1: Getting the Code from GitHub**

### **Option A: Clone the Repository (If Already on GitHub)**

1. **Open Anaconda Prompt** (Windows) or **Terminal** (Mac/Linux)

2. **Navigate to where you want the project:**
   ```bash
   # Windows example:
   cd C:\Users\YourUsername\Documents
   
   # Mac/Linux example:
   cd ~/Documents
   ```

3. **Clone the repository:**
   ```bash
   git clone https://github.com/username/student-dss-project.git
   cd student-dss-project
   ```

### **Option B: Download as ZIP**

1. Go to the GitHub repository page
2. Click the green **"Code"** button
3. Select **"Download ZIP"**
4. Extract the ZIP file to your desired location
5. Open Anaconda Prompt and navigate to the extracted folder:
   ```bash
   cd path/to/student-dss-project
   ```

---

## **🐍 Part 2: Setting Up Anaconda Environment**

### **Step 1: Create a New Conda Environment**

This keeps your project dependencies isolated and organized.

```bash
conda create -n student_dss python=3.10
```

**What this does:**
- Creates a new environment named `student_dss`
- Uses Python 3.10 (compatible with all required libraries)

**When prompted**, type `y` and press Enter.

---

### **Step 2: Activate the Environment**

```bash
conda activate student_dss
```

**You should see** `(student_dss)` appear at the beginning of your command prompt, indicating the environment is active.

**Example:**
```
(student_dss) C:\Users\YourName\Documents\student-dss-project>
```

---

### **Step 3: Install Required Packages**

**Option A: Install from requirements.txt (Recommended)**

If the repository includes a `requirements.txt` file:

```bash
pip install -r requirements.txt
```

**Option B: Install Packages Manually**

If there's no `requirements.txt`, install each package:

```bash
pip install pandas
pip install experta
pip install flask
```

**Verify installation:**
```bash
pip list | grep -E "pandas|experta|flask"
```

You should see:
```
experta      x.x.x
Flask        x.x.x
pandas       x.x.x
```

---

## **📁 Part 3: Understanding the Project Structure**

After downloading, your project should look like this:

```
student-dss-project/
│
├── data/
│   └── student-mat.csv           # Student dataset
│
├── logic/
│   └── decision_rules.py         # Expert system rules
│
├── engine/
│   └── dss_engine.py             # Processing engine
│
├── ui/
│   ├── app.py                    # Flask web application
│   └── templates/                # HTML templates
│       ├── base.html
│       ├── index.html
│       ├── results.html
│       ├── dashboard.html
│       ├── student_detail.html
│       ├── at_risk.html
│       └── error.html
│
├── requirements.txt              # Python dependencies
└── README.md                     # Project documentation
```

---

## **🔧 Part 4: Verify Your Setup**

### **Step 1: Check Python Version**

```bash
python --version
```

**Expected output:**
```
Python 3.10.x
```

---

### **Step 2: Verify Data File Exists**

```bash
# Windows:
dir data\student-mat.csv

# Mac/Linux:
ls data/student-mat.csv
```

**If the file doesn't exist:**
- You need to add your own student dataset
- The CSV should have columns: `G1`, `G2`, `absences`, `studytime`, `failures`, `famsup`, `Medu`, `Fedu`, `Dalc`, `Walc`, `goout`, etc.
- Use semicolon (`;`) or comma (`,`) as separator

---

### **Step 3: Test the Engine (Command Line)**

```bash
python engine/dss_engine.py
```

**Expected output:**
```
✓ Loaded 395 student records

==================================================
STUDENT RISK ASSESSMENT SUMMARY
==================================================
Total Students: 395
High Risk: 64 (16.2%)
Moderate Risk: 177 (44.8%)
Low Risk: 154 (39.0%)
==================================================

✓ Results saved to student_risk_results.csv

=== ALL 241 AT-RISK STUDENTS ===

1. Student #0
   Risk Level: High Risk
   Total Score: 8
   ...
```

**If you see this**, the engine is working! ✅

**If you get an error:**
- Check that you're in the project root directory
- Verify all files are in the correct folders
- Make sure the conda environment is activated

---

## **🌐 Part 5: Running the Web Interface**

### **Step 1: Start the Flask Application**

Make sure you're in the project root and your conda environment is active:

```bash
# Verify you're in the right place
pwd  # Mac/Linux
cd   # Windows

# Should show: .../student-dss-project

# Start Flask
python ui/app.py
```

---

### **Step 2: Expected Output**

```
🚀 Starting Student DSS Web Interface...
📊 Access at:
   - Form input: http://localhost:5000
   - Dashboard: http://localhost:5000/dashboard
==================================================

 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in production.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

---

### **Step 3: Open Your Web Browser**

Visit these URLs:

1. **Main Form** (analyze new students):
   ```
   http://localhost:5000
   ```

2. **Dashboard** (overview of all students):
   ```
   http://localhost:5000/dashboard
   ```

3. **At-Risk List** (students needing intervention):
   ```
   http://localhost:5000/at-risk
   ```

---

## **✅ Part 6: Testing the System**

### **Test Case 1: High-Risk Student**

1. Go to `http://localhost:5000`
2. Fill out the form with these values:

   **Academic Performance:**
   - First Period Grade (G1): `5`
   - Second Period Grade (G2): `6`
   - Past Failures: `2`

   **Attendance:**
   - Absences: `20`

   **Study Habits:**
   - Weekly Study Time: `< 2 hours`

   **Family Support:**
   - Family Educational Support: `No`
   - Mother's Education: `5th-9th grade`
   - Father's Education: `5th-9th grade`

3. Click **"Analyze Risk Level"**

**Expected Result:**
- Risk Level: **High Risk**
- Risk Score: **8-10**
- Multiple intervention recommendations

---

### **Test Case 2: Low-Risk Student**

1. Go to `http://localhost:5000`
2. Fill out the form:

   **Academic Performance:**
   - G1: `18`
   - G2: `17`
   - Past Failures: `0`

   **Attendance:**
   - Absences: `2`

   **Study Habits:**
   - Weekly Study Time: `> 10 hours`

   **Family Support:**
   - Family Educational Support: `Yes`
   - Mother's Education: `Higher education`
   - Father's Education: `Higher education`

3. Click **"Analyze Risk Level"**

**Expected Result:**
- Risk Level: **Low Risk**
- Risk Score: **< 4**
- Positive feedback

---

## **🐛 Part 7: Troubleshooting Common Issues**

### **Issue 1: "ModuleNotFoundError: No module named 'pandas'"**

**Solution:**
```bash
# Make sure environment is activated
conda activate student_dss

# Reinstall packages
pip install pandas experta flask
```

---

### **Issue 2: "TemplateNotFound: dashboard.html"**

**Solution:**
```bash
# Check if templates exist
dir ui\templates  # Windows
ls ui/templates   # Mac/Linux

# If files are missing, verify you downloaded the complete repository
```

---

### **Issue 3: "No such file or directory: 'data/student-mat.csv'"**

**Solution:**
```bash
# Check if data file exists
dir data\student-mat.csv  # Windows
ls data/student-mat.csv   # Mac/Linux

# If missing, you need to add your dataset to the data/ folder
```

---

### **Issue 4: "Address already in use" (Port 5000 busy)**

**Solution:**
```bash
# Option 1: Kill the process using port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <process_id> /F

# Mac/Linux:
lsof -ti:5000 | xargs kill -9

# Option 2: Use a different port
# Edit ui/app.py, change the last line to:
app.run(debug=True, port=5001)
# Then visit: http://localhost:5001
```

---

### **Issue 5: Import Errors**

**Solution:**
```bash
# Make sure you're running from the project root
cd path/to/student-dss-project

# Verify structure
tree  # Mac/Linux
tree /F  # Windows

# Should show logic/, engine/, ui/ folders
```

---

## **📊 Part 8: Working with Your Own Data**

### **Step 1: Prepare Your CSV File**

Your CSV file should have these columns (minimum):

| Column | Type | Description | Range |
|--------|------|-------------|-------|
| `G1` | int | First period grade | 0-20 |
| `G2` | int | Second period grade | 0-20 |
| `absences` | int | Number of absences | 0-93 |
| `studytime` | int | Weekly study time | 1-4 |
| `failures` | int | Past failures | 0-4 |
| `famsup` | string | Family support | yes/no |
| `Medu` | int | Mother's education | 0-4 |
| `Fedu` | int | Father's education | 0-4 |
| `Dalc` | int | Workday alcohol | 1-5 |
| `Walc` | int | Weekend alcohol | 1-5 |
| `goout` | int | Going out frequency | 1-5 |

**Example CSV:**
```csv
G1;G2;absences;studytime;failures;famsup;Medu;Fedu;Dalc;Walc;goout
5;6;6;2;0;no;4;4;1;1;4
6;5;4;2;0;yes;3;3;1;1;3
15;14;2;3;0;yes;4;4;1;1;2
```

---

### **Step 2: Replace the Dataset**

1. Save your CSV file as `student-mat.csv`
2. Place it in the `data/` folder
3. Restart the Flask application

```bash
# Stop Flask (Ctrl+C)
# Restart
python ui/app.py
```

---

## **🎓 Part 9: Understanding the Output**

### **Risk Scores Breakdown:**

| Score Component | What It Measures | Max Points |
|----------------|------------------|------------|
| **APS** | Academic Performance | 4 |
| **ARS** | Attendance Risk | 3 |
| **FSR** | Family Support Risk | 3 |
| **LRS** | Lifestyle Risk | 5 |
| **Total** | Overall Risk | 15 |

### **Risk Classifications:**

| Total Score | Risk Level | Action Required |
|-------------|-----------|-----------------|
| 0-3 | **Low Risk** | Continue current support |
| 4-7 | **Moderate Risk** | Monitoring & support |
| 8+ | **High Risk** | Immediate intervention |

---

## **💾 Part 10: Saving Your Work**

### **Deactivate Environment (When Done)**

```bash
conda deactivate
```

### **Reactivate Later**

```bash
conda activate student_dss
cd path/to/student-dss-project
python ui/app.py
```

---

## **📦 Part 11: Sharing Your Setup (Creating requirements.txt)**

If you want to share your exact setup:

```bash
# Create requirements file
pip freeze > requirements.txt

# Others can then install with:
pip install -r requirements.txt
```

---

## **🔄 Part 12: Updating the Code (Git)**

### **Pull Latest Changes**

```bash
git pull origin main
```

### **Check What Changed**

```bash
git status
git log --oneline -5
```

---

## **📝 Quick Reference Commands**

**Start working:**
```bash
conda activate student_dss
cd path/to/student-dss-project
python ui/app.py
```

**Stop working:**
```bash
# Press Ctrl+C to stop Flask
conda deactivate
```

**Test engine only:**
```bash
conda activate student_dss
cd path/to/student-dss-project
python engine/dss_engine.py
```

**View installed packages:**
```bash
conda list
```

**Remove environment (if needed):**
```bash
conda deactivate
conda env remove -n student_dss
```

---

## **✅ Checklist: You're Ready When...**

- [ ] Conda environment `student_dss` created and activated
- [ ] All packages installed (pandas, experta, flask)
- [ ] Data file exists in `data/student-mat.csv`
- [ ] Engine runs successfully: `python engine/dss_engine.py`
- [ ] Flask app starts: `python ui/app.py`
- [ ] Can access `http://localhost:5000` in browser
- [ ] Form submission works (no errors)
- [ ] Dashboard shows statistics

---

## **🆘 Getting Help**

**If you're stuck:**

1. **Check the error message** - it usually tells you what's wrong
2. **Verify your environment is activated** - look for `(student_dss)` in your prompt
3. **Make sure you're in the project root directory** - run `pwd` or `cd`
4. **Check file paths** - use `dir` (Windows) or `ls` (Mac/Linux)
5. **Review this guide** - follow each step carefully

**Common mistakes:**
- Forgetting to activate the conda environment
- Running commands from the wrong directory
- Missing the data file
- Not installing all required packages

---

## **🎉 Success!**

You should now have:
- ✅ A working Student DSS system
- ✅ Web interface running on your computer
- ✅ Ability to analyze student risk
- ✅ Generated reports and recommendations

**Next steps:**
- Customize the rules in `logic/decision_rules.py`
- Add your own student data
- Modify the web interface styling
- Deploy to a server for team access

---

**Congratulations! You're all set up!** 🚀
