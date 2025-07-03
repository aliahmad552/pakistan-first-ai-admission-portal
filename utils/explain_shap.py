# utils/explain_shap.py

import shap
import numpy as np
import pandas as pd
import pickle
import joblib
import os
import plotly.graph_objects as go

# Load model
model = joblib.load(open("model/rf.pkl", "rb"))

ENCODED_FEATURES = [
    "gender", "matric_normalized", "fsc_normalized", "normalized_entry_score",
    "province", "campus_full", "field_applied", "entry_test_type"
]

FEATURE_LABELS = {
    "gender": "Gender",
    "matric_normalized": "Matric Marks (Normalized)",
    "fsc_normalized": "FSc Marks (Normalized)",
    "normalized_entry_score": "Entry Test Score (Normalized)",
    "province": "Province",
    "campus_full": "Campus",
    "field_applied": "Field Applied",
    "entry_test_type": "Entry Test Type"
}

def explain_prediction(input_data_dict):
    X = pd.DataFrame({k: [v] for k, v in input_data_dict.items()})[ENCODED_FEATURES]

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    shap_val = shap_values[1][0] if isinstance(shap_values, list) else shap_values[0]
    base_value = explainer.expected_value[1] if isinstance(explainer.expected_value, list) else explainer.expected_value
    final_value = base_value + shap_val.sum()

    feature_names = [FEATURE_LABELS.get(f, f) for f in ENCODED_FEATURES]
    feature_values = X.iloc[0].tolist()

    def extract_scalar(val):
        if isinstance(val, (list, np.ndarray)):
            val = np.array(val).flatten()
            return float(val[0]) if len(val) > 0 else 0.0
        return float(val)

    contributions = [extract_scalar(val) for val in shap_val]
    feature_values = [extract_scalar(val) for val in feature_values]
    final_value = extract_scalar(final_value)
    base_value = extract_scalar(base_value)

    labels = [f"{name} = {val:.3f}" for name, val in zip(feature_names, feature_values)]

    # Generate SHAP Waterfall Chart
    fig = go.Figure(go.Waterfall(
        name="SHAP",
        orientation="v",
        measure=["relative"] * len(labels) + ["total"],
        x=labels + ["Final Prediction"],
        y=contributions + [final_value - base_value],
        base=base_value,
        text=[f"{c:+.3f}" for c in contributions] + [f"{final_value:.3f}"],
        hoverinfo="x+text",
        connector={"line": {"color": "rgba(63, 63, 63, 0.7)"}}
    ))

    fig.update_layout(
        title="Feature Impact on Admission Prediction",
        yaxis_title="Model Output",
        waterfallgap=0.3,
        plot_bgcolor="white"
    )

    os.makedirs("static", exist_ok=True)
    plot_path = "static/shap_plot.html"
    fig.write_html(plot_path)

    # 🔁 Corrected Improvement Tips
    tips = []
    for feature, contrib in zip(feature_names, contributions):
        if contrib < -0.1:
            if "FSc" in feature:
                tips.append("📘 Your Entry Test Score negatively impacted your result. Try to improve them.")
            elif "Entry Test" in feature:
                tips.append("📝 Your Entry Test score significantly lowered your chances. Focus on improving it.")
            elif "Matric" in feature:
                tips.append("📗 Your FSc slightly reduced your chances. Higher marks may help.")
        elif contrib > 0.1:
            if "FSc" in feature:
                tips.append("✅ Great FSc marks — they boosted your chances!")
            elif "Entry Test" in feature:
                tips.append("✅ Excellent Entry Test score — it helped your prediction!")
            elif "Matric" in feature:
                tips.append("✅ Good Matric performance contributed positively.")

    return plot_path, tips


import pandas as pd

# Load dataset
df = pd.read_csv("cleaned_data.csv")


def recommend_universities_verbose(student_agg, province, top_n=5):
    province_df = df[df["province"] == province].copy()

    # Calculate aggregate
    province_df["aggregate"] = (
            0.10 * province_df["matric_marks"] / 1200 +
            0.45 * province_df["fsc_marks"] / 1200 +
            0.45 * province_df["entry_test_score"] / province_df["entry_test_max_score"]
    )

    uni_agg = province_df.groupby("university")["aggregate"].mean().reset_index()
    uni_agg["score_diff"] = abs(uni_agg["aggregate"] - student_agg)
    uni_agg["chance"] = uni_agg["aggregate"].apply(
        lambda x: "👍 Very Likely" if x < student_agg - 0.02 else
        "✅ Good Chance" if x < student_agg + 0.01 else
        "⚠️ Competitive"
    )

    top_unis = uni_agg.sort_values("score_diff").head(top_n)

    suggestions = []
    for _, row in top_unis.iterrows():
        suggestions.append({
            "university": row["university"],
            "avg_merit": f"{row['aggregate'] * 100:.2f}%",
            "chance": row["chance"],
            "comment": "Consider Software/CS/SE programs" if "CS" in row[
                "university"] else "Explore general science or engineering options"
        })

    return suggestions


def recommend_fields_verbose(field_applied, agg, test_type):
    fields = []

    if agg >= 0.85:
        fields.append({"field": "Engineering", "comment": "High merit but great future in public and private sectors."})
        fields.append({"field": "Computer Science", "comment": "Excellent for tech-savvy students with high aggregate."})
        fields.append({"field": "Software Engineering", "comment": "Strong growth in software and IT industry."})
    elif 0.75 <= agg < 0.85:
        fields.append({"field": "Business", "comment": "Good blend of management and entrepreneurship."})
        fields.append({"field": "Education", "comment": "Stable and rewarding in teaching sector."})
        fields.append({"field": "Environmental Science", "comment": "Upcoming field with research opportunities."})
    elif 0.65 <= agg < 0.75:
        fields.append({"field": "Islamic Studies", "comment": "Suitable for academic and teaching careers."})
        fields.append({"field": "Media Sciences", "comment": "Creative field with career in digital journalism."})
        fields.append({"field": "Political Science", "comment": "Helps in competitive exams and civil services."})
    else:
        fields.append({"field": "History", "comment": "Good for civil services and teaching."})
        fields.append({"field": "Library Sciences", "comment": "Less competitive, but a growing field in academia."})
        fields.append({"field": "Sociology", "comment": "Relevant in research, development, and education."})

    return fields

