# Academic Dashboard (Franco-Singaporean)

Made this streamlit dashboard for myself initially as I wanted to visualise the progress of my studies at university. I began first with the French version, but added the Singaporean version (mainly modeled after NUS' grading system) once a few friends from Singapore asked for the source code. Therefore, it's Franco-Singaporean.

---

## Web Version

If you want to see whether or not this would be useful to you, this is a good place to start. However if you're looking for something more long-term, I recommend running this locally on your machine. (Explained below)

1. Open https://acadash.streamlit.app
2. **To save it as an App on your Phone/Laptop:**
   - **On iPhone (Safari):** Tap 'Share' -> 'Add to Home Screen'.
   - **On Android (Chrome):** Tap the three dots -> 'Install app'.
   - **On Laptop (Chrome/Edge):** Click the 'Install' icon in the address bar (right side).
3. This will put a **👑 Icon** on your desktop/home screen and open the dashboard in its own clean window.

---

## For local set up

If you want to run this locally on your machine:

### 1. Prerequisites
Ensure you have Python installed.

### 2. Installation
Clone this repo and install these libraries:
```bash
pip install streamlit pandas scipy
```

### 3. Run
In your terminal, run:
```bash
cd Downloads/Academic-Dashboard-Franco-Singaporean--main/Academic_Dashboard
streamlit run app.py
```
