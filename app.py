
import random
import sqlite3
import math
from datetime import datetime

import pandas as pd
import streamlit as st

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Canadian Auto Market",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DB = "car_sales.db"

st.markdown("""
<style>
.stApp {
    background: #101820;
    color: #F5F7FA;
}
[data-testid="stHeader"] {
    background: #101820;
}
.block-container {
    max-width: 1250px;
    padding-top: 2rem;
}
.brand {
    font-size: 28px;
    font-weight: 850;
    letter-spacing: 2px;
    color: white;
}
.muted {
    color: #B5C2CD;
}
.price {
    font-size: 30px;
    font-weight: 800;
    color: white;
}
.vehicle-card {
    background: #192630;
    border: 1px solid #344550;
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# INVENTORY
# --------------------------------------------------

models = {
    "Toyota": [
        ("RAV4", 42000), ("Corolla", 28000),
        ("Camry", 35000), ("4Runner", 55000)
    ],
    "Honda": [
        ("Civic", 30000), ("CR-V", 40000),
        ("Accord", 38000), ("Odyssey", 50000)
    ],
    "Ford": [
        ("F-150", 65000), ("Mustang", 55000),
        ("Escape", 38000), ("Bronco", 55000)
    ],
    "BMW": [
        ("X3", 65000), ("3 Series", 60000),
        ("7 Series", 120000)
    ],
    "Mercedes-Benz": [
        ("C-Class", 60000), ("E-Class", 80000),
        ("EQS Sedan", 120000)
    ],
    "Tesla": [
        ("Model 3", 55000), ("Model Y", 65000)
    ],
    "Hyundai": [
        ("Elantra", 27000), ("Tucson", 38000),
        ("Santa Fe", 45000)
    ],
    "Mazda": [
        ("Mazda3", 29000), ("CX-5", 38000)
    ],
    "Volkswagen": [
        ("Jetta", 28000), ("Tiguan", 38000)
    ],
    "Nissan": [
        ("Sentra", 26000), ("Rogue", 37000)
    ],
    "Kia": [
        ("Sportage", 37000), ("Sorento", 44000)
    ],
    "Porsche": [
        ("Cayenne", 110000), ("Macan", 75000)
    ],
    "Audi": [
        ("A4", 55000), ("Q5", 65000)
    ],
    "Lexus": [
        ("RX", 70000), ("GX", 85000)
    ],
    "Jeep": [
        ("Wrangler", 55000), ("Grand Cherokee", 60000)
    ],
    "Ram": [
        ("Ram 1500", 65000), ("Ram 2500", 80000)
    ],
    "GMC": [
        ("Sierra", 70000), ("Acadia", 50000)
    ],
    "Volvo": [
        ("XC60", 65000), ("V60", 55000)
    ],
    "Ferrari": [
        ("296 GTB", 400000), ("Purosangue", 500000)
    ],
    "Chevrolet": [
        ("Equinox", 38000), ("Silverado", 65000)
    ],
}

# Generic showroom photo. Replace with verified vehicle
# photos later so each photo matches its exact model.
CAR_PHOTO = (
    "https://images.unsplash.com/"
    "photo-1492144534655-ae79c964c9d7"
    "?auto=format&fit=crop&w=1200&q=85"
)


def connect():
    return sqlite3.connect(DB)


def create_database():
    with connect() as conn:
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


def make_vehicle(make, model, base_price):
    year = random.randint(2015, 2026)

    if year >= 2025:
        condition = "New"
        mileage = random.randint(0, 200)
        estimate = base_price
    else:
        condition = "Used"
        age = 2026 - year
        mileage = random.randint(age * 15000, age * 25000)
        age_factor = max(0.25, 0.90 ** age)
        mileage_factor = max(
            0.80, 1 - (mileage / 250000) * 0.15
        )
        estimate = base_price * age_factor * mileage_factor

    low = round(estimate * 0.92)
    high = round(estimate * 1.08)

    return (
        make, model, year, condition, mileage,
        low, high, datetime.now().isoformat(timespec="seconds")
    )


def seed_inventory():
    """Create demo inventory only when the database is empty."""
    with connect() as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM car_sales"
        ).fetchone()[0]

        if count == 0:
            vehicles = []

            for _ in range(24):
                make = random.choice(list(models.keys()))
                model, base = random.choice(models[make])
                vehicles.append(make_vehicle(make, model, base))

            conn.executemany("""
                INSERT INTO car_sales (
                    Make, Model, Year, Condition, Mileage,
                    Price_Low, Price_High, Date_Time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, vehicles)


def load_inventory():
    with connect() as conn:
        return pd.read_sql_query(
            "SELECT * FROM car_sales ORDER BY id DESC", conn
        )


create_database()
seed_inventory()

if "page" not in st.session_state:
    st.session_state.page = "Browse"

if "vehicle_id" not in st.session_state:
    st.session_state.vehicle_id = None

if "payment_type" not in st.session_state:
    st.session_state.payment_type = "Finance"

# --------------------------------------------------
# NAVIGATION
# --------------------------------------------------

header, nav = st.columns([4, 1])

with header:
    st.markdown(
        '<div class="brand">CANADIAN AUTO MARKET</div>',
        unsafe_allow_html=True,
    )
    st.caption("Find your next ride.")

with nav:
    if st.button("🏠 Browse cars", use_container_width=True):
        st.session_state.page = "Browse"
        st.rerun()

st.divider()

df = load_inventory()

# --------------------------------------------------
# BROWSE PAGE
# --------------------------------------------------

if st.session_state.page == "Browse":

    st.title("Find your next car")
    st.write(
        "Explore our sample vehicle listings at your own pace."
    )

    search = st.text_input(
        "Search vehicles",
        placeholder="Try Toyota, Civic, BMW..."
    )

    f1, f2, f3 = st.columns(3)

    makes_list = ["All makes"] + sorted(df["Make"].unique().tolist())

    selected_make = f1.selectbox("Make", makes_list)
    selected_condition = f2.selectbox(
        "Condition", ["All", "New", "Used"]
    )
    max_price = f3.selectbox(
        "Maximum price",
        [50000, 75000, 100000, 150000, 300000, 1000000],
        index=3,
        format_func=lambda x: f"${x:,.0f}"
    )

    filtered = df.copy()

    if search.strip():
        match = (
            filtered["Make"].str.contains(search, case=False, na=False)
            | filtered["Model"].str.contains(search, case=False, na=False)
        )
        filtered = filtered[match]

    if selected_make != "All makes":
        filtered = filtered[filtered["Make"] == selected_make]

    if selected_condition != "All":
        filtered = filtered[
            filtered["Condition"] == selected_condition
        ]

    filtered = filtered[filtered["Price_Low"] <= max_price]

    st.caption(f"{len(filtered)} vehicles found")

    if filtered.empty:
        st.info("No vehicles match your filters. Try changing them.")
    else:
        for start in range(0, len(filtered), 2):
            cols = st.columns(2)

            for col, (_, car) in zip(
                cols, filtered.iloc[start:start + 2].iterrows()
            ):
                with col:
                    st.image(CAR_PHOTO, use_container_width=True)

                    st.subheader(
                        f'{int(car["Year"])} '
                        f'{car["Make"]} {car["Model"]}'
                    )

                    st.write(
                        f'{car["Condition"]} · '
                        f'{int(car["Mileage"]):,} km'
                    )

                    st.markdown(
                        f'<div class="price">'
                        f'${car["Price_Low"]:,.0f} – '
                        f'${car["Price_High"]:,.0f}</div>',
                        unsafe_allow_html=True,
                    )

                    st.caption("Estimated price range · CAD")

                    if st.button(
                        "View vehicle details →",
                        key=f'view_{int(car["id"])}',
                        use_container_width=True,
                    ):
                        st.session_state.vehicle_id = int(car["id"])
                        st.session_state.page = "Details"
                        st.rerun()

# --------------------------------------------------
# VEHICLE DETAILS PAGE
# --------------------------------------------------

elif st.session_state.page == "Details":

    matches = df[df["id"] == st.session_state.vehicle_id]

    if matches.empty:
        st.warning("This vehicle could not be found.")
        if st.button("Back to vehicles"):
            st.session_state.page = "Browse"
            st.rerun()
    else:
        car = matches.iloc[0]

        st.caption("VEHICLE DETAILS")

        left, right = st.columns([1.1, 1])

        with left:
            st.image(CAR_PHOTO, use_container_width=True)

        with right:
            st.title(
                f'{int(car["Year"])} {car["Make"]} {car["Model"]}'
            )
            st.markdown(
                f'<div class="price">'
                f'${car["Price_Low"]:,.0f} – '
                f'${car["Price_High"]:,.0f}</div>',
                unsafe_allow_html=True,
            )
            st.caption("Estimated price range in CAD")

            st.write(f'**Condition:** {car["Condition"]}')
            st.write(f'**Mileage:** {int(car["Mileage"]):,} km')
            st.write(f'**Model year:** {int(car["Year"])}')

            st.info(
                "This is a sample listing with simulated vehicle "
                "details and estimated pricing."
            )

            if st.button(
                "Explore payment options →",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.page = "Payments"
                st.rerun()

            if st.button("← Back to all vehicles"):
                st.session_state.page = "Browse"
                st.rerun()

# --------------------------------------------------
# PAYMENT PAGE
# --------------------------------------------------

elif st.session_state.page == "Payments":

    matches = df[df["id"] == st.session_state.vehicle_id]

    if matches.empty:
        st.warning("Vehicle not found.")
        if st.button("Return to browse"):
            st.session_state.page = "Browse"
            st.rerun()
    else:
        car = matches.iloc[0]
        vehicle_name = (
            f'{int(car["Year"])} {car["Make"]} {car["Model"]}'
        )

        st.title("Choose how you'd like to pay")
        st.subheader(vehicle_name)

        price = int((car["Price_Low"] + car["Price_High"]) / 2)

        payment_type = st.radio(
            "Payment method",
            ["Cash", "Finance"],
            horizontal=True,
        )

        st.markdown(
            f'<div class="price">Estimated vehicle price: '
            f'${price:,.0f} CAD</div>',
            unsafe_allow_html=True,
        )

        if payment_type == "Cash":
            st.write(
                "Paying cash means paying the vehicle price upfront. "
                "Taxes, registration, and other fees are not included."
            )
            st.metric("Estimated upfront vehicle price", f"${price:,.0f}")

        else:
            down_payment = st.number_input(
                "Down payment (CAD)",
                min_value=0,
                max_value=price,
                value=min(5000, price),
                step=500,
            )

            term = st.selectbox(
                "Loan term",
                [24, 36, 48, 60, 72, 84],
                index=3,
                format_func=lambda x: f"{x} months ({x // 12} years)"
            )

            interest_rate = st.number_input(
                "Annual interest rate (%)",
                min_value=0.0,
                max_value=40.0,
                value=7.99,
                step=0.25,
            )

            loan = max(0, price - down_payment)
            monthly_rate = interest_rate / 100 / 12

            if loan == 0:
                monthly_payment = 0
            elif monthly_rate == 0:
                monthly_payment = loan / term
            else:
                monthly_payment = (
                    loan * monthly_rate
                    / (1 - (1 + monthly_rate) ** (-term))
                )

            total_payments = monthly_payment * term
            interest_total = total_payments - loan

            a, b = st.columns(2)
            a.metric("Estimated monthly payment", f"${monthly_payment:,.2f}")
            b.metric("Amount financed", f"${loan:,.2f}")

            st.write(f"Estimated interest over the loan: **${interest_total:,.2f}**")

            st.caption(
                "Illustrative calculator only. The interest rate is an "
                "assumption, not a loan offer. Taxes, fees, insurance, "
                "and lender approval are not included."
            )

        st.divider()
        st.subheader("Interested in this vehicle?")

        if st.button(
            "Continue to inquiry →",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.payment_type = payment_type
            st.session_state.page = "Inquiry"
            st.rerun()

        if st.button("← Back to vehicle details"):
            st.session_state.page = "Details"
            st.rerun()

# --------------------------------------------------
# INQUIRY PAGE
# --------------------------------------------------

elif st.session_state.page == "Inquiry":

    matches = df[df["id"] == st.session_state.vehicle_id]

    if matches.empty:
        st.warning("Vehicle not found.")
        if st.button("Return to browse"):
            st.session_state.page = "Browse"
            st.rerun()
    else:
        car = matches.iloc[0]
        vehicle_name = (
            f'{int(car["Year"])} {car["Make"]} {car["Model"]}'
        )

        st.title("Vehicle inquiry")
        st.write(f"You are interested in the **{vehicle_name}**.")
        st.write(f"Preferred payment: **{st.session_state.payment_type}**")

        with st.form("inquiry_form"):
            name = st.text_input("Your name")
            email = st.text_input("Email address")
            message = st.text_area(
                "Message",
                value=f"I'm interested in the {vehicle_name}."
            )

            submitted = st.form_submit_button(
                "Submit demo inquiry",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            if not name.strip() or not email.strip():
                st.error("Please enter your name and email.")
            elif "@" not in email or "." not in email.split("@")[-1]:
                st.error("Please enter a valid email address.")
            else:
                st.success(
                    "Demo inquiry complete! No message was sent to a "
                    "dealership. This prototype does not yet store or "
                    "send inquiries."
                )

        if st.button("← Back to vehicles"):
            st.session_state.page = "Browse"
            st.rerun()

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()
st.caption(
    "Canadian Auto Market · Demo website · "
    "Listings and prices are simulated, not live dealership offers. "
    "No real purchases or financing applications are processed."
)
