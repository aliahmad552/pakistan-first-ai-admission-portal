from flask import Flask, request, render_template
import joblib
import numpy as np
import pandas as pd
import json
from utils.explain_shap import explain_prediction
from utils.explain_shap import recommend_fields_verbose, recommend_universities_verbose
from universities import get_merit_chart_data
from flask import request, jsonify
import openai
import os
from dotenv import load_dotenv
load_dotenv()


with open("merit_formulas.json", "r") as f:
    merit_formulas = json.load(f)


app = Flask(__name__)
# Use OpenRouter settings
openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.api_base = "https://openrouter.ai/api/v1"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get("message")

    try:
        response = openai.ChatCompletion.create(
            model="mistralai/mistral-7b-instruct",  # free model
            messages=[
                {"role": "system", "content": "You are a helpful admission assistant for Pakistani students."},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message["content"].strip()
        return jsonify({'reply': reply})

    except Exception as e:
        print("Error:", e)
        return jsonify({'reply': "⚠️ Sorry, something went wrong while contacting the AI assistant."})
import pickle
# Load trained RandomForest model
model = joblib.load(open("model/rf.pkl", "rb"))

# Load cleaned data to populate dropdowns
df = pd.read_csv("cleaned_data.csv")

# Load label encoders
label_encoders = {
    'province': pickle.load(open("model/le_province.pkl", "rb")),
    'gender': pickle.load(open("model/le_gender.pkl","rb")),
    'campus_full': pickle.load(open("model/le_campus_full.pkl", "rb")),
    'field_applied': pickle.load(open("model/le_field_applied.pkl", "rb")),
    'entry_test_type': pickle.load(open("model/le_entry_test_type.pkl", "rb")),
}

# Helper function to get unique values for dropdowns
def get_dropdown_data():
    universities = sorted(df['university'].dropna().unique())
    provinces = sorted(df['province'].dropna().unique())
    genders = ['Male', 'Female']
    fields = sorted(df['field_applied'].dropna().unique())

    uni_campus_map = {}
    uni_test_map = {}

    for uni in universities:
        uni_df = df[df['university'] == uni]
        uni_campus_map[uni] = sorted(uni_df['campus'].dropna().unique().tolist())
        uni_test_map[uni] = sorted(uni_df['entry_test_type'].dropna().unique().tolist())

    return universities, provinces, genders, fields, uni_campus_map, uni_test_map

@app.route('/')
def home():
    return render_template(
        'index.html',
        chat_title="🎓 Ask About Admission Portal",
        show_form=False,
        show_result=False
    )


@app.route('/form')
def form():
    universities, provinces, genders, fields, uni_campus_map, uni_test_map = get_dropdown_data()
    return render_template(
        'form_section.html',
        chat_title="📝 Help with Admission Form",
        universities=universities,
        provinces=provinces,
        genders=genders,
        fields=fields,
        uni_campus_map=json.dumps(uni_campus_map),
        uni_test_map=json.dumps(uni_test_map),
        show_form=True,
        show_result=False  # So result blocks are hidden initially
    )




@app.route('/predict', methods=['POST'])
def predict():
    print("Received form data:", request.form)

    try:
        # Get form values
        gender = request.form['gender']
        matric_marks = float(request.form['matric_marks'])
        fsc_marks = float(request.form['fsc_marks'])
        entry_test_score = float(request.form['entry_test_score'])
        entry_test_max_score = float(request.form['entry_test_max_score'])

        university = request.form['university']
        campus = request.form['campus']
        campus_full = f"{university} - {campus}"

        province = request.form['province']
        field_applied = request.form['field_applied']
        entry_test_type = request.form['entry_test_type']

        # Normalize numeric values
        matric_normalized = matric_marks / 1200
        fsc_normalized = fsc_marks / 1200
        normalized_entry_score = entry_test_score / entry_test_max_score

        # Get weights from JSON or use default if not found
        weights = merit_formulas.get(university, {"matric": 0.10, "fsc": 0.45, "entry_test": 0.45})

        # Compute aggregate dynamically
        student_agg = (
                weights.get("matric", 0.0) * matric_normalized +
                weights.get("fsc", 0.0) * fsc_normalized +
                weights.get("entry_test", 0.0) * normalized_entry_score
        )

        # 🔍 Build explanation text
        weights_str_parts = []
        if "matric" in weights:
            weights_str_parts.append(f"{int(weights['matric'] * 100)}% Matric")
        if "fsc" in weights:
            weights_str_parts.append(f"{int(weights['fsc'] * 100)}% FSC")
        if "entry_test" in weights:
            weights_str_parts.append(f"{int(weights['entry_test'] * 100)}% Entry Test")

        # Join explanation
        merit_formula_text = " + ".join(weights_str_parts)
        merit_explanation = (
            f"📘 Merit Formula Used by {university}: {merit_formula_text}<br>"
            f"🔢 <strong>Your Aggregate:</strong> {round(student_agg * 100, 2)}%"
        )
        print("Encoder classes (province):", label_encoders['entry_test_type'].classes_)
        print("Incoming province:", entry_test_type)

        # Label encoding
        gender_encoded = label_encoders['gender'].transform([gender])[0]
        province_encoded = label_encoders['province'].transform([province])[0]
        field_encoded = label_encoders['field_applied'].transform([field_applied])[0]
        test_type_encoded = label_encoders['entry_test_type'].transform([entry_test_type])[0]
        campus_full_encoded = label_encoders['campus_full'].transform([campus_full])[0]

        # Prepare input for prediction
        feature_columns = [
            'matric_normalized', 'fsc_normalized', 'normalized_entry_score',
            'gender', 'province', 'campus_full',
            'field_applied', 'entry_test_type'
        ]

        input_df = pd.DataFrame([[
            matric_normalized,
            fsc_normalized,
            normalized_entry_score,
            gender_encoded,  # encoded numeric value
            province_encoded,
            campus_full_encoded,
            field_encoded,
            test_type_encoded
        ]], columns=feature_columns)

        prediction = model.predict(input_df)[0]
        result = "🎓 Selected" if prediction == 1 else "❌ Not Selected"
        # ✅ Add this to define input_dict for SHAP
        input_dict = {
            "gender": int(gender_encoded),
            "matric_normalized": float(matric_normalized),
            "fsc_normalized": float(fsc_normalized),
            "normalized_entry_score": float(normalized_entry_score),
            "province": int(province_encoded),
            "campus_full": int(campus_full_encoded),
            "field_applied": int(field_encoded),
            "entry_test_type": int(test_type_encoded),
        }
        recommendation_unis_links = [
    {
        'university': 'UET Lahore',
        'avg_merit': '82%',
        'chance': 'Moderate',
        'why': 'Strong engineering programs with focus on practical skills and research.',
        'comment': 'Good for engineering streams with competitive admission.',
        'url': 'https://uet.edu.pk',
    },
    {
        'university': 'NUST',
        'avg_merit': '88%',
        'chance': 'High',
        'why': 'Top-tier engineering and computer science programs with excellent faculty.',
        'comment': 'Top-tier engineering and CS programs, highly competitive.',
        'url': 'https://nust.edu.pk',
    },
    {
        'university': 'FAST',
        'avg_merit': '90%',
        'chance': 'High',
        'why': 'Renowned for excellence in computer science and software engineering education.',
        'comment': 'Excellent for Computer Science and software engineering.',
        'url': 'https://www.fast.edu.pk',
    },
    {
        'university': 'COMSATS',
        'avg_merit': '78%',
        'chance': 'Moderate',
        'why': 'Offers diverse technical programs with multiple campuses nationwide.',
        'comment': 'Good technical programs with multiple campuses.',
        'url': 'https://comsats.edu.pk',
    },
    {
        'university': 'PU Lahore',
        'avg_merit': '70%',
        'chance': 'Good',
        'why': 'Strong traditional university with a wide range of academic programs.',
        'comment': 'Strong traditional university with diverse programs.',
        'url': 'https://pu.edu.pk',
    },
    {
        'university': 'GIKI',
        'avg_merit': '85%',
        'chance': 'High',
        'why': 'Highly reputed engineering university known for quality education.',
        'comment': 'Renowned engineering university with competitive admissions.',
        'url': 'https://giki.edu.pk',
    },
    {
        'university': 'LUMS',
        'avg_merit': '88%',
        'chance': 'High',
        'why': 'Top business, law, and computer science programs with limited seats.',
        'comment': 'Excellent business, law and CS programs with limited seats.',
        'url': 'https://lums.edu.pk',
    },
    {
        'university': 'IBA Karachi',
        'avg_merit': '82%',
        'chance': 'Moderate',
        'why': 'Leading business school with a strong alumni network and industry connections.',
        'comment': 'Leading business school with strong alumni network.',
        'url': 'https://iba.edu.pk',
    },
    {
        'university': 'NED University',
        'avg_merit': '75%',
        'chance': 'Good',
        'why': 'Popular engineering university in Sindh with balanced competition.',
        'comment': 'Popular for engineering in Sindh with moderate competition.',
        'url': 'https://neduet.edu.pk',
    },
    {
        'university': 'Bahria University',
        'avg_merit': '70%',
        'chance': 'Good',
        'why': 'Known for flexible admissions in engineering, CS, and business disciplines.',
        'comment': 'Known for engineering, CS, and business with flexible admissions.',
        'url': 'https://bahria.edu.pk',
    },
    {
        'university': 'Air University',
        'avg_merit': '72%',
        'chance': 'Good',
        'why': 'Offers diverse programs including engineering and information technology.',
        'comment': 'Offers diverse programs, including engineering and IT.',
        'url': 'https://airuniversity.edu.pk',
    },
    {
        'university': 'QAU Islamabad',
        'avg_merit': '78%',
        'chance': 'Moderate',
        'why': 'Strong emphasis on science and social sciences research and education.',
        'comment': 'Strong focus on science and social sciences.',
        'url': 'https://qau.edu.pk',
    },
    {
        'university': 'UMT Lahore',
        'avg_merit': '75%',
        'chance': 'Good',
        'why': 'Private university with strong engineering and management programs.',
        'comment': 'Good private university for engineering and management.',
        'url': 'https://umt.edu.pk',
    },
    {
        'university': 'UCP Lahore',
        'avg_merit': '73%',
        'chance': 'Good',
        'why': 'Strong in business and computer science disciplines with good faculty.',
        'comment': 'Strong in business and computer science disciplines.',
        'url': 'https://ucp.edu.pk',
    },
    {
        'university': 'UET Taxila',
        'avg_merit': '80%',
        'chance': 'Moderate',
        'why': 'Offers quality engineering programs with campus-specific options.',
        'comment': 'Good engineering programs with campus-specific options.',
        'url': 'https://uet.edu.pk/taxila',
    },
    {
        'university': 'SZABIST',
        'avg_merit': '70%',
        'chance': 'Good',
        'why': 'Known for reputable business and IT programs.',
        'comment': 'Known for business and IT programs.',
        'url': 'https://szabist.edu.pk',
    },
    {
        'university': 'IST',
        'avg_merit': '68%',
        'chance': 'Good',
        'why': 'Well-regarded for engineering and technology disciplines.',
        'comment': 'Well-regarded for engineering and technology.',
        'url': 'https://ist.edu.pk',
    },
    {
        'university': 'Riphah International',
        'avg_merit': '65%',
        'chance': 'Good',
        'why': 'Offers programs in health sciences, engineering, and IT fields.',
        'comment': 'Offers health sciences, engineering, and IT.',
        'url': 'https://riphah.edu.pk',
    },
    {
        'university': 'Superior University',
        'avg_merit': '68%',
        'chance': 'Good',
        'why': 'Popular private university with multiple academic disciplines.',
        'comment': 'Popular private university with multiple disciplines.',
        'url': 'https://superior.edu.pk',
    },
    {
        'university': 'Dow University',
        'avg_merit': '70%',
        'chance': 'Good',
        'why': 'Leading medical university in Karachi with quality healthcare programs.',
        'comment': 'Leading medical university in Karachi.',
        'url': 'https://duhs.edu.pk',
    },
    {
        'university': 'NUMS',
        'avg_merit': '75%',
        'chance': 'Moderate',
        'why': 'National university focusing on medical and health sciences education.',
        'comment': 'National University of Medical Sciences, good for health fields.',
        'url': 'https://numspak.edu.pk',
    },
    {
        'university': 'Arid Agriculture',
        'avg_merit': '67%',
        'chance': 'Good',
        'why': 'Strong programs in agriculture and veterinary sciences.',
        'comment': 'Strong agriculture and veterinary programs.',
        'url': 'https://uaar.edu.pk',
    },
    {
        'university': 'KFUEIT',
        'avg_merit': '65%',
        'chance': 'Good',
        'why': 'Focus on engineering and technology education in Kohat region.',
        'comment': 'Engineering and technology focus in Kohat.',
        'url': 'https://kfueit.edu.pk',
    },
    {
        'university': 'Islamia University',
        'avg_merit': '60%',
        'chance': 'Good',
        'why': 'Offers wide range of programs with regional emphasis.',
        'comment': 'Wide range of programs with regional focus.',
        'url': 'https://iub.edu.pk',
    },
    {
        'university': 'Abbottabad University',
        'avg_merit': '60%',
        'chance': 'Good',
        'why': 'Regional university with growing academic programs.',
        'comment': 'Regional university with developing programs.',
        'url': 'https://uaf.edu.pk',
    },
    {
        'university': 'University of Peshawar',
        'avg_merit': '65%',
        'chance': 'Good',
        'why': 'Well-established university offering diverse academic fields.',
        'comment': 'Well-established university with diverse programs.',
        'url': 'http://uop.edu.pk',
    },
    {
        'university': 'Bahauddin Zakariya',
        'avg_merit': '62%',
        'chance': 'Good',
        'why': 'Strong presence in southern Punjab for multiple disciplines.',
        'comment': 'Strong presence in southern Punjab for multiple programs.',
        'url': 'https://bzu.edu.pk',
    },
    {
        'university': 'University of Sargodha',
        'avg_merit': '60%',
        'chance': 'Good',
        'why': 'Offers a variety of programs with moderate competition.',
        'comment': 'Offers multiple programs with moderate competition.',
        'url': 'https://uos.edu.pk',
    },
    {
        'university': 'Allama Iqbal Open University',
        'avg_merit': '55%',
        'chance': 'Good',
        'why': 'Open university providing distance learning opportunities.',
        'comment': 'Open university with distance learning programs.',
        'url': 'http://aiou.edu.pk',
    },
    {
        'university': 'University of Karachi',
        'avg_merit': '68%',
        'chance': 'Good',
        'why': 'Largest university in Karachi offering numerous disciplines.',
        'comment': 'Largest university in Karachi with many disciplines.',
        'url': 'https://uok.edu.pk',
    },
    {
        'university': 'University of Sindh',
        'avg_merit': '60%',
        'chance': 'Good',
        'why': 'Wide range of programs with regional importance.',
        'comment': 'Wide range of programs with regional importance.',
        'url': 'https://usindh.edu.pk',
    },
    {
        'university': 'GCU Lahore',
        'avg_merit': '72%',
        'chance': 'Good',
        'why': 'One of Punjab’s oldest and top-ranked public universities.',
        'comment': 'One of the oldest and top public universities in Punjab.',
        'url': 'https://gcu.edu.pk',
    },
    {
        'university': 'GCUF',
        'avg_merit': '70%',
        'chance': 'Good',
        'why': 'Well-known for science and technology programs.',
        'comment': 'Good science and technology programs.',
        'url': 'https://gcuf.edu.pk',
    },
    {
        'university': 'Hazara University',
        'avg_merit': '58%',
        'chance': 'Good',
        'why': 'Regional university offering various academic programs.',
        'comment': 'Regional university offering various programs.',
        'url': 'https://hu.edu.pk',
    },
    {
        'university': 'Islamic University',
        'avg_merit': '60%',
        'chance': 'Good',
        'why': 'Focuses on Islamic studies and related disciplines.',
        'comment': 'Focus on Islamic studies and other disciplines.',
        'url': 'https://iiu.edu.pk',
    },
    {
        'university': 'Ziauddin University',
        'avg_merit': '65%',
        'chance': 'Good',
        'why': 'Private university known for health sciences programs.',
        'comment': 'Private university with health sciences focus.',
        'url': 'https://zu.edu.pk',
    },
    {
        'university': 'HITEC University',
        'avg_merit': '60%',
        'chance': 'Good',
        'why': 'Private university focusing on engineering and IT education.',
        'comment': 'Private university focusing on engineering and IT.',
        'url': 'https://hitecuni.edu.pk',
    },
    {
        'university': 'Iqra University',
        'avg_merit': '68%',
        'chance': 'Good',
        'why': 'Popular private university in Karachi with diverse programs.',
        'comment': 'Popular private university in Karachi for various programs.',
        'url': 'https://iqra.edu.pk',
    },
    {
        'university': 'UMT Sialkot',
        'avg_merit': '60%',
        'chance': 'Good',
        'why': 'Growing regional campus with expanding program offerings.',
        'comment': 'Regional campus of UMT with growing reputation.',
        'url': 'https://umt.edu.pk',
    },
    {
        'university': 'University of Education',
        'avg_merit': '62%',
        'chance': 'Good',
        'why': 'Strong focus on education and teacher training programs.',
        'comment': 'Strong focus on education and teacher training.',
        'url': 'https://ue.edu.pk',
    },
]


        # After generating your recommendations list:
        for rec in recommendation_unis_links:
            merit_chart = get_merit_chart_data(rec['university'])
            rec['merit_labels'] = merit_chart['labels']
            rec['merit_values'] = merit_chart['values']


        # After getting prediction, aggregate and SHAP
        # Old basic recommendation_unis structure — not detailed enough
        # recommendation_unis = recommend_universities_verbose(...)

        # ✅ New: merge detailed info from recommendation_unis_links
        recommended_unis_full = []
        for rec in recommend_universities_verbose(student_agg, province):

            full_info = next(
                (item.copy() for item in recommendation_unis_links if item['university'] == rec['university']), None)
            if full_info:
                full_info['chance'] = rec.get('chance', full_info.get('chance', 'Info N/A'))
                full_info['avg_merit'] = rec.get('avg_merit', full_info.get('avg_merit', 'Unknown'))
                full_info['comment'] = rec.get('comment', full_info.get('comment', 'No comment available'))

                full_info['why'] = rec.get('why', full_info.get('why', 'No reason specified'))

                recommended_unis_full.append(full_info)

        recommendation_fields = recommend_fields_verbose(field_applied, student_agg, entry_test_type)

        shap_path, improvement_tips = explain_prediction(input_dict)
        # Re-render page with result
        universities, provinces, genders, fields, uni_campus_map, uni_test_map = get_dropdown_data()
        return render_template(
            'result.html',
            chat_title="📊 Ask About Your Result",
            prediction_text=result,
            prediction=result,
            shap_plot=shap_path,
            improvement_tips=improvement_tips if "Not Selected" in result else None,
            merit_explanation=merit_explanation,
            recommended_unis=recommended_unis_full,
            recommended_fields=recommendation_fields,
            universities=universities,
            provinces=provinces,
            genders=genders,
            fields=fields,
            uni_campus_map=json.dumps(uni_campus_map),
            uni_test_map=json.dumps(uni_test_map),
            show_form=False,
            show_result=False
        )


    except Exception as e:
        return f"Error occurred: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
