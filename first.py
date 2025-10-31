
import streamlit as st
import requests
import datetime
import matplotlib.pyplot as plt

# API Key
API_KEY = "a430b3e0016974d8b94ff7b16d445b07"

# Streamlit Config
st.set_page_config(page_title="Weather App", page_icon="⛅", layout="wide")

# Function to get location from IP
def get_location():
    try:
        res = requests.get("https://ipinfo.io/json")
        if res.status_code == 200:
            data = res.json()
            return data.get("city", "Delhi")  # fallback: Delhi
    except:
        return "Delhi"

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []
if "favorites" not in st.session_state:
    st.session_state.favorites = []

# Sidebar: Unit Switcher
st.sidebar.header("⚙️ Settings")
unit = st.sidebar.radio("Temperature Unit", ("Celsius (°C)", "Fahrenheit (°F)"))
unit_param = "metric" if "Celsius" in unit else "imperial"
unit_symbol = "°C" if unit_param == "metric" else "°F"

# Sidebar: Favorites Section
st.sidebar.header("⭐ Favorite Cities")
if st.session_state.favorites:
    for fav_city in st.session_state.favorites:
        fav_url = f"http://api.openweathermap.org/data/2.5/weather?q={fav_city}&appid={API_KEY}&units={unit_param}"
        fav_res = requests.get(fav_url)
        if fav_res.status_code == 200:
            fav_data = fav_res.json()
            fav_temp = fav_data["main"]["temp"]
            fav_icon = fav_data["weather"][0]["icon"]
            st.sidebar.write(f"**{fav_city}**: {fav_temp}{unit_symbol}")
            st.sidebar.image(f"http://openweathermap.org/img/wn/{fav_icon}.png", width=40)
else:
    st.sidebar.write("No favorites yet.")

# Sidebar: Add Favorite
fav_input = st.sidebar.text_input("➕ Add to Favorites")
if st.sidebar.button("Add City"):
    if fav_input and fav_input not in st.session_state.favorites:
        st.session_state.favorites.append(fav_input)

# Sidebar: Search History
st.sidebar.header("📜 Search History")
selected_city = None
if st.session_state.history:
    selected_city = st.sidebar.selectbox("Choose a city:", st.session_state.history)

# Main App
st.title("🌍 Real-Time Weather Dashboard")
st.write("Get current weather and 5-day forecast (auto-detects your location 🌐)")

# Detect default location
default_city = get_location()
user_city = st.text_input("Enter City Name (Auto-detected 👇)", default_city)

# Determine city
city = user_city or default_city
if st.button("Get Weather"):
    city = user_city
    if city not in st.session_state.history:
        st.session_state.history.insert(0, city)

if selected_city:
    city = selected_city

# =======================
# Weather API Calls
# =======================
weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units={unit_param}"
forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units={unit_param}"

weather_res = requests.get(weather_url)
forecast_res = requests.get(forecast_url)

if weather_res.status_code == 200 and forecast_res.status_code == 200:
    # Parse current weather
    weather_data = weather_res.json()
    forecast_data = forecast_res.json()

    temp = weather_data["main"]["temp"]
    desc = weather_data["weather"][0]["description"].title()
    main_condition = weather_data["weather"][0]["main"]
    icon = weather_data["weather"][0]["icon"]
    humidity = weather_data["main"]["humidity"]
    wind = weather_data["wind"]["speed"]

    # Show current weather
    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader(f"📍 Weather in {city}")
        st.metric(f"🌡 Temperature ({unit_symbol})", f"{temp}{unit_symbol}")
        st.write(f"☁️ Condition: {desc}")
        st.write(f"💧 Humidity: {humidity}%")
        st.write(f"🌬 Wind Speed: {wind} {'m/s' if unit_param=='metric' else 'mph'}")
    with col2:
        st.image(f"http://openweathermap.org/img/wn/{icon}@2x.png")

    # Process 5-day forecast (closest to noon each day)
    daily_forecast = {}
    for item in forecast_data["list"]:
        date = datetime.datetime.fromtimestamp(item["dt"])
        day = date.date()
        hour = date.hour
        # pick the forecast closest to 12:00
        if day not in daily_forecast or abs(hour - 12) < abs(daily_forecast[day]["hour"] - 12):
            daily_forecast[day] = {"hour": hour, "temp": item["main"]["temp"]}

    dates = list(daily_forecast.keys())
    temps = [info["temp"] for info in daily_forecast.values()]

    # Forecast Chart
    st.subheader(f"📊 5-Day Temperature Forecast ({unit_symbol})")
    fig, ax = plt.subplots()
    ax.plot(dates, temps, marker="o", linestyle="-", color="orange")
    ax.set_xlabel("Date")
    ax.set_ylabel(f"Temperature ({unit_symbol})")
    ax.set_title(f"5-Day Forecast for {city}")
    st.pyplot(fig)

    # Add quick "Add to Favorites" button
    if st.button("⭐ Add This City to Favorites"):
        if city not in st.session_state.favorites:
            st.session_state.favorites.append(city)

else:
    st.error("❌ City not found. Please try again!")
