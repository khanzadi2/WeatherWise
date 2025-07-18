import streamlit as st
import requests
from datetime import datetime
import google.generativeai as genai  # Optional if you want Gemini
import json
import os


st.markdown("""
<!-- Load Font Awesome -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
""", unsafe_allow_html=True)

# --- API Configuration ---
API_KEY = "ca9c33ad9cd43017ab094ef9c7c249b3"  # OpenWeatherMap
OPENROUTER_API_KEY = "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"

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# --- Page Config ---
st.set_page_config(page_title="WeatherWise", page_icon="🌦️", layout="centered")

# --- CSS Styling ---
st.markdown("""<style>
            
            .stSidebar {
    background: #ff5ca3;
background: linear-gradient(83deg, rgba(255, 92, 163, 1) 0%, rgba(151, 77, 255, 1) 100%);
backdrop-filter: blur(10px);
    color: white; !important
    padding: 1rem;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.2);
}
             /* Common style for all notification types */
    div[data-testid="stNotification"] {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 16px !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
        margin-top: 20px !important;
    }

    div[data-testid="stNotification"] p {
        color: white !important;
        margin: 0 !important;
    }

    /* Green left border for success */
    div[data-testid="stNotification"][role="status"] {
        border-left: 6px solid #00cc88 !important;
    }

    /* Red left border for error */
    div[data-testid="stNotification"][role="alert"] {
        border-left: 6px solid #ff4d4d !important;
    }

    /* Yellow left border for warning */
    div[data-testid="stNotification"][role="warning"] {
        border-left: 6px solid #ffc107 !important;
    }
body, .stApp {
    background: radial-gradient(circle, rgba(204, 4, 87, 1) 0%, rgba(0, 78, 186, 1) 100%);
    color: white;
    font-family: 'Segoe UI', sans-serif;
}
.header {
    text-align: center;
    padding: 1rem 0;
    background: rgba(255,255,255,0.1);
    border-radius: 0 0 20px 20px;
    margin-bottom: 2rem;
}
.stTextInput > div > div > input {
    background-color: rgba(255,255,255,0.15);
    color: black;
    border: none;
    border-radius: 12px;
    padding: 12px;
}
.stRadio > div, .stRadio label, .stTextInput label {
    color: white !important;
    font-weight: 500;
}
.stRadio div[role="radiogroup"] > label {
    background-color: rgba(255,255,255,0.70);
    padding: 0.4rem 1rem;
    border-radius: 8px;
    margin-right: 0.5rem;
    cursor: pointer;
    
}
.report-container {
    background: rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 30px;
    margin: 20px 0;
    box-shadow: 0 8px 32px 0 rgba(31,38,135,0.2);
    backdrop-filter: blur(5px);
    border: 1px solid rgba(255,255,255,0.18);
}
.weather-icon {
    font-size: 90px;
    text-align: center;
    margin: 10px 0;
    text-shadow: 0 0 10px rgba(255,255,255,0.5);
}
.temp {
    font-size: 3.5rem;
    font-weight: 800;
    text-align: center;
    margin: 10px 0;
    text-shadow: 0 0 15px rgba(255,255,255,0.3);
}
.weather-desc {
    text-transform: capitalize;
    letter-spacing: 1px;
    text-align: center;
    font-size: 1.4rem;
    margin-bottom: 20px;
}
.details {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 20px;
    margin-top: 25px;
}
.detail-box {
    text-align: center;
    background: rgba(255,255,255,0.15);
    padding: 15px;
    border-radius: 12px;
    width: 140px;
    transition: all 0.3s ease;
}
.detail-box:hover {
    transform: translateY(-5px);
    background: rgba(255,255,255,0.25);
}
.metric-value {
    font-size: 1.3rem;
    font-weight: 700;
    margin-top: 5px;
}
.stButton>button {
    background-image: linear-gradient(to right, #FF8008 0%, #FFC837  51%, #FF8008  100%);
    margin: 10px;
    padding: 15px 30px;
    text-align: center;
    transition: 0.5s;
    background-size: 200% auto;
    color: black;
    border-radius: 10px;
    font-weight: bold;
    box-shadow: 0 0 20px #eee;
}
.stButton>button:hover {
    background-position: right center;
    color: #fff;
}
.navbar {
    background-color: rgba(255, 255, 255, 0.05);
    padding: 1rem 2rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.15);
}
.navbar h1 {
    color: white;
    font-size: 1.4rem;
    margin: 0;
}
.nav-links a {
    margin-left: 20px;
    text-decoration: none;
    color: #ffffff;
    font-weight: 500;
    padding: 6px 12px;
    border-radius: 8px;
    transition: background 0.3s ease;
}
.nav-links a:hover {
    background-color: rgba(255, 255, 255, 0.1);
}
.footer {
    text-align: center;
    margin-top: 40px;
    font-size: 0.9rem;
    color: rgba(255,255,255,0.6);
}

/* Make st.warning() alerts white */
div[data-testid="stNotification"] {
    background-color: rgba(255, 255, 255, 0.1) !important;
    border-left: 4px solid #FFD700 !important;
    color: white !important;
}
div[data-testid="stNotification"] code {
    color: white !important;
    background: none !important;
    font-weight: 500 !important;
    font-size: 1rem !important;
    text-shadow: 0 0 6px rgba(255,255,255,0.3) !important;
}
</style>
""", unsafe_allow_html=True)
st.markdown("""
<!-- Load Font Awesome -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

<style>
.social-bar {
    position: fixed;
    top: 50%;
    left: 15px;
    transform: translateY(-50%);
    z-index: 9999;
    display: flex;
    flex-direction: column;
    gap: 16px;
}
.social-bar a {
    background-color: white;
    color: black;
    font-size: 20px;
    padding: 12px;
    border-radius: 50%;
    width: 45px;
    height: 45px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-decoration: none;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    transition: all 0.3s ease;
}

/* Hover colors for each platform */
.social-bar a.facebook:hover {
    background-color: #1877F2; /* Facebook blue */
    color: white;
}
.social-bar a.whatsapp:hover {
    background-color: #25D366; /* WhatsApp green */
    color: white;
}
.social-bar a.instagram:hover {
    background: radial-gradient(circle at 30% 107%, #fdf497 0%, 
                #fdf497 5%, #fd5949 45%, #d6249f 60%, #285AEB 90%);
    color: white;
}
            
</style>

<!-- Social Icon Bar -->
<div class="social-bar">
    <a class="facebook" href="https://facebook.com/yourprofile" target="_blank" title="Facebook">
        <i class="fab fa-facebook-f"></i>
    </a>
    <a class="whatsapp" href="https://wa.me/923001234567" target="_blank" title="WhatsApp">
        <i class="fab fa-whatsapp"></i>
    </a>
    <a class="instagram" href="https://instagram.com/yourprofile" target="_blank" title="Instagram">
        <i class="fab fa-instagram"></i>
    </a>
</div>
""", unsafe_allow_html=True)



# --- Auth Functions ---
def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            return json.load(f)["users"]
    else:
        return []

def save_user(username, password):
    users = load_users()
    users.append({"username": username, "password": password})
    with open("users.json", "w") as f:
        json.dump({"users": users}, f, indent=4)

def authenticate(username, password):
    users = load_users()
    for user in users:
        if user["username"] == username and user["password"] == password:
            return True
    return False
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def show_login():
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if authenticate(username, password):
            st.success("Login successful!")
            st.session_state.logged_in = True
            st.session_state.username = username
        else:
            st.error("Invalid username or password")

def show_signup():
    st.title("🆕 Sign Up")
    username = st.text_input("Choose a username")
    password = st.text_input("Choose a password", type="password")
    if st.button("Sign Up"):
        save_user(username, password)
        st.success("Account created! Please log in.")
        st.rerun()

# --- Authentication Screen ---
if not st.session_state.logged_in:
    auth_choice = st.sidebar.selectbox("Login / Signup", ["Login", "Signup"])
    if auth_choice == "Login":
        show_login()
    else:
        show_signup()
    st.stop()  # Prevent rest of app from running
if st.session_state.logged_in:
    st.sidebar.write(f"👤 Logged in as: {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

# --- NAVBAR ---
st.markdown("""
<div class="navbar">
    <h1>🌦️ WeatherWise</h1>
    <div class="nav-links">
        <a href="#weather">Weather</a>
        <a href="#map">Map</a>
        <a href="#about">About</a>
    </div>
</div>
<!-- CSS here (same as yours, omitted for brevity) -->
""", unsafe_allow_html=True)
def ask_ai(weather_data, user_message):
    weather_info = (
        f"The current weather in {weather_data['location']['name']} is "
        f"{weather_data['current']['temp_c']}°C with {weather_data['current']['condition']['text']}, "
        f"humidity is {weather_data['current']['humidity']}% and wind speed is {weather_data['current']['wind_kph']} kph."
    )

    system_prompt = (
        f"{weather_info} Now respond to the user helpfully and naturally based on this weather. "
        f"User said: {user_message}"
    )

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://weatherwise.app",
        "X-Title": "WeatherWiseAI"
    }

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": system_prompt}
        ]
    }

    res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    return res.json()['choices'][0]['message']['content']


# --- Weather Icons ---
WEATHER_ICONS = {
    "01d": "☀️", "01n": "🌙", "02d": "⛅", "02n": "⛅",
    "03d": "☁️", "03n": "☁️", "04d": "☁️", "04n": "☁️",
    "09d": "🌧️", "09n": "🌧️", "10d": "🌦️", "10n": "🌦️",
    "11d": "⛈️", "11n": "⛈️", "13d": "❄️", "13n": "❄️",
    "50d": "🌫️", "50n": "🌫️"
}

# --- API CALL ---
def get_weather_data(location, units="metric"):
    params = {"q": location, "appid": API_KEY, "units": units}
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Error: {str(e)}")
        return None

# --- Header ---
st.markdown("<div class='header'><h1 id='weather'>🌦️ WeatherWise</h1><p>Real-Time Weather Forecast</p></div>", unsafe_allow_html=True)

# --- Form ---
unit = st.radio("Select Temperature Unit:", ["Celsius", "Fahrenheit"], horizontal=True, index=0)
unit_key = "imperial" if unit == "Fahrenheit" else "metric"
location = st.text_input("Enter City Name", placeholder="e.g., London, Tokyo, New York")

# --- Weather Data ---
if st.button("Get Weather") or location:
    if not location:
        st.warning("Please enter a city name")
    else:
        with st.spinner("Fetching weather..."):
            data = get_weather_data(location, unit_key)

        if data and data.get("cod") == 200:
            city = data["name"]
            country = data["sys"]["country"]
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]
            pressure = data["main"]["pressure"]
            description = data["weather"][0]["description"]
            icon = data["weather"][0]["icon"]
            sunrise = datetime.fromtimestamp(data["sys"]["sunrise"]).strftime('%H:%M')
            sunset = datetime.fromtimestamp(data["sys"]["sunset"]).strftime('%H:%M')

            # --- AI ALERTS ---
            alerts = []
            if (unit_key == "metric" and temp >= 38) or (unit_key == "imperial" and temp >= 100):
                alerts.append("⚠️ Extreme heat! Stay hydrated and stay indoors.")
            if (unit_key == "metric" and temp <= 5) or (unit_key == "imperial" and temp <= 40):
                alerts.append("❄️ Cold weather alert! Wear warm clothes.")
            if "rain" in description.lower() or "thunderstorm" in description.lower():
                alerts.append("🌧️ Rain expected. Carry an umbrella.")
            if "snow" in description.lower():
                alerts.append("❄️ Snowfall alert! Drive carefully.")
            if (unit_key == "metric" and wind_speed > 10) or (unit_key == "imperial" and wind_speed > 22):
                alerts.append("💨 Strong wind warning. Avoid outdoor activities.")

            for alert in alerts:
                st.warning(alert)

            # --- Weather Card ---
            st.markdown("<div class='report-container'>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='text-align:center'>{city}, {country}</h2>", unsafe_allow_html=True)
            st.markdown(f"<div class='weather-icon'>{WEATHER_ICONS.get(icon, '🌬️')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='temp'>{temp:.1f}°{'F' if unit == 'Fahrenheit' else 'C'}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='weather-desc'>{description}</div>", unsafe_allow_html=True)

            st.markdown(f"""
            <div class='details'>
                <div class='detail-box'>🌡️ Feels Like<br><div class='metric-value'>{feels_like:.1f}°</div></div>
                <div class='detail-box'>💧 Humidity<br><div class='metric-value'>{humidity}%</div></div>
                <div class='detail-box'>💨 Wind<br><div class='metric-value'>{wind_speed} {'mph' if unit == 'Fahrenheit' else 'm/s'}</div></div>
                <div class='detail-box'>📊 Pressure<br><div class='metric-value'>{pressure} hPa</div></div>
                <div class='detail-box'>🌅 Sunrise<br><div class='metric-value'>{sunrise}</div></div>
                <div class='detail-box'>🌇 Sunset<br><div class='metric-value'>{sunset}</div></div>
            </div>
            </div>
            """, unsafe_allow_html=True)

# --- Weather Map ---
st.markdown("<h2 id='map'>🌍 Live Weather Radar Map</h2>", unsafe_allow_html=True)
st.components.v1.html("""
<iframe width="100%" height="500" src="https://embed.windy.com/embed2.html?lat=30.3753&lon=69.3451&zoom=5&overlay=radar&menu=&message=true&marker=true&calendar=&type=map&location=coordinates&metricWind=default&metricTemp=default" frameborder="0"></iframe>
""", height=500)

# --- AI Chat Assistant ---
st.markdown("<h2 id='chat'>🤖 Ask WeatherWise</h2>", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": "You are a friendly weather assistant. Answer weather-related questions casually and clearly."}
    ]

user_input = st.text_input("Ask something about the weather...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://weatherwise.app",
            "X-Title": "WeatherWiseAI"
        }
        data = {
            "model": "openai/gpt-3.5-turbo",
            "messages": st.session_state.chat_history
        }
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        reply = response.json()["choices"][0]["message"]["content"]

        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.markdown(f"**You:** {user_input}")
        st.markdown(f"**WeatherWise AI:** {reply}")

    except Exception as e:
        st.error(f"Chat error: {str(e)}")

# --- About ---
st.markdown("<h2 id='about'>ℹ️ About</h2>", unsafe_allow_html=True)
st.markdown("""
This weather app is powered by the OpenWeatherMap API and built with Streamlit.  
It includes real-time forecasts, radar maps, and AI-generated weather alerts to help you plan better every day.
""")

# --- Footer ---
st.markdown("""<div class="footer">Powered by OpenWeatherMap API | WeatherWise © 2025</div>""", unsafe_allow_html=True)
