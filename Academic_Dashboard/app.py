import streamlit as st
import pandas as pd
import json
import os
import scipy.stats as stats 

# --- CONFIGURATION ---
USER_DATA_FILE = "my_curriculum.json"
CUSTOM_CSS = """
    <style>
    /* Force Times New Roman ONLY on text-heavy elements */
    html, body, [class*="css"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, label, 
    div[data-testid="stExpander"] summary, 
    div[data-testid="stMetricLabel"] {
        font-family: "Times New Roman", Times, serif !important;
    }

    /* PROTECT ICONS: Ensure Streamlit icons and Material symbols remain untouched */
    .stIcon, [data-testid="stIcon"], i, svg, 
    span[data-testid="stWidgetLabel"] > div > div,
    span[class*="material-symbols"], 
    .st-emotion-cache-16idsys p, 
    [data-testid="stHeader"] * {
        font-family: inherit !important;
    }

    /* Fix the specific overlap in expander headers */
    div[data-testid="stExpander"] summary p {
        display: inline;
        margin-left: 0.5rem;
    }

    .stMetric { border: 1px solid #eeeeee; padding: 10px; border-radius: 5px; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem !important; }
    </style>
"""

# --- DATA MANAGEMENT (Local File Persistence) ---

def load_data():
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, "r") as f:
                return json.load(f)
        except:
            return get_default_structure()
    return get_default_structure()

def save_data(data_to_save):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(data_to_save, f, indent=4)

def get_default_structure():
    return {
        "system": "French", 
        "prev_avg": 0.0, 
        "prev_ects": 0, 
        "subjects": {},
        "grade_boundaries": {"A": 80, "A-": 75, "B+": 70, "B": 65, "B-": 60, "C+": 55, "C": 50}
    }

# Load data at start
data = load_data()

def get_cap_from_percent(percent, boundaries):
    if percent >= boundaries["A"]: return 5.0
    if percent >= boundaries["A-"]: return 4.5
    if percent >= boundaries["B+"]: return 4.0
    if percent >= boundaries["B"]: return 3.5
    if percent >= boundaries["B-"]: return 3.0
    if percent >= boundaries["C+"]: return 2.5
    if percent >= boundaries["C"]: return 2.0
    return 0.0

# --- CALCULATIONS ---
current_weighted_sum = 0.0
total_current_weight = 0.0 
subject_final_scores = {}

for sub_name, info in data["subjects"].items():
    comp_sum = sum(c['weight'] for c in info['components'].values())
    if comp_sum == 100:
        raw_score = sum(c['grade'] * (c['weight'] / 100) for c in info['components'].values())
        final_score = raw_score
        
        if data["system"] == "Singapore" and info.get("bell_curve"):
            method = info.get("bc_method")
            try:
                if method == "Mean/SD":
                    mu, sigma = info["bc_mean"], info["bc_sd"]
                else: 
                    mu = info["bc_mean"]
                    sigma = (info["bc_max"] - info["bc_min"]) / 6
                
                z = (raw_score - mu) / sigma if sigma != 0 else 0
                final_score = stats.norm.cdf(z) * 100
            except: 
                final_score = raw_score

        if data["system"] == "French":
            val = final_score
        else: 
            val = get_cap_from_percent(final_score, data["grade_boundaries"])
        
        subject_final_scores[sub_name] = val
        current_weighted_sum += (val * info['ects'])
        total_current_weight += info['ects']
    else:
        subject_final_scores[sub_name] = 0.0

cur_avg = current_weighted_sum / total_current_weight if total_current_weight > 0 else 0.0
overall_avg = ((data["prev_avg"] * data["prev_ects"]) + current_weighted_sum) / (data["prev_ects"] + total_current_weight) if (data["prev_ects"] + total_current_weight) > 0 else 0.0

# --- UI SETUP ---
st.set_page_config(page_title="Academic Dashboard", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
st.title("Academic Progress Dashboard")

m1, m2 = st.columns(2)
metric_label = "Moyenne Générale" if data["system"] == "French" else "Semester CAP"
metric_suffix = "/ 20" if data["system"] == "French" else "/ 5.0"
m1.metric(metric_label, f"{cur_avg:.2f} {metric_suffix}")
m2.metric(f"Overall {metric_label}", f"{overall_avg:.2f} {metric_suffix}")

st.divider()

tab_view, tab_edit = st.tabs(["Visual Progress", "⚙️ Settings"])

with tab_view:
    if not data["subjects"]:
        st.info("No subjects added. Go to settings to start.")
    else:
        for sub_name, score in subject_final_scores.items():
            col_label, col_bar = st.columns([1, 4])
            with col_label:
                st.write(f"**{sub_name}**")
                st.caption(f"Final: {score:.2f} {metric_suffix}")
            with col_bar:
                norm = 20.0 if data["system"] == "French" else 5.0
                st.progress(min(score / norm, 1.0))

with tab_edit:
    with st.expander("🌍 Regional Settings"):
        data["system"] = st.selectbox("Select Grading System", ["French", "Singapore"], index=0 if data["system"] == "French" else 1)
        if data["system"] == "Singapore":
            st.write("**Grade Boundaries (A = 5.0, etc.)**")
            b_cols = st.columns(len(data["grade_boundaries"]))
            for i, (grade, b_val) in enumerate(data["grade_boundaries"].items()):
                data["grade_boundaries"][grade] = b_cols[i].number_input(grade, value=int(b_val), step=1)

    with st.expander("📊 Past Semesters Data"):
        data["prev_avg"] = st.number_input("Past Average", value=float(data["prev_avg"]), step=0.01)
        data["prev_ects"] = st.number_input("Past Total Credits", value=int(data["prev_ects"]), step=1)

    with st.expander("➕ Add New Course"):
        n_col1, n_col2 = st.columns([3, 1])
        new_sub = n_col1.text_input("Course Name")
        new_ects = n_col2.number_input("Credits (ECTS/MCs)", 1, 30, 5)
        if st.button("Add Subject"):
            if new_sub:
                data["subjects"][new_sub] = {"ects": new_ects, "components": {}, "bell_curve": False}
                save_data(data)
                st.rerun()

    st.divider()

    for sub_name, info in list(data["subjects"].items()):
        with st.expander(f"Edit {sub_name}"):
            if data["system"] == "Singapore":
                info["bell_curve"] = st.checkbox("Enable Bell Curve Calculation", value=info.get("bell_curve", False), key=f"bc_{sub_name}")
                if info["bell_curve"]:
                    bc_col1, bc_col2 = st.columns(2)
                    info["bc_method"] = bc_col1.radio("Known Info", ["Mean/SD", "Mean/Min/Max"], key=f"bcm_{sub_name}")
                    info["bc_mean"] = bc_col2.number_input("Class Mean (%)", value=float(info.get("bc_mean", 50.0)), key=f"bmu_{sub_name}")
                    if info["bc_method"] == "Mean/SD":
                        info["bc_sd"] = st.number_input("Std Deviation", value=float(info.get("bc_sd", 10.0)), key=f"bsd_{sub_name}")
                    else:
                        m_col1, m_col2 = st.columns(2)
                        info["bc_min"] = m_col1.number_input("Min Score (%)", value=float(info.get("bc_min", 0.0)), key=f"bmin_{sub_name}")
                        info["bc_max"] = m_col2.number_input("Max Score (%)", value=float(info.get("bc_max", 100.0)), key=f"bmax_{sub_name}")

            for c_name, c_data in list(info["components"].items()):
                ca, cb, cc = st.columns([2, 2, 1])
                limit = 100.0 if data["system"] == "Singapore" else 20.0
                g = ca.number_input(f"Grade: {c_name}", 0.0, limit, float(c_data['grade']), key=f"g_{sub_name}_{c_name}")
                w = cb.number_input(f"Weight %: {c_name}", 0, 100, int(c_data['weight']), key=f"w_{sub_name}_{c_name}")
                info["components"][c_name] = {"grade": g, "weight": w}
                if cc.button("Delete", key=f"del_{sub_name}_{c_name}"):
                    del info["components"][c_name]
                    save_data(data)
                    st.rerun()
            
            if st.button(f"Add Component to {sub_name}"):
                info["components"][f"Comp {len(info['components'])+1}"] = {"grade": 0.0, "weight": 0}
                save_data(data)
                st.rerun()
            
            if st.button(f"Delete Subject: {sub_name}", type="secondary"):
                del data["subjects"][sub_name]
                save_data(data)
                st.rerun()

    if st.button("Save Changes", type="primary", use_container_width=True):
        save_data(data)
        st.success("All changes saved locally!")
