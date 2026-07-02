import streamlit as st
import joblib
import requests
from PIL import Image
import base64
import pandas as pd
from datetime import datetime
import os
import mysql.connector as sql
import subprocess
import re

# --- Load Assets (Fire Icon, Background) ---
@st.cache_data
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

fire_icon = "🔥"

# --- Custom CSS for Fire/Futuristic Theme ---
def set_fire_theme():
    fire_css = """
    <style>
    /* Main Background Plain Black */
    .stApp {
        background: #000000;
        color: #ffffff;
    }
    
    /* Fire-inspired Headers - removed text-shadow for glowing effect */
    h1, h2, h3 {
        color: #c30010 !important;
        font-family: 'Arial Black', sans-serif;
    }
    
    /* Glowing Input Boxes */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: rgba(20, 20, 20, 0.7);
        color: #c30010;
        border: 1px solid #ff5500;
        border-radius: 5px;
    }
    
    /* Fire Button */
    .stButton>button {
        background: linear-gradient(to right, #ff3300, #ff8800);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: bold;
        box-shadow: 0 0 10px #ff3333;
    }
    
    .stButton>button:hover {
        background: linear-gradient(to right, #ff5500, #ffaa00);
        box-shadow: 0 0 15px #ff5555;
    }
    
    /* Custom Expander (Flame-like) */
    .st-expander {
        background: rgba(40, 10, 0, 0.7);
        border: 1px solid #ff5500;
        border-radius: 8px;
    }
    
    /* Risk Meter (Glowing Effect) */
    .risk-high {
        animation: glow-red 1.5s infinite alternate;
    }
    @keyframes glow-red {
        from { text-shadow: 0 0 5px #ff0000; }
        to { text-shadow: 0 0 20px #ff5555; }
    }
    </style>
    """
    st.markdown(fire_css, unsafe_allow_html=True)

# Apply theme
set_fire_theme()

# --- Load Model ---
model = joblib.load('wildfire_model.pkl')

# --- Adafruit IO Setup ---
AIO_USERNAME = ""
AIO_KEY = ""
TEMP_FEED = "temperature"
HUMIDITY_FEED = "humidity"
POLLUTION_FEED = "outdoor-aqi"

# Function to save data to MySQL database
def save_to_mysql(phone, name, location, temperature, humidity, pollution, risk):
    mycon = sql.connect(host="localhost", user="root", passwd="JoelRoot1319", database="USERS")
    cursor = mycon.cursor()
    query = "INSERT INTO USERS (phone, name, location) VALUES (%s, %s, %s);"
    cursor.execute(query, (phone, name, location))
    mycon.commit()
    if mycon.is_connected():
        print("Connected to database")
    else:
        print("Database connection failed")
    cursor.close()
    mycon.close()
    return True

def sendmsg(group_name, message):
    message=int(message)
    subprocess.run(["node", "test.js", group_name, str(message)])

def get_latest_value(feed_name):
    try:
        url = f"https://io.adafruit.com/api/v2/{AIO_USERNAME}/feeds/{feed_name}/data/last"
        headers = {"X-AIO-Key": AIO_KEY}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return float(response.json()['value'])
        else:
            st.error(f"Failed to fetch data from {feed_name}. Status code: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# --- App UI ---
st.title(f" Wildfire Risk Sentinel")
st.markdown("""<div style='text-align: left; border-bottom: 2px solid #ff5500; padding-bottom: 10px; margin-bottom: 30px;'>
            Estimate the probability of a wildfire based on temperature, humidity, and pollution levels.</div>""", unsafe_allow_html=True)

# Initialize session state for user data
if 'user_data' not in st.session_state:
    st.session_state.user_data = {
        'name': '',
        'phone': '',
        'location': '',
        'temperature': None,
        'humidity': None,
        'pollution': None,
        'risk': None
    }

# --- Prediction Section ---
with st.container():
    st.header("Environmental Data Input")
    temperature = None
    humidity = None
    outdoor_aqi = None
    input_method = st.radio("Choose input source:", ("Manual Entry", "Live Sensor Data"), horizontal=True)

    if input_method == "Manual Entry":
        col1, col2, col3 = st.columns(3)
        with col1:
            temperature = st.number_input("Temperature (°C)", min_value=-50.0, max_value=100.0, value=30.0)
        with col2:
            humidity = st.number_input("Humidity (%)", min_value=0.0, max_value=100.0, value=50.0)
        with col3:
            outdoor_aqi = st.number_input("Air Quality (AQI)", min_value=0, max_value=500, value=50)
    else:
        if st.button("🔄 Fetch Live Data"):
            temperature = get_latest_value(TEMP_FEED)
            humidity = get_latest_value(HUMIDITY_FEED)
            outdoor_aqi = get_latest_value(POLLUTION_FEED)

            if None not in [temperature, humidity, outdoor_aqi]:
                st.session_state['temperature'] = temperature
                st.session_state['humidity'] = humidity
                st.session_state['outdoor_aqi'] = outdoor_aqi
                st.success("Live data loaded!")

        temperature = st.session_state.get('temperature')
        humidity = st.session_state.get('humidity')
        outdoor_aqi = st.session_state.get('outdoor_aqi')

    # 🔥 Horizontal Environmental Icons (Right under inputs)
    st.markdown("#### Visual Indicators")
    col_img1, col_img2, col_img3 = st.columns(3)
    with col_img1:
        st.image("J:/wildfire_alert_sys/images/temp.png", caption="Temperature", use_container_width=True)
    with col_img2:
        st.image("J:/wildfire_alert_sys/images/humi.png", caption="Humidity", use_container_width=True)
    with col_img3:
        st.image("J:/wildfire_alert_sys/images/aqi.png", caption="Air Quality", use_container_width=True)

# --- Prediction Button ---
if st.button("🚨 Calculate Wildfire Risk", use_container_width=True):
    if None not in [temperature, humidity, outdoor_aqi]: 
        # Create input dataframe with interaction features
        input_df = pd.DataFrame([[temperature, humidity, outdoor_aqi]], 
                      columns=['Temperature (°C)', 'Humidity Level (%)', 'Pollution Level (AQI)'])
        
        # Add interaction features
        input_df['Temp_Humidity_Interaction'] = temperature * (100 - humidity)
        input_df['Temp_AQI_Interaction'] = temperature * outdoor_aqi
        
        proba = model.predict_proba(input_df)[0]
        wildfire_prob = proba[1] * 100
        
        # Apply temperature-based scaling
        if temperature > 35:
            temp_scale = min(1.5, 1 + (temperature - 35) * 0.05)
            wildfire_prob = min(100, wildfire_prob * temp_scale)
        
        # Store data in session state
        st.session_state.user_data.update({
            'temperature': temperature,
            'humidity': humidity,
            'pollution': outdoor_aqi,
            'risk': wildfire_prob
        })
        
        # Dynamic alert threshold based on temperature
        alert_threshold = 15 if temperature > 50 else 40
        
        if wildfire_prob > alert_threshold:
            sendmsg("Jayanagar", wildfire_prob)
        
        # Dynamic risk display
        risk_color = "#ff0000" if wildfire_prob > 70 else "#ff9900" if wildfire_prob > 40 else "#00aa00"
        risk_class = "risk-high" if wildfire_prob > 70 else ""
        
        st.markdown(f"""
        <div style='background: rgba(30, 10, 0, 0.7); padding: 20px; border-radius: 10px; border-left: 5px solid {risk_color}; margin: 20px 0;' >
            <h2 class='{risk_class}' style='text-align: center; color: {risk_color};'>FIRE DANGER: {wildfire_prob:.1f}%</h2>
            <div style='height: 10px; background: linear-gradient(to right, #00aa00 0%, #ff9900 50%, #ff0000 100%); border-radius: 5px;'>
                <div style='width: {wildfire_prob}%; height: 100%; background: {risk_color}; border-radius: 5px;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- User Details (Futuristic Card) ---
with st.expander("🔒 Register for Emergency Alerts", expanded=False):
    with st.form("user_details"):
        st.write("OPTIONAL: Get notified if conditions worsen in your area")

        name = st.text_input("Full Name")
        phone = st.text_input("Phone Number")
        location = st.text_input("Your Location")

        submitted = st.form_submit_button("📡 Submit Information")

        if submitted:
            if name and location:
                # Validate phone number format: Must start with +91 and be followed by exactly 10 digits
                phone_pattern = r'^\+91\d{10}$'
                if phone and not re.match(phone_pattern, phone):
                    st.warning("Please enter a valid phone number (starts with +91 followed by 10 digits).")
                else:
                    # Update session state with the user details
                    st.session_state.user_data.update({
                        'name': name,
                        'phone': phone,
                        'location': location
                    })

                    # Always call save_to_mysql regardless of optional fields
                    try:
                        result = save_to_mysql(
                            phone=st.session_state.user_data.get('phone', ''),
                            name=st.session_state.user_data.get('name', ''),
                            location=st.session_state.user_data.get('location', ''),
                            temperature=st.session_state.user_data.get('temperature', None),
                            humidity=st.session_state.user_data.get('humidity', None),
                            pollution=st.session_state.user_data.get('pollution', None),
                            risk=st.session_state.user_data.get('risk', None)
                        )
                        if result:
                            st.success("Information saved successfully to database!")
                        else:
                            st.error("Failed to save information to database.")
                    except Exception as e:
                        st.error(f"Exception during DB save: {e}")
            else:
                st.warning("Please provide at least name and location")
