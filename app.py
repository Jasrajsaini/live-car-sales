
import random
import sqlite3
from datetime import datetime

import pandas as pd
import streamlit as st

# Page settings
st.set_page_config(
    page_title="Canadian Car Sales",
    layout="wide"
)

st.title(" Canadian Car Sales Dashboard")
st.caption("Live simulated car sales | Updated every 5 seconds")

DB_NAME = "car_sales.db"

# Sample car models and approximate base prices in CAD
car_models = {
    "Toyota": [("Camry", 35000), ("RAV4", 42000), ("Corolla", 28000)],
    "Honda": [("Civic", 30000), ("CR-V", 40000), ("Accord", 38000)],
    "Ford": [("F-150", 65000), ("Mustang", 55000), ("Escape", 38000)],
    "Chevrolet": [("Malibu", 32000), ("Equinox", 38000), ("Silverado", 65000)],
    "BMW": [("X3", 60000), ("3 Series", 55000), ("X5", 85000)],
    "Mercedes-Benz": [("C-Class", 60000), ("E-Class", 80000), ("GLC", 70000)],
    "Tesla": [("Model 3", 55000), ("Model Y", 65000)],
    "Hyundai": [("Elantra", 27000), ("Tucson", 38000), ("Santa Fe", 45000)],
    "Mazda": [("Mazda3", 29000), ("CX-5", 38000)],
    "Volkswagen": [("Jetta", 28000), ("Tiguan", 38000)],
    "Nissan": [("Sentra", 26000), ("Rogue", 37000)],
    "Kia": [("Sportage", 37000), ("Sorento", 44000)],
    "Porsche": [("Cayenne", 110000), ("Macan", 75000)],
    "Audi": [("A4", 55000), ("Q5", 65000)],
    "Lexus": [("RX", 70000), ("GX", 85000)],
    "Jeep": [("Wrangler", 55000), ("Grand Cherokee", 60000)],
    "Ram": [("Ram 1500", 65000), ("Ram 2500", 80000)],
    "GMC": [("Sierra", 70000), ("Acadia", 50000)],
    "Volvo": [("XC60", 65000), ("V60", 55000)],
    "Ferrari": [("296 GTB", 400000), ("Purosangue", 500000)]
}


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
        age = 2026 - year
        mileage = random.randint(age * 15000, age * 25000)
        age_factor = max(0.25, 0.90 ** age)
        mileage_factor = max(
            0.80, 1 - (mileage / 250000) * 0.15
        )
        estimated_price = base_price * age_factor * mileage_factor

    return (
        make,
        model,
        year,
        condition,
        mileage,
        round(estimated_price * 0.92),
        round(estimated_price * 1.08),
        datetime.now().isoformat()
    )


def save_sale(sale):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            INSERT INTO car_sales (
                Make, Model, Year, Condition, Mileage,
                Price_Low, Price_High, Date_Time
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, sale)


def load_sales():
    with sqlite3.connect(DB_NAME) as conn:
        return pd.read_sql_query(
            "SELECT * FROM car_sales ORDER BY id DESC",
            conn
        )


create_database()


@st.fragment(run_every="5s")
def live_dashboard():
    # Generate and save one simulated sale
    save_sale(generate_sale())

    df = load_sales()

    if df.empty:
        st.info("Waiting for sales...")
        return

    # Dashboard metrics
    total_sales = len(df)
    average_price = df["Price_Low"].mean()
    highest_price = df["Price_High"].max()
    used_sales = (df["Condition"] == "Used").sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Sales", f"{total_sales:,}")
    col2.metric("Average Low Price", f"${average_price:,.0f}")
    col3.metric("Highest High Price", f"${highest_price:,.0f}")
    col4.metric("Used Cars", f"{used_sales:,}")

    st.subheader("Sales by Make")
    sales_by_make = df.groupby("Make").size().sort_values(
        ascending=False
    )
    st.bar_chart(sales_by_make)

    st.subheader("Latest Car Sales")

    display_df = df.head(50).copy()
    display_df["Price_Low"] = display_df["Price_Low"].map(
        lambda x: f"${x:,.0f}"
    )
    display_df["Price_High"] = display_df["Price_High"].map(
        lambda x: f"${x:,.0f}"
    )

    st.dataframe(display_df, use_container_width=True, hide_index=True)


live_dashboard()

