import pandas as pd
import plotly.express as px
import streamlit as st

# --- Your app logic goes here ---

# Load data from GitHub (use the raw URL)
csv_url = "https://raw.githubusercontent.com/AcornDynamics/Streamlit_analytics/main/df_combined.csv"
df = pd.read_csv(csv_url)

# Convert 'date' column to datetime
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

unique_models = sorted(df['Model'].unique().tolist())
unique_manuf = sorted(df['Manuf'].unique().tolist())  # Get unique manufacturers for the manuf_filter
unique_dates = sorted(df['date'].unique().tolist())  # Get unique dates for the date filter

# --- Filters in Expanders on Top ---
col1, col2, col3 = st.columns(3)

with col1:
    with st.expander("Manufacturer Filter"):
        manuf_filter = st.multiselect("Select Manufacturer(s)", unique_manuf, key="manuf_filter")

with col2:
    with st.expander("Date Filter (Top Plots)"):
        date_filter = st.multiselect("Select date", unique_dates, key="date_filter_top")  # Date filter at the top

with col3:
    with st.expander("Bottom Scatter Plot Filters"):
        color_axis = st.selectbox("Color Axis", ["Body Type", "Motor Volume"], key="color_axis")
        x_axis_bottom = st.selectbox("X-axis (Bottom Scatter)", ["Color", "Price"], key="x_axis_bottom")
        y_axis_bottom = st.selectbox("Y-axis (Bottom Scatter)", ["Body Type", "Price"], key="y_axis_bottom")
        date_filter_bottom = st.multiselect("Select date", unique_dates, key="date_filter_bottom")

        # Apply filters for bottom scatter plot
        def apply_bottom_filters(df):
            if date_filter_bottom:
                df = df[df['date'].isin(date_filter_bottom)]
            return df

        filtered_df_bottom = apply_bottom_filters(df)  # Apply to already filtered DataFrame

# Apply filters
def apply_filters(df):
    """Applies the manufacturer, model, and date filters to the dataframe."""
    if manuf_filter:
        df = df[df['Manuf'].isin(manuf_filter)]
    if date_filter:
        df = df[df['date'].isin(date_filter)]
    return df

filtered_df = apply_filters(df)  # Apply to the main DataFrame

# --- Metrics ---
col1, col2, col3 = st.columns(3)
with col1:
    total_cars = len(filtered_df)
    st.metric("Total Cars", total_cars)

with col2:
    unique_cars = filtered_df['Model'].nunique()
    st.metric("Unique Car Models", unique_cars)

with col3:
    avg_price = round(filtered_df['Price'].mean(), 2)
    st.metric("Average Price", f"{avg_price} €")

# --- Charts ---

# Top Scatter Plot
st.header("Top Scatter Plot")
df_clean = filtered_df.replace([float('inf'), -float('inf')], float('nan')).dropna(
    subset=["Year", "Mileage", "Motor Volume", "Price"])
fig_scatter = px.scatter(df_clean, x="Year", y="Price", color="Model",
                         hover_data=["Model", "Year", "Mileage", "Price"],
                         title="Price vs. Year by Car Model")
st.plotly_chart(fig_scatter)

# Sunburst Charts side by side
st.header("Sunburst Charts")

col1, col2 = st.columns(2)

# Manufacturer and Model Short Sunburst
with col1:
    fig_manuf_model_sunburst = px.sunburst(filtered_df, path=['Manuf', 'Model Short'],
                                          title="Manufacturer and Model Short Distribution", color='Manuf')
    st.plotly_chart(fig_manuf_model_sunburst)

# Motor Type Sunburst
with col2:
    filtered_df_motor = filtered_df.dropna(subset=['Motor Type', 'Motor Volume'])
    fig_motor_type_sunburst = px.sunburst(filtered_df_motor, path=['Motor Type', 'Motor Volume'],
                                         title="Motor Type and Motor Volume Distribution", color='Motor Type')
    st.plotly_chart(fig_motor_type_sunburst)

# Transmission Type Sunburst
st.header("Transmission Type Sunburst")
filtered_df_transmission = filtered_df.dropna(subset=['Transmission Type', 'Transmission Speeds'])
fig_transmission_sunburst = px.sunburst(filtered_df_transmission, path=['Transmission Type', 'Transmission Speeds'],
                                       title="Transmission Type and Speeds Distribution", color='Transmission Type')
st.plotly_chart(fig_transmission_sunburst)

# Date Histogram
st.header("Date Histogram")
fig_histogram = px.histogram(filtered_df, x="date", color="Model", title="Model Count by Date")
fig_histogram.update_layout(bargap=0.2)  # Add space between bars
st.plotly_chart(fig_histogram)

# Bottom Scatter Plot
st.header("Bottom Scatter Plot")
df_clean_bottom = filtered_df_bottom.replace([float('inf'), -float('inf')], float('nan')).dropna(
    subset=["Color", "Body Type", "Price"])
fig_scatter_bottom = px.scatter(df_clean_bottom, x=x_axis_bottom, y=y_axis_bottom, color=color_axis,
                                 hover_data=["Model", "Color", "Body Type", "Price"],
                                 title=f"{y_axis_bottom} vs. {x_axis_bottom} by Car Model")
st.plotly_chart(fig_scatter_bottom)

# --- Top 50 Models DataFrame ---
st.header("Top 50 Models by Count")

def get_top_models_df(df):
    """Returns a DataFrame with statistics for the top 50 car models."""
    top_models = df['Model'].value_counts().head(50).index
    df_top_models = df[df['Model'].isin(top_models)]

    def most_frequent(series):
        mode_result = series.mode()
        return mode_result[0] if not mode_result.empty else None

    df_agg = df_top_models.groupby('Model').agg(
        Count=('Model', 'count'),  # Total count for the model
        Max_Price=('Price', 'max'),
        Min_Price=('Price', 'min'),
        Max_Mileage=('Mileage', 'max'),
        Min_Mileage=('Mileage', 'min'),
        Max_Year=('Year', 'max'),  # Max Year
        Min_Year=('Year', 'min'),  # Min Year
        Most_Popular_Year=('Year', most_frequent),  # Most Popular Year
        Most_Popular_Color=('Color', most_frequent),
        Most_Popular_Motor_Volume=('Motor Volume', most_frequent)
    )
    return df_agg

top_models_df = get_top_models_df(filtered_df)  # Use the filtered DataFrame

# Display DataFrame
st.dataframe(top_models_df)
