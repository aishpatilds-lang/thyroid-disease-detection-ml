import streamlit as st
import pandas as pd
import pickle
import os
import hashlib
import sqlite3
import base64

# ------------------------------
# Database Setup (SQLite)
# ------------------------------
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT
            )''')
conn.commit()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, password):
    c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()

def login_user(username, password):
    hashed = hash_password(password)
    c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, hashed))
    return c.fetchone()

def user_exists(username):
    c.execute('SELECT * FROM users WHERE username=?', (username,))
    return c.fetchone() is not None

# ------------------------------
# Model Loading
# ------------------------------
model_path = r"C:\Users\Shravani\OneDrive\ML Lab\Thyroid-Detection-App-using-Streamlit\model.pkl"
model = None
if os.path.exists(model_path):
    with open(model_path, "rb") as file:
        model = pickle.load(file)
else:
    st.warning(" Model file not found. Please check the model path.")

# ------------------------------
# Background Image
# ------------------------------
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    .main {{
        background-color: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(8px);
        border-radius: 12px;
        padding: 20px;
        margin: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

set_bg(r"C:\Users\Shravani\OneDrive\ML Lab\Thyroid-Detection-App-using-Streamlit\image\thyro.png")

# ------------------------------
# Page Config
# ------------------------------
st.set_page_config(page_title="Thyroid Detection App", page_icon="🩺", layout="centered")
st.title("🩺 Thyroid Detection System")

# ------------------------------
# Session Management
# ------------------------------
if "page" not in st.session_state:
    st.session_state["page"] = "Sign Up"

# ------------------------------
# SIGN UP PAGE
# ------------------------------
if st.session_state["page"] == "Sign Up":
    st.header("Create New Account")

    new_username = st.text_input("Username")
    new_password = st.text_input(" Password", type="password")
    confirm_password = st.text_input(" Confirm Password", type="password")

    if st.button("Create Account"):
        if not new_username or not new_password:
            st.warning(" Please fill all fields.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        elif user_exists(new_username):
            st.error("Username already exists. Try another one.")
        else:
            add_user(new_username, hash_password(new_password))
            st.success(" Account created successfully! Please login.")
            st.session_state["page"] = "Login"
            st.rerun()

    if st.button(" Already have an account? Login here"):
        st.session_state["page"] = "Login"
        st.rerun()

# ------------------------------
# LOGIN PAGE
# ------------------------------
elif st.session_state["page"] == "Login":
    st.header(" Login to Your Account")

    username = st.text_input(" Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if login_user(username, password):
            st.success(f"🎉 Welcome, {username}!")
            st.session_state["user"] = username
            st.session_state["page"] = "App"
            st.rerun()
        else:
            st.error("Invalid username or password.")

    if st.button("🆕 Don’t have an account? Sign up"):
        st.session_state["page"] = "Sign Up"
        st.rerun()

# ------------------------------
# MAIN APP PAGE
# ------------------------------
elif st.session_state.get("page") == "App" and st.session_state.get("user"):
    
    with st.form("thyroid_form"):
        col1, col2 = st.columns(2)

        with col1:
            age = st.number_input("Age", max_value=120, step=1)
            sex = st.selectbox("Sex", ["male", "female"])
            on_thyroxine = st.selectbox("On Thyroxine?", ["no", "yes"])
            query_on_thyroxine = st.selectbox("Query On Thyroxine?", ["no", "yes"])
            on_antithyroid_medication = st.selectbox("On Antithyroid Medication?", ["no", "yes"])  # ✅ fixed name
            sick = st.selectbox("Sick?", ["no", "yes"])
            pregnant = st.selectbox("Pregnant?", ["no", "yes"])
            psych = st.selectbox("Psych?", ["no", "yes"])


        with col2:
            thyroid_surgery = st.selectbox("Thyroid Surgery?", ["no", "yes"])
            I131_treatment = st.selectbox("I131 Treatment?", ["no", "yes"])
            query_hypothyroid = st.selectbox("Query Hypothyroid?", ["no", "yes"])
            query_hyperthyroid = st.selectbox("Query Hyperthyroid?", ["no", "yes"])
            lithium = st.selectbox("On Lithium?", ["no", "yes"])
            goitre = st.selectbox("Goitre?", ["no", "yes"])
            tumor = st.selectbox("Tumor?", ["no", "yes"])
            hypopituitary = st.selectbox("Hypopituitary?", ["no", "yes"])
        

        st.divider()
        TSH = st.number_input("TSH", step=0.1)
        T3 = st.number_input("T3", min_value=0.0, step=0.1)
        TT4 = st.number_input("TT4", min_value=0.0, step=0.1)
        T4U = st.number_input("T4U", min_value=0.0, step=0.1)
        FTI = st.number_input("FTI", min_value=0.0, step=0.1)

        submitted = st.form_submit_button("🔍 Predict")

    if submitted:
        if model:
            # ✅ variable name corrected below
            input_data = pd.DataFrame({
                'age': [age],
                'sex': [1 if sex == 'female' else 0],
                'on_thyroxine': [1 if on_thyroxine == 'yes' else 0],
                'query_on_thyroxine': [1 if query_on_thyroxine == 'yes' else 0],
                'on_antithyroid_meds': [1 if on_antithyroid_medication == 'yes' else 0],
                'sick': [1 if sick == 'yes' else 0],
                'pregnant': [1 if pregnant == 'yes' else 0],
                'thyroid_surgery': [1 if thyroid_surgery == 'yes' else 0],
                'I131_treatment': [1 if I131_treatment == 'yes' else 0],
                'query_hypothyroid': [1 if query_hypothyroid == 'yes' else 0],
                'query_hyperthyroid': [1 if query_hyperthyroid == 'yes' else 0],
                'lithium': [1 if lithium == 'yes' else 0],
                'goitre': [1 if goitre == 'yes' else 0],
                'tumor': [1 if tumor == 'yes' else 0],
                'hypopituitary': [1 if hypopituitary == 'yes' else 0],
                'psych': [1 if psych == 'yes' else 0],
                'TSH': [TSH],
                'T3': [T3],
                'TT4': [TT4],
                'T4U': [T4U],
                'FTI': [FTI]
            })

            try:
                pred_value = int(model.predict(input_data)[0])

                if pred_value == 2:
                    st.warning("⚠️ The patient shows signs of **Hyperthyroidism**.")
                    st.markdown("""
                    ### 🍽️ Recommended Diet
                    - Eat **cruciferous vegetables** (broccoli, kale).
                    - Include **whole grains** and **plant-based proteins**.
                    - Avoid **iodine-rich foods** (seaweed, iodized salt).
                    - Limit caffeine and spicy foods.

                    ### 🏃 Exercise
                    - Gentle **yoga**, **walking**, or **swimming**.
                    - Avoid extreme workouts.

                    ### 🌐 Helpful Links
                    - [Mayo Clinic – Hyperthyroidism](https://www.mayoclinic.org/diseases-conditions/hyperthyroidism)
                    - [Healthline – Foods to Avoid](https://www.healthline.com/nutrition/hyperthyroidism-diet)
                    """)

                elif pred_value == 1:
                    st.error("⚠️ The patient shows signs of **Hypothyroidism**.")
                    st.markdown("""
                    ### 🍽️ Recommended Diet
                    - Include **iodine**, **selenium**, and **zinc-rich foods**.
                    - Avoid **soy**, **millet**, and **processed foods**.

                    ### 🏃 Exercise
                    - Brisk **walking**, **cycling**, or **yoga**.

                    ### 🌐 Helpful Links
                    - [American Thyroid Association](https://www.thyroid.org/hypothyroidism/)
                    - [Cleveland Clinic – Hypothyroidism](https://my.clevelandclinic.org/health/diseases/12120-hypothyroidism)
                    """)

                elif pred_value == 0:
                    st.success("✅ The patient appears to have **Normal Thyroid Function**.")
                    st.markdown("""
                    Maintain a healthy diet, exercise regularly, and schedule annual checkups.
                    """)

                else:
                    st.info("ℹ️ Unable to determine thyroid status.")

            except Exception as e:
                st.error(f"⚠️ Prediction failed: {e}")
        else:
            st.error("❌ Model not loaded. Please check `model.pkl` path.")
