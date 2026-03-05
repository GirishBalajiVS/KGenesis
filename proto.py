# ==========================================================
# GLOBAL CLIMATE RISK INTELLIGENCE SYSTEM
# Hackathon Premium AI Version
# ==========================================================

import streamlit as st
import requests
import sqlite3
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from streamlit_geolocation import streamlit_geolocation

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Climate Risk AI",
    page_icon="🌍",
    layout="wide"
)

# ==========================================================
# CUSTOM CSS
# ==========================================================

st.markdown("""
<style>

body{
background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
color:white;
}

.center-box{
display:flex;
justify-content:center;
margin-top:20px;
}

.stSelectbox{
width:350px !important;
}

.metric-box{
padding:15px;
border-radius:10px;
background:rgba(255,255,255,0.05);
box-shadow:0 0 10px rgba(0,0,0,0.4);
animation:fade 1s;
}

@keyframes fade{
from{opacity:0; transform:translateY(15px)}
to{opacity:1; transform:translateY(0)}
}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# API CONFIG
# ==========================================================

API_KEY = "a7373fd6426dd7def52c342f661485b8"

# ==========================================================
# DATABASE
# ==========================================================

def create_db():

    conn = sqlite3.connect("climate_ai.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT,
        temperature REAL,
        humidity REAL,
        wind REAL,
        rainfall REAL,
        risk TEXT,
        lat REAL,
        lon REAL,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_alert(city,temp,humidity,wind,rain,risk,lat,lon):

    conn = sqlite3.connect("climate_ai.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO alerts(
    city,temperature,humidity,wind,rainfall,risk,lat,lon,timestamp
    )
    VALUES(?,?,?,?,?,?,?,?,?)
    """,(city,temp,humidity,wind,rain,risk,lat,lon,str(datetime.now())))

    conn.commit()
    conn.close()


def load_data():

    conn = sqlite3.connect("climate_ai.db")

    df = pd.read_sql_query(
        "SELECT * FROM alerts",
        conn
    )

    conn.close()

    return df


# ==========================================================
# WEATHER API
# ==========================================================

def get_weather(city):

    url=f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    try:

        r=requests.get(url)

        if r.status_code!=200:
            return None

        data=r.json()

        temp=data["main"]["temp"]
        humidity=data["main"]["humidity"]
        wind=data["wind"]["speed"]

        lat=data["coord"]["lat"]
        lon=data["coord"]["lon"]

        rain=0
        if "rain" in data:
            rain=data["rain"].get("1h",0)

        return temp,humidity,wind,rain,lat,lon

    except:
        return None


# WEATHER USING GPS

def get_weather_by_coords(lat,lon):

    url=f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

    r=requests.get(url)
    data=r.json()

    temp=data["main"]["temp"]
    humidity=data["main"]["humidity"]
    wind=data["wind"]["speed"]

    rain=0
    if "rain" in data:
        rain=data["rain"].get("1h",0)

    city=data["name"]

    return city,temp,humidity,wind,rain


# ==========================================================
# AI RISK ENGINE
# ==========================================================

def calculate_risk(temp,humidity,wind,rain):

    score=(temp*0.35)+(humidity*0.15)+(wind*3)+(rain*4)

    if score>150:
        risk="Extreme Flood Risk"

    elif score>110:
        risk="Storm Risk"

    elif score>80:
        risk="Heatwave Risk"

    else:
        risk="Normal"

    return risk,score


# ==========================================================
# FUTURE PREDICTION
# ==========================================================

def predict_future(temp,humidity,wind,rain):

    temp=temp*1.05
    wind=wind*1.1
    rain=rain*1.15

    risk,_=calculate_risk(temp,humidity,wind,rain)

    return risk


# ==========================================================
# AI DISASTER PROBABILITY
# ==========================================================

def disaster_probability(temp,humidity,wind,rain):

    flood=min((rain*12 + humidity*0.5),100)
    storm=min((wind*10 + humidity*0.4),100)
    heat=min((temp*2 + humidity*0.3),100)

    return {
        "Flood":round(flood,2),
        "Storm":round(storm,2),
        "Heatwave":round(heat,2)
    }


# ==========================================================
# AI RISK INDEX
# ==========================================================

def risk_index(score):

    index=min(score/2,100)

    return round(index,2)


# ==========================================================
# AI ALERT GENERATOR
# ==========================================================

def generate_alert(city,risk):

    if risk=="Extreme Flood Risk":

        return f"""
🚨 Extreme Flood Warning for {city}

Heavy rainfall and humidity detected.
Authorities should prepare evacuation plans.
"""

    elif risk=="Storm Risk":

        return f"""
⚠️ Storm Alert for {city}

High wind speeds may cause storms.
Citizens should remain cautious.
"""

    elif risk=="Heatwave Risk":

        return f"""
🔥 Heatwave Alert in {city}

Extreme temperatures may cause health risks.
Stay hydrated and avoid outdoor exposure.
"""

    else:

        return f"""
✅ Climate conditions in {city} are stable.
No major risks detected.
"""


# ==========================================================
# CITY AUTO SUGGESTION
# ==========================================================

@st.cache_data
def load_cities():

    url="https://raw.githubusercontent.com/datasets/world-cities/master/data/world-cities.csv"

    df=pd.read_csv(url)

    return sorted(df["name"].unique())


# ==========================================================
# GLOBAL MAP
# ==========================================================

def global_map():

    st.title("🌎 Global Climate Monitoring")

    df=load_data()

    if df.empty:
        st.info("No data yet")
        return

    fig=px.scatter_geo(
        df,
        lat="lat",
        lon="lon",
        color="risk",
        hover_name="city",
        title="Global Climate Risk Map"
    )

    st.plotly_chart(fig,use_container_width=True)


# ==========================================================
# GOVERNMENT ANALYTICS
# ==========================================================

def analytics_dashboard():

    st.title("📊 Government Climate Analytics")

    df=load_data()

    if df.empty:
        st.info("No data available")
        return

    col1,col2,col3=st.columns(3)

    col1.metric("Total Alerts",len(df))
    col2.metric("High Risk Cities",len(df[df["risk"]!="Normal"]))
    col3.metric("Cities Monitored",df["city"].nunique())

    st.dataframe(df,use_container_width=True)

    fig=px.pie(df,names="risk",title="Risk Distribution")

    st.plotly_chart(fig)


# ==========================================================
# MAIN DASHBOARD
# ==========================================================

def dashboard():

    st.title("🌍 Climate Risk AI Monitoring System")

    # LIVE LOCATION

    st.subheader("📍 Detect Risk Using Live Location")

    location = streamlit_geolocation()

    if location:

        lat = location["latitude"]
        lon = location["longitude"]

        if lat and lon:

            city,temp,humidity,wind,rain = get_weather_by_coords(lat,lon)

            risk,score=calculate_risk(temp,humidity,wind,rain)

            future=predict_future(temp,humidity,wind,rain)

            prob=disaster_probability(temp,humidity,wind,rain)

            index=risk_index(score)

            alert=generate_alert(city,risk)

            save_alert(city,temp,humidity,wind,rain,risk,lat,lon)

            st.success(f"Live Location Detected: {city}")

            col1,col2,col3,col4=st.columns(4)

            col1.metric("Temperature",f"{temp} °C")
            col2.metric("Humidity",f"{humidity} %")
            col3.metric("Wind",f"{wind} m/s")
            col4.metric("Rainfall",f"{rain} mm")

            st.info(alert)

            fig=go.Figure(go.Indicator(
            mode="gauge+number",
            value=index,
            title={'text':"AI Climate Risk Index"},
            gauge={'axis':{'range':[0,100]}}
            ))

            st.plotly_chart(fig,use_container_width=True)

            prob_df=pd.DataFrame({
            "Disaster":list(prob.keys()),
            "Probability":list(prob.values())
            })

            fig2=px.bar(prob_df,x="Disaster",y="Probability",title="Disaster Probability (%)")

            st.plotly_chart(fig2)

            trend_df=pd.DataFrame({
            "Parameter":["Temperature","Humidity","Wind","Rainfall"],
            "Value":[temp,humidity,wind,rain]
            })

            fig3=px.line(trend_df,x="Parameter",y="Value",markers=True,title="Climate Parameter Trend")

            st.plotly_chart(fig3)

            st.map(pd.DataFrame({"lat":[lat],"lon":[lon]}))


    # ======================================================
    # CITY SEARCH (CENTERED)
    # ======================================================

    st.subheader("🔎 Search Any City")

    cities=load_cities()

    left,center,right=st.columns([1,2,1])

    with center:
        city=st.selectbox("Select City",cities)

    if city:

        weather=get_weather(city)

        if weather is None:
            st.error("City not found")
            return

        temp,humidity,wind,rain,lat,lon=weather

        risk,score=calculate_risk(temp,humidity,wind,rain)

        future=predict_future(temp,humidity,wind,rain)

        save_alert(city,temp,humidity,wind,rain,risk,lat,lon)

        col1,col2,col3,col4=st.columns(4)

        col1.metric("Temperature",f"{temp} °C")
        col2.metric("Humidity",f"{humidity} %")
        col3.metric("Wind",f"{wind} m/s")
        col4.metric("Rainfall",f"{rain} mm")

        st.info(f"Future Prediction: {future}")

        st.map(pd.DataFrame({"lat":[lat],"lon":[lon]}))


# ==========================================================
# ALERT HISTORY
# ==========================================================

def history():

    st.title("📁 Alert History")

    df=load_data()

    if df.empty:
        st.info("No alerts yet")

    else:

        st.dataframe(df,use_container_width=True)

        st.download_button(
            label="Download Climate Report",
            data=df.to_csv(index=False),
            file_name="climate_report.csv",
            mime="text/csv"
        )


# ==========================================================
# APP START
# ==========================================================

create_db()

menu=st.sidebar.selectbox(
    "Navigation",
    [
        "Dashboard",
        "Global Map",
        "Government Analytics",
        "Alert History"
    ]
)

if menu=="Dashboard":
    dashboard()

elif menu=="Global Map":
    global_map()

elif menu=="Government Analytics":
    analytics_dashboard()

elif menu=="Alert History":

    history()
