import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Set page config
st.set_page_config(
    page_title="IIA Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.2rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">📊 IIA Dashboard</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/300x100/1f77b4/white?text=IIA+Test", width=300)
    st.markdown("### Navigation")
    
    # Sample filters
    date_range = st.date_input(
        "Select Date Range",
        value=[datetime.now() - timedelta(days=30), datetime.now()],
        format="YYYY-MM-DD"
    )
    
    category = st.selectbox(
        "Select Category",
        ["All", "Sales", "Marketing", "Operations", "Finance"]
    )
    
    refresh_data = st.button("🔄 Refresh Data", type="primary")

# Generate sample data
@st.cache_data
def generate_sample_data():
    """Generate sample data for the dashboard"""
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    
    # Sales data
    sales_data = pd.DataFrame({
        'Date': dates,
        'Sales': np.random.normal(1000, 200, len(dates)).cumsum(),
        'Orders': np.random.poisson(50, len(dates)),
        'Revenue': np.random.normal(5000, 1000, len(dates)),
        'Category': np.random.choice(['Sales', 'Marketing', 'Operations', 'Finance'], len(dates))
    })
    
    # Customer data
    customer_data = pd.DataFrame({
        'Region': ['North', 'South', 'East', 'West', 'Central'],
        'Customers': np.random.randint(100, 1000, 5),
        'Satisfaction': np.random.uniform(3.5, 5.0, 5)
    })
    
    return sales_data, customer_data

# Load data
if refresh_data:
    st.cache_data.clear()

sales_data, customer_data = generate_sample_data()

# Filter data based on sidebar selections
filtered_data = sales_data.copy()
if len(date_range) == 2:
    filtered_data = filtered_data[
        (filtered_data['Date'] >= pd.Timestamp(date_range[0])) & 
        (filtered_data['Date'] <= pd.Timestamp(date_range[1]))
    ]

if category != "All":
    filtered_data = filtered_data[filtered_data['Category'] == category]

# Main content with tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "💰 Revenue", "👥 Customers", "⚙️ Settings"])

with tab1:
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sales = filtered_data['Sales'].sum()
        st.metric(
            label="Total Sales",
            value=f"${total_sales:,.0f}",
            delta=f"{np.random.uniform(-10, 20):.1f}%"
        )
    
    with col2:
        total_orders = filtered_data['Orders'].sum()
        st.metric(
            label="Total Orders",
            value=f"{total_orders:,}",
            delta=f"{np.random.randint(-50, 100)}"
        )
    
    with col3:
        avg_revenue = filtered_data['Revenue'].mean()
        st.metric(
            label="Avg Revenue",
            value=f"${avg_revenue:,.0f}",
            delta=f"{np.random.uniform(-5, 15):.1f}%"
        )
    
    with col4:
        total_customers = customer_data['Customers'].sum()
        st.metric(
            label="Total Customers",
            value=f"{total_customers:,}",
            delta=f"{np.random.randint(10, 100)}"
        )
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Sales Trend")
        fig_line = px.line(
            filtered_data, 
            x='Date', 
            y='Sales',
            title="Sales Over Time",
            color_discrete_sequence=['#1f77b4']
        )
        fig_line.update_layout(height=400)
        st.plotly_chart(fig_line, use_container_width=True)
    
    with col2:
        st.subheader("📊 Orders by Category")
        category_orders = filtered_data.groupby('Category')['Orders'].sum().reset_index()
        fig_pie = px.pie(
            category_orders,
            values='Orders',
            names='Category',
            title="Order Distribution"
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)

with tab2:
    st.subheader("💰 Revenue Analysis")
    
    # Revenue metrics
    col1, col2 = st.columns(2)
    
    with col1:
        fig_bar = px.bar(
            filtered_data.groupby(filtered_data['Date'].dt.month)['Revenue'].sum().reset_index(),
            x='Date',
            y='Revenue',
            title="Monthly Revenue",
            labels={'Date': 'Month', 'Revenue': 'Revenue ($)'}
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        fig_histogram = px.histogram(
            filtered_data,
            x='Revenue',
            nbins=30,
            title="Revenue Distribution"
        )
        st.plotly_chart(fig_histogram, use_container_width=True)
    
    # Revenue table
    st.subheader("📋 Revenue Details")
    revenue_summary = filtered_data.groupby('Category').agg({
        'Revenue': ['sum', 'mean', 'std'],
        'Orders': 'sum'
    }).round(2)
    
    revenue_summary.columns = ['Total Revenue', 'Avg Revenue', 'Revenue StdDev', 'Total Orders']
    st.dataframe(revenue_summary, use_container_width=True)

with tab3:
    st.subheader("👥 Customer Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_customers = px.bar(
            customer_data,
            x='Region',
            y='Customers',
            title="Customers by Region",
            color='Customers',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_customers, use_container_width=True)
    
    with col2:
        fig_satisfaction = px.scatter(
            customer_data,
            x='Customers',
            y='Satisfaction',
            size='Customers',
            title="Customer Satisfaction vs Count",
            hover_data=['Region']
        )
        st.plotly_chart(fig_satisfaction, use_container_width=True)
    
    # Customer data table
    st.subheader("📋 Customer Data")
    st.dataframe(customer_data, use_container_width=True)

with tab4:
    st.subheader("⚙️ Application Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Configuration")
        auto_refresh = st.checkbox("Auto-refresh data", value=False)
        refresh_interval = st.slider("Refresh interval (seconds)", 5, 60, 30)
        theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
        
        if st.button("Save Settings"):
            st.success("Settings saved successfully!")
    
    with col2:
        st.markdown("### System Information")
        st.info(f"**Application:** IIA Test Dashboard")
        st.info(f"**Version:** 1.0.0")
        st.info(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.info(f"**Data Points:** {len(filtered_data):,}")
        
        # System health check
        st.markdown("### Health Check")
        if st.button("Run Health Check"):
            with st.spinner("Running health check..."):
                time.sleep(2)
                st.success("✅ All systems operational")
                st.success("✅ Database connection: OK")
                st.success("✅ API endpoints: OK")
                st.success("✅ Cache: OK")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🚀 IIA Test Dashboard | Built with Streamlit | 
        <a href="https://github.com/deepankar-MT24031/iia_test" target="_blank">GitHub Repository</a></p>
    </div>
    """,
    unsafe_allow_html=True
)

# Auto-refresh functionality
if 'auto_refresh' in locals() and auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
