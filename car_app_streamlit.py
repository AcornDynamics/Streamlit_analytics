import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit_authenticator as stauth

# --- User Authentication ---
# Single user credentials
names = ['Acorn']
usernames = ['acorn']
passwords = ['Alex!sonfire@6']  # Password stored in plain text for simplicity

# Hash the password for better security (optional but recommended)
hashed_passwords = stauth.Hasher(passwords).generate()

# Authenticator object
authenticator = stauth.Authenticate(names, usernames, hashed_passwords, "app_home", "random_key", cookie_expiry_days=30)

# Create login form
name, authentication_status, username = authenticator.login("Login", "main")

# Conditional rendering based on login status
if authentication_status:
    st.success(f"Welcome, {name}!")
    
    # --- Your app logic goes here ---
    
    # Load data from GitHub (use the raw URL)
    csv_url = "https://raw.githubusercontent.com/AcornDynamics/Streamlit_analytics/main/df_combined.csv"
    df = pd.read_csv(csv_url)

    unique_models = sorted(df['Model'].unique().tolist())
    unique_manuf = sorted(df['Manuf'].unique().tolist())  # Get unique manufacturers for the manuf_filter
    unique_dates = sorted(df['date'].unique().tolist())  # Get unique dates for the date filter

    # Sidebar filters
    st.sidebar.header("Filters")
    manuf_filter = st.sidebar.multiselect("Select Manufacturer(s)", unique_manuf, key="manuf_filter")
    model_filter = st.sidebar.multiselect("Select Model(s)", unique_models, key="model_filter")
    x_axis = st.sidebar.selectbox("X-axis", ["Year", "Mileage", "Motor Volume"], key="x_axis")
    y_axis = st.sidebar.selectbox("Y-axis", ["Price"], key="y_axis")
    date_filter = st.sidebar.multiselect("Select date", unique_dates, key="date_filter_top")

    # Apply filters
    def apply_filters(df):
        """Applies the manufacturer, model, and date filters to the dataframe."""
        if manuf_filter:
            df = df[df['Manuf'].isin(manuf_filter)]
        if model_filter:
            df = df[df['Model'].isin(model_filter)]
        if date_filter:
            df = df[df['date'].isin(date_filter)]
        return df

    filtered_df = apply_filters(df)

    # Top Scatter Plot
    st.header("Top Scatter Plot")
    df_clean = filtered_df.replace([float('inf'), -float('inf')], float('nan')).dropna(subset=["Year", "Mileage", "Motor Volume", "Price"])
    fig_scatter = px.scatter(df_clean, x=x_axis, y=y_axis, color="Model", hover_data=["Model", "Year", "Mileage", "Price"],
                             title=f"{y_axis} vs. {x_axis} by Car Model")
    st.plotly_chart(fig_scatter)

    # Sunburst Charts side by side
    st.header("Sunburst Charts")

    col1, col2 = st.columns(2)

    # Manufacturer and Model Short Sunburst
    with col1:
        fig_manuf_model_sunburst = px.sunburst(filtered_df, path=['Manuf', 'Model Short'], title="Manufacturer and Model Short Distribution", color='Manuf')
        st.plotly_chart(fig_manuf_model_sunburst)

    # Motor Type Sunburst
    with col2:
        filtered_df_motor = filtered_df.dropna(subset=['Motor Type', 'Motor Volume'])
        fig_motor_type_sunburst = px.sunburst(filtered_df_motor, path=['Motor Type', 'Motor Volume'], title="Motor Type and Motor Volume Distribution", color='Motor Type')
        st.plotly_chart(fig_motor_type_sunburst)

    # Transmission Type Sunburst
    st.header("Transmission Type Sunburst")
    filtered_df_transmission = filtered_df.dropna(subset=['Transmission Type', 'Transmission Speeds'])
    fig_transmission_sunburst = px.sunburst(filtered_df_transmission, path=['Transmission Type', 'Transmission Speeds'], title="Transmission Type and Speeds Distribution", color='Transmission Type')
    st.plotly_chart(fig_transmission_sunburst)

    # Date Histogram
    st.header("Date Histogram")
    fig_histogram = px.histogram(filtered_df, x="date", color="Model", title="Model Count by Date")
    fig_histogram.update_layout(bargap=0.2)  # Add space between bars
    st.plotly_chart(fig_histogram)

    # Bottom Scatter Plot Filters
    st.sidebar.header("Bottom Scatter Plot Filters")
    color_axis = st.sidebar.selectbox("Color Axis", ["Body Type", "Motor Volume"], key="color_axis")
    x_axis_bottom = st.sidebar.selectbox("X-axis (Bottom Scatter)", ["Color", "Price"], key="x_axis_bottom")
    y_axis_bottom = st.sidebar.selectbox("Y-axis (Bottom Scatter)", ["Body Type", "Price"], key="y_axis_bottom")
    date_filter_bottom = st.sidebar.multiselect("Select date", unique_dates, key="date_filter_bottom")

    # Apply filters for bottom scatter plot
    def apply_bottom_filters(df):
        if date_filter_bottom:
            df = df[df['date'].isin(date_filter_bottom)]
        return df

    filtered_df_bottom = apply_bottom_filters(filtered_df)

    # Bottom Scatter Plot
    st.header("Bottom Scatter Plot")
    df_clean_bottom = filtered_df_bottom.replace([float('inf'), -float('inf')], float('nan')).dropna(subset=["Color", "Body Type", "Price"])
    fig_scatter_bottom = px.scatter(df_clean_bottom, x=x_axis_bottom, y=y_axis_bottom, color=color_axis,
                                    hover_data=["Model", "Color", "Body Type", "Price"],
                                    title=f"{y_axis_bottom} vs. {x_axis_bottom} by Car Model")
    st.plotly_chart(fig_scatter_bottom)

elif authentication_status is False:
    st.error("Username or password is incorrect")

elif authentication_status is None:
    st.warning("Please enter your username and password")
