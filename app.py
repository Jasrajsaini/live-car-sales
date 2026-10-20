
import sqlite3
import random
import streamlit as st
import pandas as pd

# ---------------- PAGE SETUP ----------------

st.set_page_config(
    page_title="Northstar Motors",
    layout="wide"
)

DB_NAME = "car_sales.db"

# ---------------- DESIGN ----------------

st.markdown("""
<style>
.stApp {
    background-color: #f4f7fb;
    color: #172b4d;
}
.block-container {
    padding-top: 1.5rem;
    max-width: 1250px;
}
.hero {
    background: linear-gradient(120deg, #10243e, #164e63);
    padding: 35px;
    border-radius: 18px;
    color: white;
    margin-bottom: 25px;
}
.hero h1 {
    color: white;
    font-size: 42px;
}
.hero p {
    color: #d7e9f0;
    font-size: 17px;
}
.car-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 10px;
}
.car-visual {
    background: linear-gradient(145deg, #e6eef5, #f8fafc);
    border-radius: 12px;
    height: 125px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 65px;
    margin-bottom: 15px;
}
.price {
    color: #087e8b;
    font-size: 24px;
    font-weight: 750;
}
div.stButton > button {
    background-color: #087e8b;
    color: white;
    border: none;
    border-radius: 9px;
    padding: 10px 16px;
    font-weight: 600;
}
div.stButton > button:hover {
    background-color: #075d68;
    color: white;
    border: none;
}
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e2e8f0;
    padding: 15px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)


# ---------------- DATABASE ----------------

def get_connection():
    return sqlite3.connect(DB_NAME)


def setup_database():
    conn = get_connection()
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
    conn.commit()
    conn.close()


# ---------------- SAMPLE INVENTORY ----------------

CAR_MODELS = {
    "Toyota": ["Corolla", "Camry", "RAV4", "Highlander", "Tacoma", "Prius"],
    "Honda": ["Civic", "Accord", "CR-V", "Pilot", "Odyssey"],
    "Ford": ["F-150", "Escape", "Explorer", "Bronco", "Mustang"],
    "Chevrolet": ["Equinox", "Malibu", "Silverado", "Tahoe", "Traverse"],
    "Hyundai": ["Elantra", "Sonata", "Tucson", "Santa Fe", "Palisade"],
    "Kia": ["Forte", "K5", "Sportage", "Sorento", "Telluride"],
    "Nissan": ["Sentra", "Altima", "Rogue", "Pathfinder", "Frontier"],
    "Volkswagen": ["Jetta", "Passat", "Tiguan", "Atlas", "Golf"],
    "Mazda": ["Mazda3", "Mazda6", "CX-5", "CX-50", "CX-90"],
    "Subaru": ["Impreza", "Legacy", "Forester", "Outback", "Crosstrek"],
    "BMW": ["3 Series", "5 Series", "X3", "X5", "i4"],
    "Mercedes-Benz": ["C-Class", "E-Class", "GLA", "GLC", "GLE"],
    "Audi": ["A3", "A4", "Q3", "Q5", "Q7"],
    "Tesla": ["Model 3", "Model Y", "Model S", "Model X"],
    "Lexus": ["IS", "ES", "NX", "RX", "GX"],
    "Jeep": ["Compass", "Cherokee", "Grand Cherokee", "Wrangler"],
    "GMC": ["Terrain", "Acadia", "Sierra", "Yukon"],
    "Ram": ["1500", "2500", "3500"],
    "Volvo": ["S60", "S90", "XC40", "XC60", "XC90"],
    "Porsche": ["Macan", "Cayenne", "Panamera", "Taycan"],
}

BASE_PRICES = {
    "Toyota": 36000, "Honda": 35000, "Ford": 44000,
    "Chevrolet": 42000, "Hyundai": 33000, "Kia": 32000,
    "Nissan": 34000, "Volkswagen": 37000, "Mazda": 35000,
    "Subaru": 37000, "BMW": 65000, "Mercedes-Benz": 72000,
    "Audi": 63000, "Tesla": 60000, "Lexus": 65000,
    "Jeep": 43000, "GMC": 52000, "Ram": 54000,
    "Volvo": 62000, "Porsche": 105000,
}


def seed_inventory():
    conn = get_connection()
    count = conn.execute(
        "SELECT COUNT(*) FROM car_sales"
    ).fetchone()[0]

    # Add more sample vehicles if the database has fewer than 120.
    if count < 120:
        existing = set(
            conn.execute(
                "SELECT Make, Model, Year, Condition FROM car_sales"
            ).fetchall()
        )

        rng = random.Random(42)
        vehicles = []

        for make, models in CAR_MODELS.items():
            for model in models:
                for year in range(2016, 2027):
                    condition = "New" if year >= 2025 else "Used"
                    key = (make, model, year, condition)

                    if key in existing:
                        continue

                    base = BASE_PRICES[make]
                    if model in ["F-150", "Silverado", "Sierra", "1500"]:
                        base *= 1.25
                    if model in ["Cayenne", "Panamera", "Taycan"]:
                        base *= 1.35

                    if condition == "New":
                        mileage = rng.randint(0, 200)
                        price = base * rng.uniform(0.95, 1.20)
                    else:
                        age = 2026 - year
                        mileage = rng.randint(
                            max(0, age * 12000),
                            max(1000, age * 22000)
                        )
                        price = base * max(0.30, 0.88 ** age)
                        price *= rng.uniform(0.90, 1.10)

                    vehicles.append((
                        make, model, year, condition, mileage,
                        round(price * 0.97, 2),
                        round(price * 1.03, 2),
                        "Sample inventory"
                    ))

        rng.shuffle(vehicles)
        needed = max(0, 120 - count)

        conn.executemany("""
            INSERT INTO car_sales
            (Make, Model, Year, Condition, Mileage,
             Price_Low, Price_High, Date_Time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, vehicles[:needed])

        conn.commit()

    conn.close()


setup_database()
seed_inventory()


# ---------------- NAVIGATION ----------------

if "page" not in st.session_state:
    st.session_state.page = "Browse"

if "visible_count" not in st.session_state:
    st.session_state.visible_count = 12

if "selected_car" not in st.session_state:
    st.session_state.selected_car = None


def go_to(page):
    st.session_state.page = page
    st.rerun()


def money(value):
    return f"${value:,.0f}"


# ---------------- HEADER ----------------

with st.container():
    st.markdown("""
    <div class="hero">
        <h1>Northstar Motors</h1>
        <p>Find your next vehicle. Explore your options. Drive with confidence.</p>
    </div>
    """, unsafe_allow_html=True)

nav1, nav2, nav3 = st.columns(3)

with nav1:
    if st.button(" Browse Vehicles", use_container_width=True):
        go_to("Browse")

with nav2:
    if st.button(" Payment Calculator", use_container_width=True):
        go_to("Payments")

with nav3:
    if st.button(" Contact Us", use_container_width=True):
        go_to("Inquiry")


# ---------------- BROWSE INVENTORY ----------------

if st.session_state.page == "Browse":

    st.subheader("Find your next vehicle")
    st.write("Browse our sample inventory and select a vehicle to view its details.")

    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM car_sales ORDER BY Year DESC, Make, Model",
        conn
    )
    conn.close()

    if not df.empty:
        f1, f2, f3 = st.columns(3)

        with f1:
            makes = ["All Makes"] + sorted(df["Make"].dropna().unique().tolist())
            chosen_make = st.selectbox("Make", makes)

        with f2:
            chosen_condition = st.selectbox(
                "Condition",
                ["All", "New", "Used"]
            )

        with f3:
            max_price = st.selectbox(
                "Maximum budget",
                ["Any budget", "$25,000", "$40,000", "$60,000",
                 "$80,000", "$100,000", "$150,000"]
            )

        filtered = df.copy()

        if chosen_make != "All Makes":
            filtered = filtered[filtered["Make"] == chosen_make]

        if chosen_condition != "All":
            filtered = filtered[filtered["Condition"] == chosen_condition]

        if max_price != "Any budget":
            budget = int(max_price.replace("$", "").replace(",", ""))
            filtered = filtered[filtered["Price_Low"] <= budget]

        st.markdown("---")
        st.write(f"**{len(filtered)} vehicles available for these filters**")

        if filtered.empty:
            st.info("No vehicles match these filters. Try changing your selections.")
        else:
            shown = filtered.head(st.session_state.visible_count)

            for start in range(0, len(shown), 3):
                columns = st.columns(3)

                for col, (_, car) in zip(
                    columns,
                    shown.iloc[start:start + 3].iterrows()
                ):
                    with col:
                        st.markdown(
                            f"""
                            <div class="car-card">
                                <div class="car-visual">🚘</div>
                                <h3>{car['Year']} {car['Make']}</h3>
                                <h4>{car['Model']}</h4>
                                <p>{car['Condition']} · {int(car['Mileage']):,} km</p>
                                <div class="price">{money(car['Price_Low'])}</div>
                                <p style="color:#64748b;font-size:13px;">
                                    Estimated sample price
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        if st.button(
                            "View Vehicle",
                            key=f"vehicle_{int(car['id'])}",
                            use_container_width=True
                        ):
                            st.session_state.selected_car = car.to_dict()
                            go_to("Details")

            if st.session_state.visible_count < len(filtered):
                st.write("")
                if st.button("Load More Vehicles", use_container_width=True):
                    st.session_state.visible_count += 12
                    st.rerun()

            if st.session_state.visible_count > 12:
                if st.button("Show Fewer Vehicles"):
                    st.session_state.visible_count = 12
                    st.rerun()

    st.caption(
        "Demo website: vehicles and prices are simulated and are not confirmed dealership listings."
    )


# ---------------- VEHICLE DETAILS ----------------

elif st.session_state.page == "Details":

    car = st.session_state.selected_car

    if not car:
        st.warning("Choose a vehicle from the Browse page first.")
        if st.button("Back to Browse"):
            go_to("Browse")
    else:
        st.subheader(f"{car['Year']} {car['Make']} {car['Model']}")

        st.markdown(
            f"""
            <div class="car-visual" style="height:200px;font-size:100px;">
                
            </div>
            """,
            unsafe_allow_html=True
        )

        a, b, c = st.columns(3)
        a.metric("Estimated price", money(car["Price_Low"]))
        b.metric("Mileage", f"{int(car['Mileage']):,} km")
        c.metric("Condition", car["Condition"])

        st.markdown("### Vehicle overview")
        st.write(f"**Make:** {car['Make']}")
        st.write(f"**Model:** {car['Model']}")
        st.write(f"**Year:** {car['Year']}")
        st.write(f"**Estimated price range:** {money(car['Price_Low'])} – {money(car['Price_High'])}")

        left, right = st.columns(2)

        with left:
            if st.button("Explore Payment Options", use_container_width=True):
                go_to("Payments")

        with right:
            if st.button("Ask About This Vehicle", use_container_width=True):
                go_to("Inquiry")

        if st.button("← Back to Vehicles"):
            go_to("Browse")


# ---------------- PAYMENT CALCULATOR ----------------

elif st.session_state.page == "Payments":

    st.subheader("Explore your payment options")
    st.write("Compare paying in full with an illustrative financing estimate.")

    car = st.session_state.selected_car
    default_price = float(car["Price_Low"]) if car else 30000.0

    payment_type = st.radio(
        "Choose a payment option",
        ["Finance with monthly payments", "Pay in full"],
        horizontal=True
    )

    vehicle_price = st.number_input(
        "Vehicle price ($)",
        min_value=1000.0,
        max_value=500000.0,
        value=float(default_price),
        step=500.0
    )

    if payment_type == "Pay in full":
        st.markdown("### Estimated total")
        st.markdown(f"<div class='price'>{money(vehicle_price)}</div>",
                    unsafe_allow_html=True)
        st.caption("Taxes, registration, and other fees are not included.")

    else:
        down_payment = st.number_input(
            "Down payment ($)",
            min_value=0.0,
            max_value=float(vehicle_price),
            value=min(5000.0, float(vehicle_price)),
            step=500.0
        )

        interest_rate = st.selectbox(
            "Illustrative annual interest rate",
            [4.9, 5.9, 6.9, 7.9, 8.9, 9.9],
            index=2
        )

        term_years = st.select_slider(
            "Financing term",
            options=[2, 3, 4, 5, 6, 7],
            value=5
        )

        principal = vehicle_price - down_payment
        months = term_years * 12
        monthly_rate = interest_rate / 100 / 12

        if monthly_rate == 0:
            monthly_payment = principal / months
        else:
            monthly_payment = (
                principal * monthly_rate /
                (1 - (1 + monthly_rate) ** (-months))
            )

        st.markdown("### Your estimated payment")

        m1, m2 = st.columns(2)
        m1.metric("Estimated monthly payment", money(monthly_payment))
        m2.metric("Amount financed", money(principal))

        st.caption(
            "Illustration only. Actual rates, approval, taxes, fees, and lender terms may differ. "
            "This demo does not provide financing or loan approval."
        )

    if st.button("Continue to Inquiry", use_container_width=True):
        go_to("Inquiry")


# ---------------- INQUIRY ----------------

elif st.session_state.page == "Inquiry":

    st.subheader("Interested in a vehicle?")
    st.write("Enter your details to preview the inquiry process.")

    car = st.session_state.selected_car
    if car:
        st.info(
            f"Vehicle selected: {car['Year']} {car['Make']} {car['Model']}"
        )

    with st.form("inquiry_form"):
        name = st.text_input("Your name")
        email = st.text_input("Email address")
        message = st.text_area("Message (optional)")
        submitted = st.form_submit_button("Submit Inquiry")

    if submitted:
        if not name.strip() or "@" not in email or "." not in email.split("@")[-1]:
            st.error("Please enter your name and a valid email address.")
        else:
            st.success(
                "Demo inquiry complete! This prototype does not send or save your message."
            )
            st.write("In a live website, this step would securely send your inquiry to the dealership.")

    if st.button("Back to Browse"):
        go_to("Browse")
