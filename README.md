# 🇵🇰 Pakistan AI Admission Portal 🎓

This is Pakistan's First AI-Powered University Admission Predictor Portal.  
It helps students predict their admission chances by entering their academic scores, university, test type, and other details.

---

## ✨ Key Features
- Predict admission chances using Machine Learning.
- User-friendly, modern web interface.
- Supports multiple universities, campuses, and entry tests.
- Dynamic dropdowns based on university selection.
- Auto-calculates entry test max score.
- Predicts fields based on selected test type.
- Built with Flask (Python) and Bootstrap 5.
- Model trained using RandomForestClassifier.

---

## 🚀 Project Structure

```
├── app.py                 # Flask backend
├── templates/
│   ├── form_section.html  # Main form page (UI)
│   └── result.html        # Result page
├── static/
│   └── logo.png           # Project logo
├── model/
│   ├── rf.pkl             # Trained ML Model (Large file)
│   ├── le_gender.pkl      # Label Encoder (Gender)
│   ├── le_province.pkl    # Label Encoder (Province)
│   ├── le_campus_full.pkl # Label Encoder (Campus)
│   ├── le_field_applied.pkl # Label Encoder (Field)
│   └── le_entry_test_type.pkl # Label Encoder (Test Type)
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

---

## ⚙️ How to Run Locally

1. Clone the repository:
```bash
git clone https://github.com/your-username/pakistan-ai-admission-portal.git
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Run the Flask app:
```bash
python app.py
```

4. Visit:
```
https://pakistan-first-ai-admission-portal.onrender.com/
```

---

## 🏷️ Git Large File Storage (Git LFS) Setup (Required for Model Files)
**Important:** This project uses Git LFS for large files like models (`.pkl`).

### Follow These Steps:

1. Install Git LFS:
```bash
git lfs install
```

2. Track `.pkl` files:
```bash
git lfs track "*.pkl"
```

3. Commit `.gitattributes`:
```bash
git add .gitattributes
git commit -m "Track large files with Git LFS"
```

4. Add model files:
```bash
git add model/rf.pkl
git commit -m "Add large model file via Git LFS"
```

5. Push your changes:
```bash
git push origin main
```

---

## 💡 Technologies Used
- Python (Flask)
- Scikit-learn (Random Forest Classifier)
- Pandas, Numpy
- Bootstrap 5 (Frontend)
- Git LFS (Large File Storage)

---

## 📄 Notes
- This project is for academic purposes.
- You can extend it by adding more universities, tests, and fields.

---

## 🙌 Credits
Made with ❤️ by [Ali Ahmad](https://github.com/aliahmad552)
