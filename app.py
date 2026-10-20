
import random
import sqlite3
from datetime import datetime

import pandas as pd
import streamlit as st

# PAGE SETTINGS

st.set_page_config(
    page_title="Canadian Auto Market",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DB_NAME = "car_sales.db"

# SHOWROOM DESIGN


st.markdown("""
<style>
    .stApp {
        background-color: #101820;
        color: #F5F7FA;
    }

    [data-testid="stHeader"] {
        background-color: #101820;
    }

    .block-container {
        max-width: 1150px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .brand {
        font-size: 29px;
        font-weight: 800;
        letter-spacing: 2px;
        color: #FFFFFF;
    }

    .subtitle {
        color: #AAB8C5;
        font-size: 13px;
        letter-spacing: 3px;
    }

    .live {
        color: #48E0A4;
        font-weight: 700;
        font-size: 14px;
    }

    .eyebrow {
        color: #AAB8C5;
        font-size: 12px;
        letter-spacing: 3px;
        margin-top: 25px;
    }

    .car-title {
        color: #FFFFFF;
        font-size: clamp(30px, 5vw, 48px);
        font-weight: 800;
        line-height: 1.15;
        margin: 8px 0;
    }

    .car-details {
        color: #C2CDD7;
        font-size: 16px;
        margin-bottom: 22px;
    }

    .price {
        color: #FFFFFF;
        font-size: clamp(27px, 4vw, 38px);
        font-weight: 750;
        margin-top: 10px;
    }

    .price-label {
        color: #AAB8C5;
        font-size: 12px;
        letter-spacing: 2px;
    }

    .sale-card {
        background: #192630;
        border: 1px solid #30404C;
        border-radius: 16px;
        padding: 22px;
        margin: 12px 0;
    }

    .section-heading {
        color: #FFFFFF;
        font-size: 22px;
        font-weight: 700;
        margin-top: 35px;
        margin-bottom: 8px;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #30404C;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# CAR MODELS AND ESTIMATED BASE PRICES (CAD)

car_models = {
    "Toyota": [
        ("Camry", 35000),
        ("RAV4", 42000),
        ("Corolla", 28000),
        ("4Runner", 55000),
        ("Sequoia", 85000)
    ],
    "Honda": [
        ("Civic", 30000),
        ("CR-V", 40000),
        ("Accord", 38000),
        ("Odyssey", 50000)
    ],
    "Ford": [
        ("F-150", 65000),
        ("Mustang", 55000),
        ("Escape", 38000),
        ("Bronco", 55000),
        ("Expedition", 85000)
    ],
    "Chevrolet": [
        ("Malibu", 32000),
        ("Equinox", 38000),
        ("Silverado", 65000),
        ("Corvette", 100000)
    ],
    "BMW": [
        ("X1", 50000),
        ("X3", 65000),
        ("3 Series", 60000),
        ("7 Series", 120000)
    ],
    "Mercedes-Benz": [
        ("C-Class", 60000),
        ("E-Class", 80000),
        ("EQS Sedan", 120000),
        ("GLC", 70000)
    ],
    "Tesla": [
        ("Model 3", 55000),
        ("Model Y", 65000),
        ("Model S", 110000)
    ],
    "Hyundai": [
        ("Elantra", 27000),
        ("Tucson", 38000),
        ("Santa Fe", 45000),
        ("Kona", 30000)
    ],
    "Mazda": [
        ("Mazda3", 29000),
        ("CX-5", 38000),
        ("MX-5 Miata", 40000)
    ],
    "Volkswagen": [
        ("Jetta", 28000),
        ("Tiguan", 38000),
        ("Atlas", 50000)
    ],
    "Nissan": [
        ("Sentra", 26000),
        ("Rogue", 37000),
        ("Pathfinder", 50000)
    ],
    "Kia": [
        ("Sportage", 37000),
        ("Sorento", 44000),
        ("Telluride", 52000)
    ],
    "Porsche": [
        ("Cayenne", 110000),
        ("Macan", 75000),
        ("911", 150000)
    ],
    "Audi": [
        ("A4", 55000),
        ("Q5", 65000),
        ("A7", 90000)
    ],
    "Lexus": [
        ("RX", 70000),
        ("GX", 85000),
        ("TX", 75000)
    ],
    "Jeep": [
        ("Wrangler", 55000),
        ("Grand Cherokee", 60000),
        ("Cherokee", 40000)
    ],
    "Ram": [
        ("Ram 1500", 65000),
        ("Ram 2500", 80000),
        ("Ram 3500", 90000)
    ],
    "GMC": [
        ("Sierra", 70000),
        ("Acadia", 50000),
        ("Hummer EV", 110000)
    ],
    "Volvo": [
        ("XC60", 65000),
        ("V60", 55000)
    ],
    "Ferrari": [
        ("296 GTB", 400000),
        ("Purosangue", 500000)
    ]
}


# DATABASE

def create_database():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS car_sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Make TEXT,
                Model TEXT,
                Year INTEGER,
                Condition TEXT,
                Mileage INTEGER,
                Price_Low REAL,
                Price_High REAL,
                Date_Time TEXT
            )
        """)


def generate_sale():
    make = random.choice(list(car_models.keys()))
    model, base_price = random.choice(car_models[make])
    year = random.randint(2015, 2026)

    if year >= 2025:
        condition = "New"
        mileage = random.randint(0, 200)
        estimated_price = base_price
    else:
        condition = "Used"
        car_age = 2026 - year

        mileage = random.randint(
            car_age * 15000,
            car_age * 25000
        )

        age_factor = max(0.25, 0.90 ** car_age)
        mileage_factor = max(
            0.80,
            1 - (mileage / 250000) * 0.15
        )

        estimated_price = (
            base_price * age_factor * mileage_factor
        )

    return {
        "Make": make,
        "Model": model,
        "Year": year,
        "Condition": condition,
        "Mileage": mileage,
        "Price_Low": round(estimated_price * 0.92),
        "Price_High": round(estimated_price * 1.08),
        "Date_Time": datetime.now().isoformat(timespec="seconds")
    }


def save_sale(sale):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            INSERT INTO car_sales (
                Make, Model, Year, Condition, Mileage,
                Price_Low, Price_High, Date_Time
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sale["Make"],
            sale["Model"],
            sale["Year"],
            sale["Condition"],
            sale["Mileage"],
            sale["Price_Low"],
            sale["Price_High"],
            sale["Date_Time"]
        ))


def load_sales():
    with sqlite3.connect(DB_NAME) as conn:
        return pd.read_sql_query("""
            SELECT *
            FROM car_sales
            ORDER BY id DESC
        """, conn)


# HEADER

create_database()

header_left, header_right = st.columns([5, 1])

with header_left:
    st.markdown(
        '<div class="brand">CANADIAN AUTO MARKET</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="subtitle">YOUR NEXT RIDE STARTS HERE</div>',
        unsafe_allow_html=True
    )

with header_right:
    st.markdown(
        '<div class="live">● LIVE</div>',
        unsafe_allow_html=True
    )

st.divider()

# LIVE SHOWROOM
# A new simulated listing is created every 20 seconds.

@st.fragment(run_every="20s")
def showroom():
    # Create one new simulated listing per refresh
    sale = generate_sale()
    save_sale(sale)

    st.markdown(
        '<div class="eyebrow">LATEST VEHICLE LISTING</div>',
        unsafe_allow_html=True
    )

    photo_col, details_col = st.columns(
        [1.15, 1],
        gap="large",
        vertical_alignment="center"
    )

    with photo_col:
        # Decorative showroom photo; it may not match
        # the exact make and model being displayed.
        st.image(
            "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7"
            "?auto=format&fit=crop&w=1200&q=85",
            use_container_width=True
        )

    with details_col:
        st.markdown(
            f'<div class="car-title">{sale["Year"]} '
            f'{sale["Make"]} {sale["Model"]}</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="car-details">'
            f'{sale["Condition"].upper()} &nbsp; • &nbsp; '
            f'{sale["Mileage"]:,} km'
            f'</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="price-label">ESTIMATED PRICE RANGE · CAD</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="price">'
            f'${sale["Price_Low"]:,.0f} – '
            f'${sale["Price_High"]:,.0f}'
            f'</div>',
            unsafe_allow_html=True
        )

        st.caption(
            "Illustrative estimate for this simulated listing."
        )

        st.markdown(
            f'<div class="sale-card">'
            f'<b>Model year</b><br>{sale["Year"]}<br><br>'
            f'<b>Condition</b><br>{sale["Condition"]}<br><br>'
            f'<b>Mileage</b><br>{sale["Mileage"]:,} km'
            f'</div>',
            unsafe_allow_html=True
        )

    st.caption("A new simulated listing appears approximately every 20 seconds.")

    # Previous listings
    st.markdown(
        '<div class="section-heading">Recently Featured Vehicles</div>',
        unsafe_allow_html=True
    )

    history = load_sales()

    if not history.empty:
        history = history.head(5).copy()
        history["Price Range (CAD)"] = history.apply(
            lambda row: (
                f'${row["Price_Low"]:,.0f} – '
                f'${row["Price_High"]:,.0f}'
            ),
            axis=1
        )

        history = history.rename(columns={
            "Make": "Make",
            "Model": "Model",
            "Year": "Year",
            "Condition": "Condition",
            "Mileage": "Mileage (km)"
        })

        st.dataframe(
            history[[
                "Make", "Model", "Year", "Condition",
                "Mileage (km)", "Price Range (CAD)"
            ]],
            use_container_width=True,
            hide_index=True
        )

showroom()

st.markdown("---")
st.caption(
    "Canadian Auto Market · Demonstration project · "
    "All listings and prices are simulated, not live dealership offers."
)
