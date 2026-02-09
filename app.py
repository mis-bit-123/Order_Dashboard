import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_loader import OrderDataLoader
from config import DASHBOARD_TITLE, CURRENCY, BRUSH_SHEET_NAME
import numpy as np
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="CMPL Order Analytics Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# PROFESSIONAL GLOBAL CSS
# ==========================================
st.markdown("""
<style>

    /* Main Header */
    .main-header { 
        font-size: 2.8rem; 
        font-weight: 800; 
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding-bottom: 10px;
        border-bottom: 3px solid #1f77b4;
    }

    .subheader { 
        font-size: 1.5rem; 
        font-weight: 600; 
        color: #2c3e50;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    .metric-card { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px; 
        border-radius: 15px; 
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }

    .filter-box {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin-bottom: 20px;
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4 !important;
        color: white !important;
    }

    /* Side Radio Buttons */
    .stRadio > div {
        background-color: #101a24;
        border-radius: 10px;
        padding: 0.5rem;
        margin-top: 0.5rem;
    }
    .stRadio label {
        font-weight: 500 !important;
        padding: 0.4rem 0.6rem !important;
        border-radius: 6px !important;
        margin: 0.2rem 0 !important;
        transition: all 0.2s;
    }
    .stRadio label:hover {
        background-color: #e9ecef;
        transform: translateX(3px);
    }
    .stRadio [aria-selected="true"] {
        background-color: #1f77b4 !important;
        color: black !important;
        font-weight: 600 !important;
    }
    
    /* Brush Dashboard Specific Styles */
    .brush-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin-bottom: 20px;
    }
    
    .urgency-overdue { background-color: #ffebee; color: #c62828; padding: 4px 8px; border-radius: 12px; font-weight: bold; }
    .urgency-week { background-color: #fff3e0; color: #ef6c00; padding: 4px 8px; border-radius: 12px; font-weight: bold; }
    .urgency-month { background-color: #fffde7; color: #f9a825; padding: 4px 8px; border-radius: 12px; font-weight: bold; }
    .urgency-future { background-color: #e8f5e9; color: #2e7d32; padding: 4px 8px; border-radius: 12px; font-weight: bold; }

</style>
""", unsafe_allow_html=True)


# ==========================================
# DATA INITIALIZATION
# ==========================================
@st.cache_resource
def get_loader():
    return OrderDataLoader()

loader = get_loader()

# ==========================================
# LOAD DATA FIRST (Before Sidebar)
# ==========================================
@st.cache_data(ttl=300)
def load_data():
    try:
        return loader.fetch_data()
    except Exception as e:
        return None

df = load_data()

# Calculate stats safely
if df is not None and not df.empty:
    record_count = len(df)
    stats = loader.get_stats(df)
else:
    record_count = 0
# ==========================================
# SIDEBAR HEADER (Now df is defined)
# ==========================================
st.sidebar.markdown(f"""
<div style="text-align: center; padding: 1.5rem 0.5rem; background: linear-gradient(135deg, #1f77b4 0%, #ff7f0e 100%); border-radius: 15px; margin-bottom: 1.5rem; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
    <div style="font-size: 3rem; margin-bottom: 0.5rem;">📊</div>
    <div style="font-size: 1.4rem; font-weight: 800; margin-bottom: 0.3rem; letter-spacing: 0.5px;">CMPL Analytics</div>
    <div style="font-size: 0.95rem; opacity: 0.95; margin-bottom: 0.8rem; font-weight: 500;">Order Management System</div>
    <div style="font-size: 0.8rem; background: rgba(255,255,255,0.25); padding: 0.4rem 1rem; border-radius: 20px; display: inline-block; font-weight: 600; backdrop-filter: blur(10px);">
        🟢 System Online • {record_count:,} records
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR NAVIGATION (NO CATEGORY TITLES)
# ==========================================

report_categories = {
    "📊 Overview": ["🏠 Executive Dashboard", "📈 Performance Metrics"],
    "🗺️ Geographic": ["🗺️ State-wise Deep Dive", "🗺️ State vs Product Matrix", "🗺️ Regional Comparison"],
    "💰 Financial": ["💰 Revenue Trends", "💰 Year-wise Analysis", "💰 Monthly Insights", "💰 Top Revenue Sources"],
    "🔧 Products": ["🔧 Product Performance", "🔧 Product Trends", "🔧 Best Sellers by State"],
    "🏢 Companies": ["🏢 Company Analysis", "🏢 Customer Segmentation"],
    "⚡ Operations": ["⚡ Lead Time Analysis"],
    "🧹 Brush System": ["🧹 Brush Follow-up Dashboard"],  # NEW SECTION
    "📥 Export": ["📋 Raw Data Explorer"]
}

# Flatten into single radio list
all_reports = []
for reports in report_categories.values():
    all_reports.extend(reports)

# RADIO BUTTON ONLY
report = st.sidebar.radio("📌 Select Report", all_reports)


# ==========================================
# LOAD DATA WITH ERROR HANDLING
# ==========================================
@st.cache_data(ttl=300)
def load_data():
    try:
        return loader.fetch_data()
    except Exception as e:
        st.error(f"Data load error: {e}")
        return None

df = load_data()

if df is None:
    st.error("❌ Failed to connect to Google Sheets!")
    st.info("🔧 Troubleshooting:\n1. Check credentials/service_account.json\n2. Verify Sheet ID in config.py\n3. Ensure sharing with service account")
    st.stop()

if df.empty:
    st.warning("⚠️ No data found in sheet")
    st.stop()

# Stats
stats = loader.get_stats(df)

# Filters
years = sorted(df['Year'].unique(), reverse=True)
months = ["All"] + list(df['Month_Name'].unique())


# ==========================================
# MAIN HEADER
# ==========================================
st.markdown(f"<h1 class='main-header'>{DASHBOARD_TITLE}</h1>", unsafe_allow_html=True)
st.caption(f"🔄 Live Data | 📊 {len(df):,} records | 🕒 Updated: {datetime.now().strftime('%d-%m-%Y %H:%M')}")
st.markdown("---")

# ==========================================
# REPORT: BRUSH FOLLOW-UP DASHBOARD (NEW)
# ==========================================
if report == "🧹 Brush Follow-up Dashboard":
    st.markdown("""
    <div class="brush-header">
        <h2>🧹 Broomer / Sweeper / Brush Set - Follow-up System</h2>
        <p>Track brush set purchases and manage 3-month replacement follow-ups</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Process brush data
    brush_df = loader.identify_brush_products(df)
    
    if brush_df.empty:
        st.warning("No Broomer, Sweeper, or Brush products found in the current dataset.")
        st.stop()
    
    # Calculate follow-up dates
    brush_df = loader.calculate_followup_dates(brush_df)
    brush_stats = loader.get_brush_summary_stats(brush_df)
    
    # ==================== MINI DASHBOARD METRICS ====================
    st.markdown("### 📊 Quick Overview")
    
    metric_cols = st.columns(5)
    with metric_cols[0]:
        st.metric("🧹 Total Units", f"{brush_stats['total_units']:,}")
    with metric_cols[1]:
        st.metric("💰 Total Revenue", f"{CURRENCY}{brush_stats['total_revenue']:,.0f}")
    with metric_cols[2]:
        st.metric("🏢 Unique Companies", f"{brush_stats['unique_companies']}")
    with metric_cols[3]:
        st.metric("⚠️ Overdue Follow-ups", f"{brush_stats['overdue_count']}", 
                 delta="Action Needed" if brush_stats['overdue_count'] > 0 else None,
                 delta_color="inverse")
    with metric_cols[4]:
        st.metric("📅 Due This Month", f"{brush_stats['upcoming_count']}")
    
    st.markdown("---")
    
    # ==================== TABS FOR ORGANIZATION ====================
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Follow-up Reminders", "📈 Analytics", "🔍 Search & Filter", "💾 Data Management"])
    
    # ==================== TAB 1: FOLLOW-UP REMINDERS ====================
    with tab1:
        st.markdown("### 📋 Follow-up Reminder Table")
        st.info("Brush sets need replacement after 90 days. Below is the automatic follow-up schedule based on purchase dates.")
        
        # Create display table
        display_df = brush_df[[
            'Date', 'Company', 'Client_Name', 'Product', 'State', 
            'Follow_Up_Date', 'Days_Until_Followup', 'Urgency', 'Inquiry_No'
        ]].copy()
        
        # Rename columns for display
        display_df.columns = [
            'Purchase Date', 'Company Name', 'Client Name', 'Product', 'State',
            'Follow-up Date', 'Days Left', 'Status', 'Inquiry No'
        ]
        
        # Format dates
        display_df['Purchase Date'] = display_df['Purchase Date'].dt.strftime('%d-%m-%Y')
        display_df['Follow-up Date'] = display_df['Follow-up Date'].dt.strftime('%d-%m-%Y')
        
        # Sort by urgency (overdue first)
        urgency_order = {'🔴 Overdue': 0, '🟠 Due This Week': 1, '🟡 Due This Month': 2, '🟢 Future': 3}
        display_df['Sort_Priority'] = brush_df['Urgency'].map(urgency_order)
        display_df = display_df.sort_values('Sort_Priority').drop('Sort_Priority', axis=1)
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.multiselect("Filter by Status:", 
                                          options=display_df['Status'].unique(),
                                          default=display_df['Status'].unique())
        with col2:
            search_company = st.text_input("Search Company:", placeholder="Type company name...")
        
        # Apply filters
        filtered_display = display_df[display_df['Status'].isin(status_filter)]
        if search_company:
            filtered_display = filtered_display[filtered_display['Company Name'].str.contains(search_company, case=False)]
        
        # Display styled table
        if not filtered_display.empty:
            # Color coding for status
            def color_status(val):
                if '🔴' in val:
                    return 'background-color: #ffebee; color: #c62828; font-weight: bold;'
                elif '🟠' in val:
                    return 'background-color: #fff3e0; color: #ef6c00; font-weight: bold;'
                elif '🟡' in val:
                    return 'background-color: #fffde7; color: #f9a825; font-weight: bold;'
                else:
                    return 'background-color: #e8f5e9; color: #2e7d32; font-weight: bold;'
            
            styled_df = filtered_display.style.applymap(color_status, subset=['Status'])
            st.dataframe(styled_df, use_container_width=True, height=500)
            
            # Summary for filtered view
            st.caption(f"Showing {len(filtered_display)} of {len(display_df)} total records")
        else:
            st.warning("No records match your filter criteria.")
    
    # ==================== TAB 2: ANALYTICS ====================
    with tab2:
        st.markdown("### 📈 Brush Product Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Urgency Distribution
            st.markdown("#### ⏰ Follow-up Status Distribution")
            urgency_data = brush_df['Urgency'].value_counts().reset_index()
            urgency_data.columns = ['Status', 'Count']
            
            fig_urgency = px.pie(urgency_data, values='Count', names='Status', 
                                color_discrete_map={
                                    '🔴 Overdue': '#c62828',
                                    '🟠 Due This Week': '#ef6c00',
                                    '🟡 Due This Month': '#f9a825',
                                    '🟢 Future': '#2e7d32'
                                },
                                hole=0.4)
            fig_urgency.update_traces(textinfo='percent+label', textposition='outside')
            st.plotly_chart(fig_urgency, use_container_width=True)
        
        with col2:
            # Top Products
            st.markdown("#### 🏆 Top Brush Products")
            top_products = brush_df['Product'].value_counts().head(10).reset_index()
            top_products.columns = ['Product', 'Units Sold']
            
            fig_products = px.bar(top_products, y='Product', x='Units Sold', 
                                 orientation='h', color='Units Sold',
                                 color_continuous_scale='Viridis')
            fig_products.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_products, use_container_width=True)
        
        # Timeline view
        st.markdown("#### 📅 Follow-up Timeline")
        timeline_df = brush_df.copy()
        timeline_df['Month'] = timeline_df['Follow_Up_Date'].dt.strftime('%Y-%m')
        monthly_followups = timeline_df.groupby(['Month', 'Urgency']).size().reset_index(name='Count')
        
        fig_timeline = px.bar(monthly_followups, x='Month', y='Count', color='Urgency',
                             color_discrete_map={
                                 '🔴 Overdue': '#c62828',
                                 '🟠 Due This Week': '#ef6c00',
                                 '🟡 Due This Month': '#f9a825',
                                 '🟢 Future': '#2e7d32'
                             },
                             barmode='stack')
        fig_timeline.update_layout(xaxis_title="Follow-up Month", yaxis_title="Number of Follow-ups")
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # State-wise analysis
        st.markdown("#### 🗺️ State-wise Brush Sales")
        state_brush = brush_df.groupby('State').agg({
            'Total_Amount': 'sum',
            'Company': 'nunique',
            'Inquiry_No': 'count'
        }).reset_index()
        state_brush.columns = ['State', 'Revenue', 'Companies', 'Units']
        
        fig_state = px.scatter(state_brush, x='Companies', y='Revenue', size='Units',
                              color='Revenue', hover_name='State',
                              color_continuous_scale='Plasma')
        fig_state.update_layout(xaxis_title="Number of Companies", yaxis_title=f"Revenue ({CURRENCY})")
        st.plotly_chart(fig_state, use_container_width=True)
    
    # ==================== TAB 3: SEARCH & FILTER ====================
    with tab3:
        st.markdown("### 🔍 Advanced Search")
        
        # Advanced filters
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_state = st.multiselect("Select States:", options=sorted(brush_df['State'].unique()))
        with col2:
            filter_product = st.multiselect("Select Products:", options=sorted(brush_df['Product'].unique()))
        with col3:
            date_range = st.date_input("Purchase Date Range:", 
                                      [brush_df['Date'].min(), brush_df['Date'].max()])
        
        # Apply advanced filters
        search_result = brush_df.copy()
        if filter_state:
            search_result = search_result[search_result['State'].isin(filter_state)]
        if filter_product:
            search_result = search_result[search_result['Product'].isin(filter_product)]
        if len(date_range) == 2:
            search_result = search_result[(search_result['Date'] >= pd.Timestamp(date_range[0])) & 
                                         (search_result['Date'] <= pd.Timestamp(date_range[1]))]
        
        if not search_result.empty:
            st.success(f"Found {len(search_result)} records matching your criteria")
            st.dataframe(search_result[[
                'Date', 'Company', 'Client_Name', 'Product', 'State', 
                'Total_Amount', 'Follow_Up_Date', 'Urgency'
            ]].style.format({
                'Date': lambda x: x.strftime('%d-%m-%Y'),
                'Follow_Up_Date': lambda x: x.strftime('%d-%m-%Y'),
                'Total_Amount': lambda x: f"{CURRENCY}{x:,.0f}"
            }), use_container_width=True)
            
            # Export option for filtered data
            csv = search_result.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Filtered Data as CSV",
                data=csv,
                file_name=f"brush_followups_{datetime.now().strftime('%Y%m%d')}.csv",
                mime='text/csv'
            )
        else:
            st.warning("No records found matching your criteria.")
    
    # ==================== TAB 4: DATA MANAGEMENT ====================
    with tab4:
        st.markdown("### 💾 Store to Google Sheets")
        st.info(f"This will store all {len(brush_df)} brush product records to the '{BRUSH_SHEET_NAME}' sheet in your Google Spreadsheet.")
        
        # Show preview of what will be stored
        with st.expander("👁️ Preview Data to be Stored"):
            preview_df = brush_df[[
                'Date', 'Inquiry_No', 'Company', 'Client_Name', 'Product', 
                'State', 'Total_Amount', 'Follow_Up_Date', 'Urgency'
            ]].copy()
            preview_df['Date'] = preview_df['Date'].dt.strftime('%d-%m-%Y')
            preview_df['Follow_Up_Date'] = preview_df['Follow_Up_Date'].dt.strftime('%d-%m-%Y')
            st.dataframe(preview_df.head(10), use_container_width=True)
            st.caption(f"Showing first 10 of {len(brush_df)} records")
        
        # Store button
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🚀 Store to Sheet", type="primary", use_container_width=True):
                with st.spinner("Storing data to Google Sheets..."):
                    success, message = loader.store_to_brush_sheet(brush_df)
                    if success:
                        st.success(message)
                        st.balloons()
                    else:
                        st.error(message)
        
        with col2:
            # Check existing data
            existing_data = loader.fetch_existing_brush_data()
            if existing_data is not None and not existing_data.empty:
                st.info(f"ℹ️ Sheet currently contains {len(existing_data)} records. Storing will update with latest data from Order Confirmation sheet.")
            else:
                st.info("ℹ️ No existing data found in the sheet. This will create a new entry.")
        
        # Show existing data if available
        if existing_data is not None and not existing_data.empty:
            st.markdown("### 📋 Currently Stored Data")
            st.dataframe(existing_data, use_container_width=True, height=300)

# ==========================================
# REPORT 1: EXECUTIVE DASHBOARD
# ==========================================
elif report == "🏠 Executive Dashboard":
    st.markdown("## 🎯 Executive Overview")
    
    # Get unique years safely, handling both int and float formats
    years = sorted(df['Year'].dropna().unique())
    # Convert to clean integers for display
    year_options = ["All"] + [str(int(float(y))) if pd.notna(y) else str(y) for y in years]
    
    # Top filters
    with st.container():
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            selected_year = st.selectbox("📅 Select Year:", year_options)
        with col_f2:
            selected_state = st.selectbox("🗺️ Select State:", ["All"] + sorted(df['State'].dropna().unique().tolist()))
        with col_f3:
            selected_product = st.selectbox("🔧 Select Product:", ["All"] + sorted(df['Product'].dropna().unique().tolist()))
    
    # Filter data with safe type handling
    filtered_df = df.copy()
    
    if selected_year != "All":
        # Handle both int and float year formats in data
        selected_year_num = int(float(selected_year))
        filtered_df = filtered_df[filtered_df['Year'].apply(
            lambda x: int(float(x)) if pd.notna(x) else None
        ) == selected_year_num]
    
    if selected_state != "All":
        filtered_df = filtered_df[filtered_df['State'] == selected_state]
    
    if selected_product != "All":
        filtered_df = filtered_df[filtered_df['Product'] == selected_product]
    
    # Handle empty filtered data
    if filtered_df.empty:
        st.warning("⚠️ No data found for the selected filters.")
        st.stop()
    
    # KPI Cards with gradient
    cols = st.columns(4)
    
    total_revenue = filtered_df['Total_Amount'].sum()
    total_qty = filtered_df['Qty'].sum()
    avg_order = filtered_df['Total_Amount'].mean()
    
    # Safely get top product
    product_sales = filtered_df.groupby('Product')['Total_Amount'].sum()
    top_product = product_sales.idxmax() if not product_sales.empty else "N/A"
    
    metrics = [
        ("💰 Total Revenue", f"{CURRENCY}{total_revenue:,.0f}", f"{len(filtered_df)} Orders"),
        ("📦 Total Quantity", f"{total_qty:,.0f}", "Units Sold"),
        ("📊 Avg Order Value", f"{CURRENCY}{avg_order:,.0f}", "Per Order"),
        ("🏆 Top Product", top_product, "Best Seller")
    ]
    
    for col, (label, value, delta) in zip(cols, metrics):
        with col:
            st.metric(label=label, value=value, delta=delta)
    
    st.markdown("---")
    
    # Charts Row 1
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 💵 Revenue by State (Top 8)")
        state_data = filtered_df.groupby('State')['Total_Amount'].sum().nlargest(8).reset_index()
        if not state_data.empty:
            fig = px.bar(
                state_data, 
                x='State', 
                y='Total_Amount', 
                color='Total_Amount',
                color_continuous_scale='Viridis', 
                text=state_data['Total_Amount'].apply(lambda x: f'{CURRENCY}{x/100000:.1f}L')
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No state data available")
    
    with c2:
        st.markdown("### 🔥 Top 5 Products by Revenue")
        prod_data = filtered_df.groupby('Product')['Total_Amount'].sum().nlargest(5).reset_index()
        if not prod_data.empty:
            fig = px.pie(
                prod_data, 
                values='Total_Amount', 
                names='Product', 
                hole=0.5,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No product data available")
    
    # Charts Row 2
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 📈 Monthly Revenue Trend")
        if not filtered_df.empty and 'Date' in filtered_df.columns:
            monthly = filtered_df.groupby(filtered_df['Date'].dt.to_period('M'))['Total_Amount'].sum()
            monthly.index = monthly.index.to_timestamp()
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=monthly.index, 
                y=monthly.values, 
                fill='tozeroy', 
                line=dict(color='#1f77b4', width=3), 
                name='Revenue'
            ))
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No date data available")
    
    with c2:
        st.markdown("### 🏢 Top 8 Companies")
        comp_data = filtered_df.groupby('Company')['Total_Amount'].sum().nlargest(8).reset_index()
        if not comp_data.empty:
            fig = px.bar(
                comp_data, 
                y='Company', 
                x='Total_Amount', 
                orientation='h', 
                color='Total_Amount',
                color_continuous_scale='Blues'
            )
            fig.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No company data available")
# ==========================================
# REPORT 2: PERFORMANCE METRICS
# ==========================================
elif report == "📈 Performance Metrics":
    st.markdown("## 📈 Advanced Performance Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Order Statistics")
        stats_df = pd.DataFrame({
            'Metric': ['Total Orders', 'Total Revenue', 'Avg Order Value', 'Total Quantity', 'Unique States', 'Unique Products'],
            'Value': [
                len(df),
                f"{CURRENCY}{df['Total_Amount'].sum():,.0f}",
                f"{CURRENCY}{df['Total_Amount'].mean():,.0f}",
                f"{df['Qty'].sum():,.0f}",
                df['State'].nunique(),
                df['Product'].nunique()
            ]
        })
        st.table(stats_df)
    
    with col2:
        st.markdown("### 📈 Growth Metrics")
        if len(df) > 0:
            daily_orders = df.groupby('Date').size()
            growth_rate = ((daily_orders.iloc[-1] - daily_orders.iloc[0]) / daily_orders.iloc[0] * 100) if len(daily_orders) > 1 else 0
            
            metrics = {
                "Avg Orders/Day": f"{daily_orders.mean():.1f}",
                "Peak Day Orders": f"{daily_orders.max()}",
                "Revenue/Day": f"{CURRENCY}{df.groupby('Date')['Total_Amount'].sum().mean():,.0f}",
                "Growth Rate": f"{growth_rate:.1f}%"
            }
            for k, v in metrics.items():
                st.metric(k, v)

# ==========================================
# REPORT 3: STATE-WISE DEEP DIVE
# ==========================================
elif report == "🗺️ State-wise Deep Dive":
    st.markdown("## 🗺️ Comprehensive State Analysis")
    
    # State selector with multi-select
    states = sorted(df['State'].unique())
    selected_states = st.multiselect("🗺️ Select States to Compare:", states, default=states[:5])
    
    if not selected_states:
        st.warning("Please select at least one state")
        st.stop()
    
    filtered = df[df['State'].isin(selected_states)]
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "📈 Trends", "🔍 Product Breakdown"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        with col1:
            state_summary = filtered.groupby('State').agg({
                'Total_Amount': 'sum',
                'Qty': 'sum',
                'Inquiry_No': 'count'
            }).rename(columns={'Inquiry_No': 'Orders'}).reset_index()
            
            fig = px.bar(state_summary, x='State', y=['Total_Amount', 'Qty'], 
                        barmode='group', title='Revenue vs Quantity by State')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📋 State Rankings")
            state_summary['Rank'] = state_summary['Total_Amount'].rank(ascending=False)
            st.dataframe(state_summary.sort_values('Total_Amount', ascending=False).style.format({
                'Total_Amount': lambda x: f"{CURRENCY}{x:,.0f}",
                'Qty': lambda x: f"{x:,.0f}"
            }), use_container_width=True)
    
    with tab2:
        st.markdown("### 📈 State-wise Monthly Trends")
        for state in selected_states[:3]:  # Show top 3 to avoid clutter
            state_df = df[df['State'] == state]
            monthly = state_df.groupby(state_df['Date'].dt.to_period('M'))['Total_Amount'].sum()
            monthly.index = monthly.index.to_timestamp()
            st.line_chart(monthly, use_container_width=True)
            st.caption(f"Trend for {state}")
    
    with tab3:
        selected_state_detail = st.selectbox("🔍 Select State for Product Details:", selected_states)
        if selected_state_detail:
            state_products = df[df['State'] == selected_state_detail].groupby('Product').agg({
                'Total_Amount': 'sum',
                'Qty': 'sum',
                'Inquiry_No': 'count'
            }).sort_values('Total_Amount', ascending=False).head(15)
            
            fig = px.treemap(state_products.reset_index(), path=['Product'], values='Total_Amount',
                           title=f'Product Distribution in {selected_state_detail}')
            st.plotly_chart(fig, use_container_width=True)

# ==========================================
# REPORT 4: STATE VS PRODUCT MATRIX
# ==========================================
elif report == "🗺️ State vs Product Matrix":
    st.markdown("## 🗺️ State-Product Correlation Matrix")
    
    # Create pivot table
    pivot = df.pivot_table(values='Total_Amount', index='Product', columns='State', aggfunc='sum', fill_value=0)
    
    # Filter options
    min_revenue = st.slider("💰 Minimum Revenue Threshold:", 0, int(df['Total_Amount'].max()), 100000)
    
    # Filter pivot
    pivot_filtered = pivot[pivot.sum(axis=1) > min_revenue]
    
    # Heatmap
    fig = px.imshow(pivot_filtered, 
                    labels=dict(x="State", y="Product", color="Revenue"),
                    aspect="auto",
                    color_continuous_scale='YlOrRd')
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 📊 Top State-Product Combinations")
    top_combos = df.groupby(['State', 'Product'])['Total_Amount'].sum().nlargest(20).reset_index()
    st.dataframe(top_combos, use_container_width=True)

# # ==========================================
# # REPORT 5: REGIONAL COMPARISON (FIXED COLORS)
# # ==========================================
# elif report == "🗺️ Regional Comparison":
#     st.markdown("## 🗺️ Multi-State Comparison Tool")
    
#     col1, col2 = st.columns(2)
#     with col1:
#         state1 = st.selectbox("🗺️ Select State 1:", df['State'].unique(), index=0)
#     with col2:
#         state2 = st.selectbox("🗺️ Select State 2:", df['State'].unique(), index=1 if len(df['State'].unique()) > 1 else 0)
    
#     # Comparison logic
#     s1_data = df[df['State'] == state1]
#     s2_data = df[df['State'] == state2]
    
#     cols = st.columns(2)
#     for idx, (state, data) in enumerate([(state1, s1_data), (state2, s2_data)]):
#         with cols[idx]:
#             st.markdown(f"### 🏳️ {state}")
#             st.metric("Revenue", f"{CURRENCY}{data['Total_Amount'].sum():,.0f}")
#             st.metric("Orders", f"{len(data)}")
#             st.metric("Avg Order", f"{CURRENCY}{data['Total_Amount'].mean():,.0f}")
#             st.metric("Top Product", data.groupby('Product')['Total_Amount'].sum().idxmax() if not data.empty else "N/A")
    
#     # Comparison chart with OPPOSITE/CONTRASTING colors
#     comparison_df = pd.DataFrame({
#         state1: s1_data.groupby('Product')['Total_Amount'].sum(),
#         state2: s2_data.groupby('Product')['Total_Amount'].sum()
#     }).fillna(0)
    
#     fig = go.Figure()
#     # State 1 - Blue, State 2 - Orange/Red (Opposite colors)
#     fig.add_trace(go.Bar(name=state1, x=comparison_df.index, y=comparison_df[state1], 
#                         marker_color='#1f77b4'))  # Blue
#     fig.add_trace(go.Bar(name=state2, x=comparison_df.index, y=comparison_df[state2], 
#                         marker_color='#ff7f0e'))  # Orange (opposite of blue)
#     fig.update_layout(barmode='group', title='Product-wise Comparison', xaxis_tickangle=-45)
#     st.plotly_chart(fig, use_container_width=True)
# ==========================================
# REPORT 5: REGIONAL COMPARISON (ENHANCED)
# ==========================================
elif report == "🗺️ Regional Comparison":
    st.markdown("## 🗺️ Multi-State Comparison Tool")
    
    # Year filter for fair comparison
    available_years = sorted(df['Year'].dropna().unique())
    year_options = ["All Years"] + [int(float(y)) if pd.notna(y) else y for y in available_years]
    
    selected_year = st.selectbox("📅 Select Year for Comparison:", year_options)
    
    # Filter data by year if selected
    compare_df = df.copy()
    if selected_year != "All Years":
        compare_df = compare_df[compare_df['Year'].apply(
            lambda x: int(float(x)) if pd.notna(x) else None
        ) == int(selected_year)]
    
    col1, col2 = st.columns(2)
    with col1:
        state1 = st.selectbox("🗺️ Select State 1:", compare_df['State'].unique(), index=0)
    with col2:
        state_options = [s for s in compare_df['State'].unique() if s != state1]
        default_idx = 0 if state_options else 0
        state2 = st.selectbox("🗺️ Select State 2:", state_options if state_options else compare_df['State'].unique(), 
                             index=default_idx)
    
    # Comparison logic
    s1_data = compare_df[compare_df['State'] == state1]
    s2_data = compare_df[compare_df['State'] == state2]
    
    # Calculate metrics
    s1_revenue = s1_data['Total_Amount'].sum()
    s2_revenue = s2_data['Total_Amount'].sum()
    s1_orders = len(s1_data)
    s2_orders = len(s2_data)
    s1_avg = s1_data['Total_Amount'].mean() if not s1_data.empty else 0
    s2_avg = s2_data['Total_Amount'].mean() if not s2_data.empty else 0
    s1_qty = s1_data['Qty'].sum()
    s2_qty = s2_data['Qty'].sum()
    
    # Determine winner
    metrics_comparison = {
        'Revenue': (s1_revenue, s2_revenue),
        'Orders': (s1_orders, s2_orders),
        'Avg Order Value': (s1_avg, s2_avg),
        'Total Quantity': (s1_qty, s2_qty)
    }
    
    s1_wins = sum(1 for v1, v2 in metrics_comparison.values() if v1 > v2)
    s2_wins = sum(1 for v1, v2 in metrics_comparison.values() if v2 > v1)
    
    # Winner announcement
    winner_col = st.container()
    with winner_col:
        if s1_wins > s2_wins:
            st.success(f"🏆 **{state1} WINS!** ({s1_wins}/4 metrics) 🎉")
            st.balloons()
        elif s2_wins > s1_wins:
            st.success(f"🏆 **{state2} WINS!** ({s2_wins}/4 metrics) 🎉")
            st.balloons()
        else:
            st.info(f"🤝 **IT'S A TIE!** Both states won 2 metrics each")
    
    # Metrics comparison cards
    cols = st.columns(2)
    colors = {'win': '#d4edda', 'lose': '#f8d7da', 'tie': '#fff3cd'}
    
    for idx, (state, data, revenue, orders, avg, qty) in enumerate([
        (state1, s1_data, s1_revenue, s1_orders, s1_avg, s1_qty),
        (state2, s2_data, s2_revenue, s2_orders, s2_avg, s2_qty)
    ]):
        with cols[idx]:
            st.markdown(f"### 🏳️ {state}")
            
            # Revenue with comparison indicator
            rev_color = colors['win'] if revenue > s2_revenue else colors['lose'] if revenue < s2_revenue else colors['tie']
            rev_delta = f"+{CURRENCY}{abs(revenue - s2_revenue):,.0f}" if idx == 0 and revenue > s2_revenue else \
                       f"-{CURRENCY}{abs(revenue - s2_revenue):,.0f}" if idx == 0 and revenue < s2_revenue else \
                       f"+{CURRENCY}{abs(revenue - s1_revenue):,.0f}" if idx == 1 and revenue > s1_revenue else \
                       f"-{CURRENCY}{abs(revenue - s1_revenue):,.0f}" if idx == 1 and revenue < s1_revenue else "Tie"
            
            st.metric("💰 Revenue", f"{CURRENCY}{revenue:,.0f}", rev_delta)
            
            # Orders
            ord_delta = f"+{orders - s2_orders}" if idx == 0 and orders > s2_orders else \
                       f"{orders - s2_orders}" if idx == 0 else \
                       f"+{orders - s1_orders}" if orders > s1_orders else f"{orders - s1_orders}"
            st.metric("📦 Orders", f"{orders:,}", ord_delta)
            
            # Avg Order
            st.metric("📊 Avg Order", f"{CURRENCY}{avg:,.0f}")
            
            # Top Product
            top_prod = data.groupby('Product')['Total_Amount'].sum()
            top_product = top_prod.idxmax() if not top_prod.empty else "N/A"
            st.metric("🏆 Top Product", top_product)
            
            # Market Share
            total_market = revenue + (s2_revenue if idx == 0 else s1_revenue)
            share = (revenue / total_market * 100) if total_market > 0 else 0
            st.progress(min(share / 100, 1.0), text=f"Market Share: {share:.1f}%")
    
    st.markdown("---")
    
    # TABS for different comparisons
    tab1, tab2, tab3 = st.tabs(["📊 Product-wise", "📅 Month-wise", "📈 Trend Analysis"])
    
    with tab1:
        st.markdown("### 🔧 Product-wise Comparison")
        comparison_df = pd.DataFrame({
            state1: s1_data.groupby('Product')['Total_Amount'].sum(),
            state2: s2_data.groupby('Product')['Total_Amount'].sum()
        }).fillna(0).reset_index()
        
        # Add difference column
        comparison_df['Difference'] = comparison_df[state1] - comparison_df[state2]
        comparison_df['Winner'] = comparison_df.apply(
            lambda x: state1 if x[state1] > x[state2] else state2 if x[state2] > x[state1] else 'Tie', axis=1
        )
        
        # Chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name=f"{state1} 🔵", 
            x=comparison_df['Product'], 
            y=comparison_df[state1], 
            marker_color='#1f77b4'
        ))
        fig.add_trace(go.Bar(
            name=f"{state2} 🟠", 
            x=comparison_df['Product'], 
            y=comparison_df[state2], 
            marker_color='#ff7f0e'
        ))
        fig.update_layout(
            barmode='group', 
            title='Revenue by Product',
            xaxis_tickangle=-45,
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed table
        with st.expander("📋 View Detailed Product Comparison"):
            display_df = comparison_df.copy()
            display_df[state1] = display_df[state1].apply(lambda x: f"{CURRENCY}{x:,.0f}")
            display_df[state2] = display_df[state2].apply(lambda x: f"{CURRENCY}{x:,.0f}")
            display_df['Difference'] = display_df['Difference'].apply(lambda x: f"{CURRENCY}{x:,.0f}")
            st.dataframe(display_df, use_container_width=True)
    
    with tab2:
        st.markdown("### 📅 Month-wise Comparison")
        
        # Prepare monthly data
        s1_monthly = s1_data.groupby(s1_data['Date'].dt.to_period('M')).agg({
            'Total_Amount': 'sum',
            'Qty': 'sum'
        }).reset_index()
        s1_monthly['Date'] = s1_monthly['Date'].dt.to_timestamp()
        s1_monthly['Month'] = s1_monthly['Date'].dt.strftime('%b %Y')
        
        s2_monthly = s2_data.groupby(s2_data['Date'].dt.to_period('M')).agg({
            'Total_Amount': 'sum',
            'Qty': 'sum'
        }).reset_index()
        s2_monthly['Date'] = s2_monthly['Date'].dt.to_timestamp()
        s2_monthly['Month'] = s2_monthly['Date'].dt.strftime('%b %Y')
        
        # Merge for comparison
        monthly_comparison = pd.merge(
            s1_monthly[['Month', 'Total_Amount', 'Qty']], 
            s2_monthly[['Month', 'Total_Amount', 'Qty']], 
            on='Month', 
            how='outer',
            suffixes=(f'_{state1}', f'_{state2}')
        ).fillna(0)
        
        # Sort by date
        monthly_comparison['Sort_Date'] = pd.to_datetime(monthly_comparison['Month'], format='%b %Y')
        monthly_comparison = monthly_comparison.sort_values('Sort_Date')
        
        # Revenue comparison chart
        fig_rev = go.Figure()
        fig_rev.add_trace(go.Scatter(
            x=monthly_comparison['Month'],
            y=monthly_comparison[f'Total_Amount_{state1}'],
            name=f"{state1} Revenue",
            mode='lines+markers',
            line=dict(color='#1f77b4', width=3),
            fill='tonexty' if len(monthly_comparison) > 1 else None
        ))
        fig_rev.add_trace(go.Scatter(
            x=monthly_comparison['Month'],
            y=monthly_comparison[f'Total_Amount_{state2}'],
            name=f"{state2} Revenue",
            mode='lines+markers',
            line=dict(color='#ff7f0e', width=3),
            fill='tonexty' if len(monthly_comparison) > 1 else None
        ))
        fig_rev.update_layout(
            title='Monthly Revenue Trend Comparison',
            xaxis_title='Month',
            yaxis_title=f'Revenue ({CURRENCY})',
            height=450,
            hovermode='x unified'
        )
        st.plotly_chart(fig_rev, use_container_width=True)
        
        # Quantity comparison
        fig_qty = go.Figure()
        fig_qty.add_trace(go.Bar(
            x=monthly_comparison['Month'],
            y=monthly_comparison[f'Qty_{state1}'],
            name=f"{state1} Quantity",
            marker_color='#1f77b4'
        ))
        fig_qty.add_trace(go.Bar(
            x=monthly_comparison['Month'],
            y=monthly_comparison[f'Qty_{state2}'],
            name=f"{state2} Quantity",
            marker_color='#ff7f0e'
        ))
        fig_qty.update_layout(
            title='Monthly Quantity Comparison',
            barmode='group',
            xaxis_title='Month',
            yaxis_title='Quantity',
            height=400
        )
        st.plotly_chart(fig_qty, use_container_width=True)
        
        # Monthly winner summary
        st.markdown("### 🏆 Monthly Winners")
        monthly_comparison['Revenue_Winner'] = monthly_comparison.apply(
            lambda x: state1 if x[f'Total_Amount_{state1}'] > x[f'Total_Amount_{state2}'] 
            else state2 if x[f'Total_Amount_{state2}'] > x[f'Total_Amount_{state1}'] 
            else 'Tie', axis=1
        )
        
        win_cols = st.columns(4)
        s1_month_wins = (monthly_comparison['Revenue_Winner'] == state1).sum()
        s2_month_wins = (monthly_comparison['Revenue_Winner'] == state2).sum()
        ties = (monthly_comparison['Revenue_Winner'] == 'Tie').sum()
        
        with win_cols[0]:
            st.metric(f"🔵 {state1} Wins", f"{s1_month_wins} months")
        with win_cols[1]:
            st.metric(f"🟠 {state2} Wins", f"{s2_month_wins} months")
        with win_cols[2]:
            st.metric("🤝 Ties", f"{ties} months")
        with win_cols[3]:
            total_months = len(monthly_comparison)
            st.metric("📊 Total Months", total_months)
        
        # Show monthly breakdown table
        with st.expander("📋 View Monthly Breakdown"):
            display_monthly = monthly_comparison[['Month', f'Total_Amount_{state1}', f'Total_Amount_{state2}', 
                                                  f'Qty_{state1}', f'Qty_{state2}', 'Revenue_Winner']].copy()
            display_monthly[f'Total_Amount_{state1}'] = display_monthly[f'Total_Amount_{state1}'].apply(lambda x: f"{CURRENCY}{x:,.0f}")
            display_monthly[f'Total_Amount_{state2}'] = display_monthly[f'Total_Amount_{state2}'].apply(lambda x: f"{CURRENCY}{x:,.0f}")
            st.dataframe(display_monthly, use_container_width=True)
    
    with tab3:
        st.markdown("### 📈 Comprehensive Trend Analysis")
        
        # Growth rate calculation
        if len(s1_monthly) >= 2 and len(s2_monthly) >= 2:
            s1_growth = ((s1_monthly['Total_Amount'].iloc[-1] - s1_monthly['Total_Amount'].iloc[0]) / 
                        s1_monthly['Total_Amount'].iloc[0] * 100)
            s2_growth = ((s2_monthly['Total_Amount'].iloc[-1] - s2_monthly['Total_Amount'].iloc[0]) / 
                        s2_monthly['Total_Amount'].iloc[0] * 100)
            
            growth_cols = st.columns(2)
            with growth_cols[0]:
                growth_color = "normal" if s1_growth > 0 else "inverse"
                st.metric(f"{state1} Growth Rate", f"{s1_growth:+.1f}%", delta_color=growth_color)
            with growth_cols[1]:
                growth_color = "normal" if s2_growth > 0 else "inverse"
                st.metric(f"{state2} Growth Rate", f"{s2_growth:+.1f}%", delta_color=growth_color)
        
        # Cumulative revenue comparison
        s1_data_sorted = s1_data.sort_values('Date')
        s2_data_sorted = s2_data.sort_values('Date')
        s1_data_sorted['Cumulative'] = s1_data_sorted['Total_Amount'].cumsum()
        s2_data_sorted['Cumulative'] = s2_data_sorted['Total_Amount'].cumsum()
        
        fig_cum = go.Figure()
        fig_cum.add_trace(go.Scatter(
            x=s1_data_sorted['Date'],
            y=s1_data_sorted['Cumulative'],
            name=f"{state1} Cumulative",
            line=dict(color='#1f77b4', width=3)
        ))
        fig_cum.add_trace(go.Scatter(
            x=s2_data_sorted['Date'],
            y=s2_data_sorted['Cumulative'],
            name=f"{state2} Cumulative",
            line=dict(color='#ff7f0e', width=3)
        ))
        fig_cum.update_layout(
            title='Cumulative Revenue Over Time',
            xaxis_title='Date',
            yaxis_title=f'Cumulative Revenue ({CURRENCY})',
            height=450
        )
        st.plotly_chart(fig_cum, use_container_width=True)
        
        # Performance radar chart (if enough data)
        categories = ['Revenue', 'Orders', 'Quantity', 'Avg Order', 'Products Sold']
        s1_values = [
            s1_revenue / max(s1_revenue, s2_revenue) * 100 if max(s1_revenue, s2_revenue) > 0 else 0,
            s1_orders / max(s1_orders, s2_orders) * 100 if max(s1_orders, s2_orders) > 0 else 0,
            s1_qty / max(s1_qty, s2_qty) * 100 if max(s1_qty, s2_qty) > 0 else 0,
            s1_avg / max(s1_avg, s2_avg) * 100 if max(s1_avg, s2_avg) > 0 else 0,
            len(s1_data['Product'].unique()) / max(len(s1_data['Product'].unique()), len(s2_data['Product'].unique())) * 100
        ]
        s2_values = [
            s2_revenue / max(s1_revenue, s2_revenue) * 100 if max(s1_revenue, s2_revenue) > 0 else 0,
            s2_orders / max(s1_orders, s2_orders) * 100 if max(s1_orders, s2_orders) > 0 else 0,
            s2_qty / max(s1_qty, s2_qty) * 100 if max(s1_qty, s2_qty) > 0 else 0,
            s2_avg / max(s1_avg, s2_avg) * 100 if max(s1_avg, s2_avg) > 0 else 0,
            len(s2_data['Product'].unique()) / max(len(s1_data['Product'].unique()), len(s2_data['Product'].unique())) * 100
        ]
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=s1_values + [s1_values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name=f'{state1} 🔵',
            line_color='#1f77b4'
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=s2_values + [s2_values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name=f'{state2} 🟠',
            line_color='#ff7f0e'
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            title='Performance Comparison (Normalized)',
            height=500
        )
        st.plotly_chart(fig_radar, use_container_width=True)
# ==========================================
# REPORT 6: REVENUE TRENDS (ENHANCED)
# ==========================================
elif report == "💰 Revenue Trends":
    st.markdown("## 💰 Advanced Revenue Trends & Quarterly Analysis")
    
    # Year selection
    selected_year = st.selectbox("📅 Select Year:", ["All"] + [str(y) for y in years])
    
    trend_df = df.copy()
    if selected_year != "All":
        trend_df = trend_df[trend_df['Year'] == int(selected_year)]
        available_years = [int(selected_year)]
    else:
        available_years = sorted(trend_df['Year'].unique())
    
    # ==========================================
    # MONTHLY TREND ANALYSIS (Enhanced)
    # ==========================================
    st.markdown("### 📈 Monthly Trend Analysis")
    
    monthly_data = trend_df.groupby([trend_df['Date'].dt.year.rename('Year'), 
                                     trend_df['Date'].dt.month.rename('Month')]).agg({
        'Total_Amount': 'sum',
        'Inquiry_No': 'count',
        'Qty': 'sum'
    }).reset_index()
    
    # Create proper date column
    monthly_data['Period'] = pd.to_datetime(monthly_data[['Year', 'Month']].assign(day=1))
    monthly_data = monthly_data.sort_values('Period')
    
    # Calculate MoM Growth
    monthly_data['Revenue_Growth'] = monthly_data['Total_Amount'].pct_change() * 100
    monthly_data['Orders_Growth'] = monthly_data['Inquiry_No'].pct_change() * 100
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue Trend with Growth Indicators
        fig_rev = go.Figure()
        
        fig_rev.add_trace(go.Scatter(
            x=monthly_data['Period'], 
            y=monthly_data['Total_Amount'],
            mode='lines+markers+text',
            name='Revenue',
            line=dict(color='#2E86AB', width=3),
            marker=dict(size=8),
            text=monthly_data['Total_Amount'].apply(lambda x: f'{CURRENCY}{x/100000:.1f}L'),
            textposition='top center',
            textfont=dict(size=9),
            fill='tozeroy',
            fillcolor='rgba(46, 134, 171, 0.2)'
        ))
        
        fig_rev.update_layout(
            title="Monthly Revenue Trend",
            xaxis_title="Month",
            yaxis_title=f"Revenue ({CURRENCY})",
            height=400,
            hovermode='x unified',
            showlegend=False
        )
        st.plotly_chart(fig_rev, use_container_width=True)
    
    with col2:
        # Order Count with Secondary Trend
        fig_ord = go.Figure()
        
        fig_ord.add_trace(go.Bar(
            x=monthly_data['Period'], 
            y=monthly_data['Inquiry_No'],
            name='Orders',
            marker_color='#A23B72',
            text=monthly_data['Inquiry_No'].astype(int),
            textposition='outside'
        ))
        
        # Add trend line
        fig_ord.add_trace(go.Scatter(
            x=monthly_data['Period'], 
            y=monthly_data['Inquiry_No'],
            mode='lines',
            name='Trend',
            line=dict(color='#F18F01', width=2, dash='dash')
        ))
        
        fig_ord.update_layout(
            title="Monthly Order Count",
            xaxis_title="Month",
            yaxis_title="Number of Orders",
            height=400,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig_ord, use_container_width=True)
    
    # Monthly Growth Metrics
    if len(monthly_data) > 1:
        st.markdown("#### 📊 Monthly Growth Metrics")
        latest_month = monthly_data.iloc[-1]
        prev_month = monthly_data.iloc[-2]
        
        m_cols = st.columns(4)
        with m_cols[0]:
            rev_growth = latest_month['Revenue_Growth']
            st.metric(
                "Revenue Growth (MoM)",
                f"{rev_growth:+.1f}%" if pd.notna(rev_growth) else "N/A",
                f"{CURRENCY}{latest_month['Total_Amount'] - prev_month['Total_Amount']:,.0f}" if pd.notna(rev_growth) else "",
                delta_color="normal" if pd.notna(rev_growth) and rev_growth > 0 else "inverse" if pd.notna(rev_growth) else "off"
            )
        with m_cols[1]:
            ord_growth = latest_month['Orders_Growth']
            st.metric(
                "Orders Growth (MoM)",
                f"{ord_growth:+.1f}%" if pd.notna(ord_growth) else "N/A",
                f"{int(latest_month['Inquiry_No'] - prev_month['Inquiry_No'])} orders" if pd.notna(ord_growth) else "",
                delta_color="normal" if pd.notna(ord_growth) and ord_growth > 0 else "inverse" if pd.notna(ord_growth) else "off"
            )
        with m_cols[2]:
            st.metric(
                "Avg Monthly Revenue",
                f"{CURRENCY}{monthly_data['Total_Amount'].mean():,.0f}",
                f"Peak: {CURRENCY}{monthly_data['Total_Amount'].max():,.0f}"
            )
        with m_cols[3]:
            best_month = monthly_data.loc[monthly_data['Total_Amount'].idxmax(), 'Period']
            st.metric(
                "Best Month",
                best_month.strftime('%b %Y'),
                f"{CURRENCY}{monthly_data['Total_Amount'].max():,.0f}"
            )
    
    # ==========================================
    # QUARTERLY ANALYSIS (Enhanced)
    # ==========================================
    st.markdown("---")
    st.markdown("### 📊 Quarterly Performance Deep Dive")
    
    # Create Quarter labels
    trend_df['Year_Quarter'] = trend_df['Date'].dt.to_period('Q')
    trend_df['Quarter'] = trend_df['Date'].dt.quarter
    trend_df['Year'] = trend_df['Date'].dt.year
    
    quarterly = trend_df.groupby(['Year', 'Quarter']).agg({
        'Total_Amount': 'sum',
        'Inquiry_No': 'count',
        'Qty': 'sum'
    }).reset_index()
    
    quarterly['Quarter_Label'] = 'Q' + quarterly['Quarter'].astype(str) + ' ' + quarterly['Year'].astype(str)
    quarterly['Avg_Order_Value'] = quarterly['Total_Amount'] / quarterly['Inquiry_No']
    
    # Sort properly
    quarterly = quarterly.sort_values(['Year', 'Quarter'])
    
    # Calculate QoQ Growth
    quarterly['QoQ_Revenue_Growth'] = quarterly['Total_Amount'].pct_change() * 100
    quarterly['QoQ_Orders_Growth'] = quarterly['Inquiry_No'].pct_change() * 100
    
    # Quarterly KPI Cards
    st.markdown("#### 🎯 Quarterly Key Metrics")
    
    # Create columns for each quarter found
    q_cols = st.columns(len(quarterly))
    for idx, (_, row) in enumerate(quarterly.iterrows()):
        with q_cols[idx]:
            st.markdown(f"**{row['Quarter_Label']}**")
            st.metric(
                "Revenue",
                f"{CURRENCY}{row['Total_Amount']:,.0f}",
                None
            )
            st.metric(
                "Orders",
                f"{int(row['Inquiry_No'])}",
                None
            )
            st.metric(
                "AOV",
                f"{CURRENCY}{row['Avg_Order_Value']:,.0f}",
                None
            )
    
    # Quarter-over-Quarter Analysis
    if len(quarterly) > 1:
        st.markdown("#### 📈 Quarter-over-Quarter Growth")
        
        qoq_cols = st.columns(min(len(quarterly)-1, 4))
        for i in range(1, len(quarterly)):
            if i-1 < len(qoq_cols):
                with qoq_cols[i-1]:
                    curr = quarterly.iloc[i]
                    prev = quarterly.iloc[i-1]
                    rev_growth = curr['QoQ_Revenue_Growth']
                    
                    st.metric(
                        label=f"{prev['Quarter_Label']} → {curr['Quarter_Label']}",
                        value=f"{rev_growth:+.1f}%" if pd.notna(rev_growth) else "N/A",
                        delta=f"{CURRENCY}{curr['Total_Amount'] - prev['Total_Amount']:,.0f}" if pd.notna(rev_growth) else "",
                        delta_color="normal" if pd.notna(rev_growth) and rev_growth > 0 else "inverse"
                    )
    
    # Quarterly Visualizations
    st.markdown("#### 📊 Quarterly Visualizations")
    
    col_q1, col_q2 = st.columns(2)
    
    with col_q1:
        # Quarterly Revenue Trend
        fig_qtr = go.Figure()
        
        colors_q = px.colors.qualitative.Prism[:len(quarterly)]
        
        fig_qtr.add_trace(go.Bar(
            x=quarterly['Quarter_Label'],
            y=quarterly['Total_Amount'],
            marker_color=colors_q,
            text=quarterly['Total_Amount'].apply(lambda x: f'{CURRENCY}{x/100000:.1f}L'),
            textposition='outside'
        ))
        
        # Add trend line
        fig_qtr.add_trace(go.Scatter(
            x=quarterly['Quarter_Label'],
            y=quarterly['Total_Amount'],
            mode='lines+markers',
            line=dict(color='red', width=2),
            marker=dict(size=10),
            name='Trend'
        ))
        
        fig_qtr.update_layout(
            title="Quarterly Revenue Trend",
            xaxis_title="Quarter",
            yaxis_title=f"Revenue ({CURRENCY})",
            height=400,
            showlegend=False,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_qtr, use_container_width=True)
    
    with col_q2:
        # Quarterly Orders vs AOV
        fig_q_combo = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig_q_combo.add_trace(
            go.Bar(
                x=quarterly['Quarter_Label'],
                y=quarterly['Inquiry_No'],
                name="Orders",
                marker_color='lightblue',
                text=quarterly['Inquiry_No'].astype(int),
                textposition='outside'
            ),
            secondary_y=False
        )
        
        fig_q_combo.add_trace(
            go.Scatter(
                x=quarterly['Quarter_Label'],
                y=quarterly['Avg_Order_Value'],
                name="AOV",
                mode='lines+markers',
                line=dict(color='darkred', width=3),
                marker=dict(size=10)
            ),
            secondary_y=True
        )
        
        fig_q_combo.update_layout(
            title="Orders vs Average Order Value by Quarter",
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            xaxis_tickangle=-45
        )
        fig_q_combo.update_yaxes(title_text="Number of Orders", secondary_y=False)
        fig_q_combo.update_yaxes(title_text=f"Avg Order Value ({CURRENCY})", secondary_y=True)
        
        st.plotly_chart(fig_q_combo, use_container_width=True)
    
    # Quarterly Comparison Table
    st.markdown("#### 📋 Quarterly Performance Table")
    
    # Prepare display table
    display_qtr = quarterly[['Quarter_Label', 'Total_Amount', 'Inquiry_No', 'Avg_Order_Value', 'QoQ_Revenue_Growth']].copy()
    display_qtr.columns = ['Quarter', 'Revenue', 'Orders', 'AOV', 'QoQ Growth']
    
    # Format columns
    display_qtr['Revenue'] = display_qtr['Revenue'].apply(lambda x: f"{CURRENCY}{x:,.0f}")
    display_qtr['Orders'] = display_qtr['Orders'].apply(lambda x: f"{int(x)}")
    display_qtr['AOV'] = display_qtr['AOV'].apply(lambda x: f"{CURRENCY}{x:,.0f}")
    display_qtr['QoQ Growth'] = display_qtr['QoQ Growth'].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else "-")
    
    st.table(display_qtr.set_index('Quarter'))
    
    # Year-over-Year Quarterly Comparison (if multiple years selected)
    if len(available_years) > 1:
        st.markdown("#### 🔄 Year-over-Year Quarterly Comparison")
        
        # Pivot for comparison
        qtr_pivot = quarterly.pivot(index='Quarter', columns='Year', values='Total_Amount').fillna(0)
        
        fig_yoy = go.Figure()
        
        colors_yoy = px.colors.qualitative.Set2[:len(available_years)]
        for idx, year in enumerate(available_years):
            if year in qtr_pivot.columns:
                fig_yoy.add_trace(go.Bar(
                    name=str(year),
                    x=['Q1', 'Q2', 'Q3', 'Q4'],
                    y=qtr_pivot[year],
                    marker_color=colors_yoy[idx],
                    text=qtr_pivot[year].apply(lambda x: f'{CURRENCY}{x/100000:.1f}L' if x > 0 else ''),
                    textposition='outside'
                ))
        
        fig_yoy.update_layout(
            title="Quarterly Revenue Comparison Across Years",
            xaxis_title="Quarter",
            yaxis_title=f"Revenue ({CURRENCY})",
            barmode='group',
            height=450,
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig_yoy, use_container_width=True)
        
        # YoY Growth by Quarter
        if len(available_years) == 2:
            y1, y2 = available_years
            if y1 in qtr_pivot.columns and y2 in qtr_pivot.columns:
                st.markdown(f"**{y1} vs {y2} Quarterly Growth:**")
                yoy_cols = st.columns(4)
                for q in [1, 2, 3, 4]:
                    if q in qtr_pivot.index:
                        val_prev = qtr_pivot.loc[q, y1]
                        val_curr = qtr_pivot.loc[q, y2]
                        if val_prev > 0:
                            growth = ((val_curr - val_prev) / val_prev * 100)
                            with yoy_cols[q-1]:
                                st.metric(
                                    f"Q{q} Growth",
                                    f"{growth:+.1f}%",
                                    f"{CURRENCY}{val_curr - val_prev:,.0f}",
                                    delta_color="normal" if growth > 0 else "inverse"
                                )
    
    # Quarterly Insights Summary
    st.markdown("#### 🎯 Quarterly Insights")
    
    best_qtr = quarterly.loc[quarterly['Total_Amount'].idxmax()]
    worst_qtr = quarterly.loc[quarterly['Total_Amount'].idxmin()]
    avg_qtr_revenue = quarterly['Total_Amount'].mean()
    
    insight_cols = st.columns(3)
    with insight_cols[0]:
        st.metric(
            "🏆 Best Quarter",
            best_qtr['Quarter_Label'],
            f"{CURRENCY}{best_qtr['Total_Amount']:,.0f}"
        )
    with insight_cols[1]:
        st.metric(
            "📉 Lowest Quarter",
            worst_qtr['Quarter_Label'],
            f"{CURRENCY}{worst_qtr['Total_Amount']:,.0f}"
        )
    with insight_cols[2]:
        st.metric(
            "📊 Quarterly Average",
            f"{CURRENCY}{avg_qtr_revenue:,.0f}",
            f"Total: {CURRENCY}{quarterly['Total_Amount'].sum():,.0f}"
        )
    
    # Cumulative Trend
    st.markdown("#### 📈 Cumulative Revenue Trend")
    quarterly['Cumulative_Revenue'] = quarterly['Total_Amount'].cumsum()
    
    fig_cum = go.Figure()
    fig_cum.add_trace(go.Scatter(
        x=quarterly['Quarter_Label'],
        y=quarterly['Cumulative_Revenue'],
        mode='lines+markers+text',
        fill='tozeroy',
        line=dict(color='green', width=3),
        marker=dict(size=10),
        text=quarterly['Cumulative_Revenue'].apply(lambda x: f'{CURRENCY}{x/100000:.1f}L'),
        textposition='top center'
    ))
    
    fig_cum.update_layout(
        height=400,
        xaxis_title="Quarter",
        yaxis_title=f"Cumulative Revenue ({CURRENCY})",
        showlegend=False,
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig_cum, use_container_width=True)

# ==========================================
# REPORT 7: YEAR-WISE ANALYSIS
# ==========================================
elif report == "💰 Year-wise Analysis":
    st.markdown("## 💰 Year-over-Year Growth Analysis")
    
    # Get available years
    available_years = sorted(df['Year'].unique())
    
    if len(available_years) < 1:
        st.warning("No year data available")
        st.stop()
    
    # Year selection dropdowns
    col1, col2 = st.columns(2)
    with col1:
        base_year = st.selectbox("📅 Select Base Year:", available_years, index=0)
    with col2:
        compare_years = [y for y in available_years if y != base_year]
        if compare_years:
            comparison_year = st.selectbox("📅 Compare With Year:", compare_years, index=len(compare_years)-1 if len(compare_years) > 0 else 0)
        else:
            comparison_year = None
            st.info("Only one year available in dataset")
    
    # Calculate yearly stats
    yearly_stats = df.groupby('Year').agg({
        'Total_Amount': ['sum', 'mean', 'count'],
        'Qty': 'sum',
        'Company': 'nunique'
    }).round(2)
    
    yearly_stats.columns = ['Total_Revenue', 'Avg_Order_Value', 'Total_Orders', 'Total_Qty', 'Unique_Customers']
    
    # Display stats for selected years
    if base_year in yearly_stats.index:
        base_data = yearly_stats.loc[base_year]
        
        st.markdown(f"### 📊 {base_year} Performance")
        cols = st.columns(5)
        with cols[0]:
            st.metric("💰 Revenue", f"{CURRENCY}{base_data['Total_Revenue']:,.0f}")
        with cols[1]:
            st.metric("📦 Orders", f"{int(base_data['Total_Orders'])}")
        with cols[2]:
            st.metric("📊 Avg Order", f"{CURRENCY}{base_data['Avg_Order_Value']:,.0f}")
        with cols[3]:
            st.metric("🏭 Quantity", f"{int(base_data['Total_Qty'])}")
        with cols[4]:
            st.metric("🏢 Customers", f"{int(base_data['Unique_Customers'])}")
    
    # Year-to-Year Comparison
    if comparison_year and comparison_year in yearly_stats.index:
        st.markdown("---")
        st.markdown(f"### 📈 {base_year} vs {comparison_year} - Growth Analysis")
        
        comp_data = yearly_stats.loc[comparison_year]
        
        # Calculate differences
        revenue_diff = base_data['Total_Revenue'] - comp_data['Total_Revenue']
        orders_diff = base_data['Total_Orders'] - comp_data['Total_Orders']
        qty_diff = base_data['Total_Qty'] - comp_data['Total_Qty']
        
        # Calculate growth percentages
        revenue_growth = ((base_data['Total_Revenue'] / comp_data['Total_Revenue']) - 1) * 100 if comp_data['Total_Revenue'] > 0 else 0
        orders_growth = ((base_data['Total_Orders'] / comp_data['Total_Orders']) - 1) * 100 if comp_data['Total_Orders'] > 0 else 0
        qty_growth = ((base_data['Total_Qty'] / comp_data['Total_Qty']) - 1) * 100 if comp_data['Total_Qty'] > 0 else 0
        avg_order_growth = ((base_data['Avg_Order_Value'] / comp_data['Avg_Order_Value']) - 1) * 100 if comp_data['Avg_Order_Value'] > 0 else 0
        
        # Comparison Table
        comparison_data = {
            'Metric': ['Total Revenue', 'Total Orders', 'Quantity Sold', 'Avg Order Value', 'Active Customers'],
            base_year: [
                f"{CURRENCY}{base_data['Total_Revenue']:,.0f}",
                f"{int(base_data['Total_Orders'])}",
                f"{int(base_data['Total_Qty'])}",
                f"{CURRENCY}{base_data['Avg_Order_Value']:,.0f}",
                f"{int(base_data['Unique_Customers'])}"
            ],
            comparison_year: [
                f"{CURRENCY}{comp_data['Total_Revenue']:,.0f}",
                f"{int(comp_data['Total_Orders'])}",
                f"{int(comp_data['Total_Qty'])}",
                f"{CURRENCY}{comp_data['Avg_Order_Value']:,.0f}",
                f"{int(comp_data['Unique_Customers'])}"
            ],
            'Difference': [
                f"{CURRENCY}{revenue_diff:,.0f}",
                f"{int(orders_diff)}",
                f"{int(qty_diff)}",
                f"{CURRENCY}{base_data['Avg_Order_Value'] - comp_data['Avg_Order_Value']:,.0f}",
                f"{int(base_data['Unique_Customers'] - comp_data['Unique_Customers'])}"
            ],
            'Growth %': [
                f"{revenue_growth:+.2f}%",
                f"{orders_growth:+.2f}%",
                f"{qty_growth:+.2f}%",
                f"{avg_order_growth:+.2f}%",
                f"{((base_data['Unique_Customers']/comp_data['Unique_Customers'])-1)*100:+.2f}%" if comp_data['Unique_Customers'] > 0 else "N/A"
            ]
        }
        
        comp_df = pd.DataFrame(comparison_data)
        st.table(comp_df.set_index('Metric'))
        
        # Growth indicators
        st.markdown("### 📊 Growth Indicators")
        cols = st.columns(4)
        
        with cols[0]:
            delta_color = "normal" if revenue_growth > 0 else "inverse"
            st.metric(label="💰 Revenue Growth", value=f"{revenue_growth:+.2f}%", delta=f"{CURRENCY}{revenue_diff:,.0f}", delta_color=delta_color)
        
        with cols[1]:
            delta_color = "normal" if orders_growth > 0 else "inverse"
            st.metric(label="📦 Orders Growth", value=f"{orders_growth:+.2f}%", delta=f"{int(orders_diff)} orders", delta_color=delta_color)
        
        with cols[2]:
            delta_color = "normal" if qty_growth > 0 else "inverse"
            st.metric(label="🏭 Quantity Growth", value=f"{qty_growth:+.2f}%", delta=f"{int(qty_diff)} units", delta_color=delta_color)
        
        with cols[3]:
            delta_color = "normal" if avg_order_growth > 0 else "inverse"
            st.metric(label="📊 AOV Growth", value=f"{avg_order_growth:+.2f}%", delta=f"{CURRENCY}{base_data['Avg_Order_Value'] - comp_data['Avg_Order_Value']:,.0f}", delta_color=delta_color)
        
        # Visual indicator
        if revenue_growth > 0:
            st.success(f"✅ Growth of {revenue_growth:.2f}% from {comparison_year} to {base_year}")
        else:
            st.error(f"⚠️ Decline of {abs(revenue_growth):.2f}% from {comparison_year} to {base_year}")
    
    elif len(available_years) == 1:
        # Only one year available - show detailed breakdown
        st.info(f"📊 Only {available_years[0]} data available. Showing detailed breakdown...")
        
        # Monthly breakdown for single year
        year_df = df[df['Year'] == available_years[0]]
        monthly = year_df.groupby(year_df['Date'].dt.month).agg({
            'Total_Amount': 'sum',
            'Inquiry_No': 'count',
            'Qty': 'sum'
        }).round(2)
        monthly.columns = ['Revenue', 'Orders', 'Quantity']
        monthly.index = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][:len(monthly)]
        
        st.markdown(f"### 📅 {available_years[0]} Monthly Breakdown")
        st.table(monthly.style.format({
            'Revenue': lambda x: f"{CURRENCY}{x:,.0f}",
            'Orders': lambda x: f"{int(x)}",
            'Quantity': lambda x: f"{int(x)}"
        }))
    
    # All Years Line Chart
    if len(available_years) >= 2:
        st.markdown("---")
        st.markdown("### 📈 All Years Growth Trend")
        
        # Calculate growth for all years
        yearly_growth = yearly_stats.copy()
        yearly_growth['Revenue_Growth_Pct'] = yearly_growth['Total_Revenue'].pct_change() * 100
        yearly_growth['Orders_Growth_Pct'] = yearly_growth['Total_Orders'].pct_change() * 100
        
        # Create two charts side by side
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 💰 Revenue Trend (All Years)")
            fig1 = go.Figure()
            
            fig1.add_trace(go.Scatter(
                x=yearly_growth.index,
                y=yearly_growth['Total_Revenue'],
                mode='lines+markers+text',
                name='Revenue',
                text=yearly_growth['Total_Revenue'].apply(lambda x: f'{CURRENCY}{x/100000:.0f}L'),
                textposition='top center',
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=10)
            ))
            
            fig1.update_layout(
                height=400,
                xaxis_title="Year",
                yaxis_title=f"Revenue ({CURRENCY})",
                showlegend=False,
                xaxis=dict(tickmode='linear', tick0=min(available_years), dtick=1)
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            st.markdown("#### 📊 Year-over-Year Growth %")
            fig2 = go.Figure()
            
            # Filter out first year (no growth data)
            growth_data = yearly_growth[yearly_growth['Revenue_Growth_Pct'].notna()]
            
            colors = ['green' if x > 0 else 'red' for x in growth_data['Revenue_Growth_Pct']]
            
            fig2.add_trace(go.Bar(
                x=growth_data.index,
                y=growth_data['Revenue_Growth_Pct'],
                marker_color=colors,
                text=growth_data['Revenue_Growth_Pct'].apply(lambda x: f'{x:+.1f}%'),
                textposition='outside'
            ))
            
            fig2.add_hline(y=0, line_dash="dash", line_color="gray")
            
            fig2.update_layout(
                height=400,
                xaxis_title="Year",
                yaxis_title="Growth %",
                showlegend=False,
                xaxis=dict(tickmode='linear', tick0=min(available_years), dtick=1)
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Summary statistics for all years
        st.markdown("#### 📋 Year-over-Year Summary")
        summary_df = pd.DataFrame({
            'Year': yearly_growth.index,
            'Revenue': yearly_growth['Total_Revenue'].apply(lambda x: f"{CURRENCY}{x:,.0f}"),
            'Growth vs Previous': yearly_growth['Revenue_Growth_Pct'].apply(lambda x: f"{x:+.2f}%" if pd.notna(x) else "Base Year"),
            'Orders': yearly_growth['Total_Orders'].astype(int),
            'Order Growth': yearly_growth['Orders_Growth_Pct'].apply(lambda x: f"{x:+.2f}%" if pd.notna(x) else "-")
        })
        st.table(summary_df.set_index('Year'))

# ==========================================
# REPORT 8: MONTHLY INSIGHTS (FIXED)
# ==========================================
elif report == "💰 Monthly Insights":
    st.markdown("## 💰 Monthly Deep Dive & Seasonal Analysis")
    
    # Select multiple years for comparison
    selected_years = st.multiselect(
        "📅 Select Years to Compare:", 
        sorted(years), 
        default=sorted(years)[-2:] if len(years) >= 2 else years,
        help="Select multiple years to compare month-wise trends"
    )
    
    # State filter
    state_options = ["All States"] + sorted(df['State'].unique().tolist())
    selected_state_monthly = st.selectbox("🗺️ Filter by State:", state_options)
    
    if not selected_years:
        st.warning("Please select at least one year")
        st.stop()
    
    # Filter data
    filtered_df = df[df['Year'].isin(selected_years)]
    if selected_state_monthly != "All States":
        filtered_df = filtered_df[filtered_df['State'] == selected_state_monthly]
    
    # Prepare month-wise data
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    monthly_data = filtered_df.groupby(['Year', 'Month_Name']).agg({
        'Total_Amount': 'sum',
        'Inquiry_No': 'count',
        'Qty': 'sum'
    }).reset_index()
    
    # ==========================================
    # MONTH-WISE TREND CHARTS
    # ==========================================
    st.markdown(f"### 📈 Month-wise Trend Comparison - {selected_state_monthly}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💰 Revenue by Month")
        
        fig_revenue = go.Figure()
        colors = px.colors.qualitative.Set2[:len(selected_years)]
        
        for idx, year in enumerate(selected_years):
            year_data = monthly_data[monthly_data['Year'] == year]
            if not year_data.empty:
                # Sort by month order
                year_data['Month_Num'] = year_data['Month_Name'].apply(lambda x: month_order.index(x) if x in month_order else 0)
                year_data = year_data.sort_values('Month_Num')
                
                fig_revenue.add_trace(go.Scatter(
                    x=year_data['Month_Name'],
                    y=year_data['Total_Amount'],
                    mode='lines+markers+text',
                    name=str(year),
                    line=dict(color=colors[idx], width=3),
                    marker=dict(size=8),
                    text=year_data['Total_Amount'].apply(lambda x: f'{CURRENCY}{x/100000:.1f}L'),
                    textposition='top center',
                    textfont=dict(size=9)
                ))
        
        fig_revenue.update_layout(
            height=450,
            xaxis_title="Month",
            yaxis_title=f"Revenue ({CURRENCY})",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(categoryorder='array', categoryarray=month_order),
            hovermode='x unified',
            margin=dict(l=50, r=50, t=80, b=50)
        )
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    with col2:
        st.markdown("#### 📊 Order Count by Month")
        
        fig_orders = go.Figure()
        
        for idx, year in enumerate(selected_years):
            year_data = monthly_data[monthly_data['Year'] == year]
            if not year_data.empty:
                year_data['Month_Num'] = year_data['Month_Name'].apply(lambda x: month_order.index(x) if x in month_order else 0)
                year_data = year_data.sort_values('Month_Num')
                
                fig_orders.add_trace(go.Bar(
                    x=year_data['Month_Name'],
                    y=year_data['Inquiry_No'],
                    name=str(year),
                    marker_color=colors[idx],
                    text=year_data['Inquiry_No'].astype(int),
                    textposition='outside'
                ))
        
        fig_orders.update_layout(
            height=450,
            xaxis_title="Month",
            yaxis_title="Number of Orders",
            barmode='group',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(categoryorder='array', categoryarray=month_order),
            margin=dict(l=50, r=50, t=80, b=50)
        )
        st.plotly_chart(fig_orders, use_container_width=True)
    
    # ==========================================
    # COMPARISON TABLE
    # ==========================================
    st.markdown("---")
    st.markdown("### 📋 Month-wise Comparison Table")
    
    # Create pivot table
    pivot_revenue = monthly_data.pivot(index='Month_Name', columns='Year', values='Total_Amount').fillna(0)
    pivot_orders = monthly_data.pivot(index='Month_Name', columns='Year', values='Inquiry_No').fillna(0)
    
    # Reindex to ensure correct month order
    pivot_revenue = pivot_revenue.reindex([m for m in month_order if m in pivot_revenue.index])
    pivot_orders = pivot_orders.reindex([m for m in month_order if m in pivot_orders.index])
    
    # Display tabs for Revenue and Orders
    tab1, tab2 = st.tabs(["💰 Revenue", "📦 Orders"])
    
    with tab1:
        # Format for display
        display_rev = pivot_revenue.copy()
        for year in selected_years:
            if year in display_rev.columns:
                display_rev[year] = display_rev[year].apply(lambda x: f"{CURRENCY}{x:,.0f}" if x > 0 else "-")
        
        # Add YoY Growth column if 2+ years selected
        if len(selected_years) == 2:
            y1, y2 = sorted(selected_years)
            if y1 in pivot_revenue.columns and y2 in pivot_revenue.columns:
                growth = ((pivot_revenue[y2] - pivot_revenue[y1]) / pivot_revenue[y1] * 100).round(1)
                display_rev['Growth %'] = growth.apply(lambda x: f"{x:+.1f}%" if pd.notna(x) and x != 0 else "-")
        
        st.table(display_rev)
        
        # Total row
        totals = pivot_revenue.sum()
        st.markdown("**Total:**")
        cols = st.columns(len(selected_years) + (1 if len(selected_years) == 2 else 0))
        for idx, year in enumerate(selected_years):
            with cols[idx]:
                st.metric(f"{year}", f"{CURRENCY}{totals[year]:,.0f}")

    # ==========================================
    # YEAR-WISE SUMMARY SECTION
    # ==========================================
    st.markdown("---")
    st.markdown("### 🗓️ Year-wise Performance Summary")
    
    # Calculate year-wise totals
    yearly_summary = filtered_df.groupby('Year').agg({
        'Total_Amount': 'sum',
        'Inquiry_No': 'count',
        'Qty': 'sum'
    }).reset_index()
    
    # Calculate additional metrics
    yearly_summary['Avg_Order_Value'] = yearly_summary['Total_Amount'] / yearly_summary['Inquiry_No']
    yearly_summary = yearly_summary.sort_values('Year')
    
    # Year-wise KPI Cards
    st.markdown("#### 📊 Key Metrics by Year")
    year_cols = st.columns(len(selected_years))
    
    for idx, row in yearly_summary.iterrows():
        with year_cols[idx]:
            st.markdown(f"**{int(row['Year'])}**")
            st.metric(
                label="Total Revenue",
                value=f"{CURRENCY}{row['Total_Amount']:,.0f}",
                delta=None
            )
            st.metric(
                label="Total Orders",
                value=f"{int(row['Inquiry_No'])}",
                delta=None
            )
            st.metric(
                label="Avg Order Value",
                value=f"{CURRENCY}{row['Avg_Order_Value']:,.0f}",
                delta=None
            )
    
    # Year-over-Year Growth Calculation
    if len(yearly_summary) > 1:
        st.markdown("#### 📈 Year-over-Year Growth")
        
        yoy_data = yearly_summary.copy()
        yoy_data['Revenue_Growth'] = yoy_data['Total_Amount'].pct_change() * 100
        yoy_data['Orders_Growth'] = yoy_data['Inquiry_No'].pct_change() * 100
        yoy_data['AOV_Growth'] = yoy_data['Avg_Order_Value'].pct_change() * 100
        
        # Display YoY metrics
        yoy_cols = st.columns(3)
        
        # Get the latest comparison (last year vs previous)
        latest_yoy = yoy_data.iloc[-1]
        prev_year = yoy_data.iloc[-2]['Year']
        curr_year = latest_yoy['Year']
        
        with yoy_cols[0]:
            rev_growth = latest_yoy['Revenue_Growth']
            st.metric(
                label=f"Revenue Growth ({int(prev_year)} → {int(curr_year)})",
                value=f"{rev_growth:+.1f}%",
                delta=f"{CURRENCY}{latest_yoy['Total_Amount'] - yoy_data.iloc[-2]['Total_Amount']:,.0f}",
                delta_color="normal" if rev_growth > 0 else "inverse"
            )
        
        with yoy_cols[1]:
            ord_growth = latest_yoy['Orders_Growth']
            st.metric(
                label=f"Orders Growth ({int(prev_year)} → {int(curr_year)})",
                value=f"{ord_growth:+.1f}%",
                delta=f"{int(latest_yoy['Inquiry_No'] - yoy_data.iloc[-2]['Inquiry_No'])} orders",
                delta_color="normal" if ord_growth > 0 else "inverse"
            )
        
        with yoy_cols[2]:
            aov_growth = latest_yoy['AOV_Growth']
            st.metric(
                label=f"AOV Growth ({int(prev_year)} → {int(curr_year)})",
                value=f"{aov_growth:+.1f}%",
                delta=f"{CURRENCY}{latest_yoy['Avg_Order_Value'] - yoy_data.iloc[-2]['Avg_Order_Value']:,.0f}",
                delta_color="normal" if aov_growth > 0 else "inverse"
            )
    
    # ==========================================
    # YEAR-WISE COMPARISON TABLE
    # ==========================================
    st.markdown("#### 📋 Year-wise Detailed Comparison")
    
    # Prepare display table
    display_yearly = yearly_summary.copy()
    display_yearly.columns = ['Year', 'Total Revenue', 'Total Orders', 'Total Qty', 'Avg Order Value']
    
    # Format for display
    for col in ['Total Revenue', 'Avg Order Value']:
        display_yearly[col] = display_yearly[col].apply(lambda x: f"{CURRENCY}{x:,.0f}")
    display_yearly['Total Orders'] = display_yearly['Total Orders'].apply(lambda x: f"{int(x)}")
    display_yearly['Total Qty'] = display_yearly['Total Qty'].apply(lambda x: f"{int(x)}")
    
    # Add YoY Growth columns if multiple years
    if len(yearly_summary) > 1:
        for i in range(1, len(yearly_summary)):
            prev_rev = yearly_summary.iloc[i-1]['Total_Amount']
            curr_rev = yearly_summary.iloc[i]['Total_Amount']
            growth = ((curr_rev - prev_rev) / prev_rev * 100)
            display_yearly.loc[i, 'YoY Growth'] = f"{growth:+.1f}%"
    
    st.table(display_yearly.set_index('Year').transpose())
    
    # ==========================================
    # YEAR-WISE VISUAL TRENDS
    # ==========================================
    st.markdown("#### 📊 Year-wise Trend Visualization")
    
    col_y1, col_y2 = st.columns(2)
    
    with col_y1:
        # Year-wise Revenue Bar Chart
        fig_year_rev = go.Figure()
        
        colors_years = px.colors.qualitative.Bold[:len(yearly_summary)]
        
        fig_year_rev.add_trace(go.Bar(
            x=yearly_summary['Year'].astype(str),
            y=yearly_summary['Total_Amount'],
            marker_color=colors_years,
            text=yearly_summary['Total_Amount'].apply(lambda x: f'{CURRENCY}{x/100000:.1f}L'),
            textposition='outside'
        ))
        
        # Add trend line if 2+ years
        if len(yearly_summary) > 1:
            fig_year_rev.add_trace(go.Scatter(
                x=yearly_summary['Year'].astype(str),
                y=yearly_summary['Total_Amount'],
                mode='lines+markers',
                line=dict(color='red', width=2, dash='dash'),
                marker=dict(size=10),
                name='Trend'
            ))
        
        fig_year_rev.update_layout(
            title="Annual Revenue Trend",
            xaxis_title="Year",
            yaxis_title=f"Revenue ({CURRENCY})",
            height=400,
            showlegend=False,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        st.plotly_chart(fig_year_rev, use_container_width=True)
    
    with col_y2:
        # Year-wise Orders & AOV Combo Chart
        fig_year_combo = go.Figure()
        
        # Bar chart for Orders
        fig_year_combo.add_trace(go.Bar(
            x=yearly_summary['Year'].astype(str),
            y=yearly_summary['Inquiry_No'],
            name='Orders',
            marker_color='lightblue',
            yaxis='y',
            text=yearly_summary['Inquiry_No'].astype(int),
            textposition='outside'
        ))
        
        # Line chart for AOV
        fig_year_combo.add_trace(go.Scatter(
            x=yearly_summary['Year'].astype(str),
            y=yearly_summary['Avg_Order_Value'],
            name='Avg Order Value',
            mode='lines+markers',
            line=dict(color='darkred', width=3),
            marker=dict(size=10),
            yaxis='y2'
        ))
        
        fig_year_combo.update_layout(
            title="Orders vs Avg Order Value",
            xaxis_title="Year",
            yaxis=dict(
                title="Number of Orders",
                side="left"
            ),
            yaxis2=dict(
                title=f"Avg Order Value ({CURRENCY})",
                side="right",
                overlaying="y",
                showgrid=False
            ),
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=50, r=50, t=80, b=50)
        )
        st.plotly_chart(fig_year_combo, use_container_width=True)

    # ==========================================
    # SEASONAL INSIGHTS
    # ==========================================
    st.markdown("---")
    st.markdown("### 🎯 Seasonal Insights")
    
    if len(selected_years) > 0:
        # Find peak months across all selected years
        all_months = monthly_data.groupby('Month_Name')['Total_Amount'].sum().sort_values(ascending=False)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🏆 Peak Month", all_months.index[0], f"{CURRENCY}{all_months.iloc[0]:,.0f}")
        with col2:
            st.metric("📉 Lowest Month", all_months.index[-1], f"{CURRENCY}{all_months.iloc[-1]:,.0f}")
        with col3:
            avg_monthly = all_months.mean()
            st.metric("📊 Avg Monthly", f"{CURRENCY}{avg_monthly:,.0f}")
        
        # Top 3 months
        st.markdown("**Top 3 Performing Months:**")
        for i, (month, revenue) in enumerate(all_months.head(3).items(), 1):
            pct = (revenue / all_months.sum()) * 100
            st.write(f"{i}. **{month}**: {CURRENCY}{revenue:,.0f} ({pct:.1f}% of total)")

# ==========================================
# REPORT 9: TOP REVENUE SOURCES (ENHANCED)
# ==========================================
elif report == "💰 Top Revenue Sources":
    st.markdown("## 💰 Revenue Contribution & Distribution Analysis")
    
    # Calculate contributions
    total_revenue = df['Total_Amount'].sum()
    
    # State contribution
    state_revenue = df.groupby('State').agg({
        'Total_Amount': ['sum', 'count', 'mean'],
        'Qty': 'sum'
    }).round(2)
    state_revenue.columns = ['Revenue', 'Orders', 'Avg_Order', 'Quantity']
    state_revenue = state_revenue.sort_values('Revenue', ascending=False)
    state_revenue['Revenue_Pct'] = (state_revenue['Revenue'] / total_revenue * 100).round(2)
    state_revenue['Cumulative_Pct'] = state_revenue['Revenue_Pct'].cumsum().round(2)
    
    # Product contribution
    product_revenue = df.groupby('Product').agg({
        'Total_Amount': ['sum', 'count'],
        'Qty': 'sum',
        'State': 'nunique'
    }).round(2)
    product_revenue.columns = ['Revenue', 'Orders', 'Quantity', 'States_Presence']
    product_revenue = product_revenue.sort_values('Revenue', ascending=False)
    product_revenue['Revenue_Pct'] = (product_revenue['Revenue'] / total_revenue * 100).round(2)
    product_revenue['Cumulative_Pct'] = product_revenue['Revenue_Pct'].cumsum().round(2)
    
    # TOP SUMMARY CARDS
    st.markdown("### 📊 Market Overview")
    cols = st.columns(4)
    with cols[0]:
        st.metric("🗺️ Total States", len(state_revenue))
    with cols[1]:
        st.metric("🔧 Total Products", len(product_revenue))
    with cols[2]:
        top_state = state_revenue.index[0]
        st.metric("🏆 Top State", top_state, f"{state_revenue.iloc[0]['Revenue_Pct']:.1f}%")
    with cols[3]:
        top_product = product_revenue.index[0]
        st.metric("⭐ Top Product", top_product[:20] + "..." if len(top_product) > 20 else top_product, 
                 f"{product_revenue.iloc[0]['Revenue_Pct']:.1f}%")
    
    st.markdown("---")
    
    # ==========================================
    # STATE-WISE CONTRIBUTION (ENHANCED)
    # ==========================================
    st.markdown("### 🗺️ State-wise Revenue Contribution")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Top 10 States Table with Rankings
        top_states = state_revenue.head(10).copy()
        top_states['Rank'] = range(1, len(top_states) + 1)
        
        # Format for display
        display_states = pd.DataFrame({
            'Rank': top_states['Rank'],
            'State': top_states.index,
            'Revenue': top_states['Revenue'].apply(lambda x: f"{CURRENCY}{x:,.0f}"),
            'Market Share': top_states['Revenue_Pct'].apply(lambda x: f"{x:.2f}%"),
            'Orders': top_states['Orders'].astype(int),
            'Avg Order': top_states['Avg_Order'].apply(lambda x: f"{CURRENCY}{x:,.0f}"),
            'Cumulative %': top_states['Cumulative_Pct'].apply(lambda x: f"{x:.1f}%")
        })
        
        st.table(display_states.set_index('Rank'))
        
        # State tier classification
        st.markdown("#### 🏅 State Performance Tiers")
        tier_cols = st.columns(3)
        
        # Classify states
        star_states = state_revenue[state_revenue['Revenue_Pct'] >= 10]  # >10% share
        growth_states = state_revenue[(state_revenue['Revenue_Pct'] >= 5) & (state_revenue['Revenue_Pct'] < 10)]
        emerging_states = state_revenue[state_revenue['Revenue_Pct'] < 5]
        
        with tier_cols[0]:
            st.markdown(f"**⭐ Star States (≥10%)**\n\n{len(star_states)} states")
            for state in star_states.head(3).index:
                st.write(f"• {state}")
        
        with tier_cols[1]:
            st.markdown(f"**📈 Growth States (5-10%)**\n\n{len(growth_states)} states")
            for state in growth_states.head(3).index:
                st.write(f"• {state}")
        
        with tier_cols[2]:
            st.markdown(f"**🌱 Emerging (<5%)**\n\n{len(emerging_states)} states")
            st.write(f"Total: {len(emerging_states)} states")
    
    with col2:
        # Enhanced Pie Chart with details
        st.markdown("#### Revenue Distribution")
        
        # Show top 8 + others
        top_8_states = state_revenue.head(8)
        others_revenue = state_revenue.iloc[8:]['Revenue'].sum()
        
        pie_data = pd.DataFrame({
            'State': list(top_8_states.index) + ['Others'],
            'Revenue': list(top_8_states['Revenue']) + [others_revenue]
        })
        
        fig = px.pie(pie_data, values='Revenue', names='State', hole=0.5,
                    color_discrete_sequence=px.colors.sequential.Blues_r)
        fig.update_traces(textinfo='percent+label', textposition='outside', 
                         textfont_size=11, pull=[0.05 if i == 0 else 0 for i in range(len(pie_data))])
        fig.update_layout(height=500, showlegend=False,
                         annotations=[dict(text=f'Top 8<br>States', x=0.5, y=0.5, font_size=14, showarrow=False)])
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # ==========================================
    # PRODUCT-WISE CONTRIBUTION (NUMERIC FOCUS)
    # ==========================================
    st.markdown("### 🔧 Product Revenue Contribution")
    
    # Filters
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        show_top_n = st.slider("Show Top N Products:", 5, 30, 10)
    with col_f2:
        min_revenue_prod = st.number_input("Min Revenue:", value=0, step=100000)
    
    filtered_products = product_revenue[product_revenue['Revenue'] >= min_revenue_prod].head(show_top_n)
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.markdown(f"#### Top {show_top_n} Products Ranking")
        
        # Detailed product table
        prod_display = pd.DataFrame({
            'Rank': range(1, len(filtered_products) + 1),
            'Product': filtered_products.index,
            'Revenue': filtered_products['Revenue'].apply(lambda x: f"{CURRENCY}{x:,.0f}"),
            'Market Share': filtered_products['Revenue_Pct'].apply(lambda x: f"{x:.2f}%"),
            'Orders': filtered_products['Orders'].astype(int),
            'States': filtered_products['States_Presence'].astype(int)
        })
        
        st.table(prod_display.set_index('Rank'))
        
        # Product market share summary
        total_prod_share = filtered_products['Revenue_Pct'].sum()
        st.info(f"**Top {show_top_n} products contribute {total_prod_share:.1f}% of total revenue**")
    
    with col2:
        st.markdown("#### Product Performance Metrics")
        
        # Horizontal bar chart with numbers
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=filtered_products.index[::-1],
            x=filtered_products['Revenue'][::-1],
            orientation='h',
            marker=dict(
                color=filtered_products['Revenue_Pct'][::-1],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Market Share %")
            ),
            text=filtered_products.apply(
                lambda x: f"{CURRENCY}{x['Revenue']/100000:.1f}L ({x['Revenue_Pct']:.1f}%)", 
                axis=1
            )[::-1],
            textposition='outside',
            textfont=dict(size=10)
        ))
        
        fig.update_layout(
            height=500,
            xaxis_title=f"Revenue ({CURRENCY})",
            yaxis=dict(autorange="reversed"),
            margin=dict(l=150, r=100, t=30, b=30)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Product concentration analysis
    st.markdown("#### 📊 Product Concentration Analysis")
    
    # Calculate how many products make up 80% of revenue
    product_revenue_sorted = product_revenue.sort_values('Revenue', ascending=False)
    product_revenue_sorted['Cumulative_Revenue'] = product_revenue_sorted['Revenue'].cumsum()
    product_revenue_sorted['Cumulative_Pct'] = (product_revenue_sorted['Cumulative_Revenue'] / total_revenue * 100)
    
    # Find Pareto point (80%)
    pareto_80_idx = product_revenue_sorted[product_revenue_sorted['Cumulative_Pct'] <= 80].index
    pareto_90_idx = product_revenue_sorted[product_revenue_sorted['Cumulative_Pct'] <= 90].index
    
    cols = st.columns(4)
    with cols[0]:
        st.metric("🎯 Top 20% Products", f"{int(len(product_revenue) * 0.2)}", 
                 f"{(product_revenue_sorted.head(int(len(product_revenue) * 0.2))['Revenue_Pct'].sum()):.1f}% revenue")
    with cols[1]:
        st.metric("⭐ 80% Revenue Covered By", f"{len(pareto_80_idx)} products", 
                 f"{len(pareto_80_idx)/len(product_revenue)*100:.1f}% of catalog")
    with cols[2]:
        st.metric("💎 90% Revenue Covered By", f"{len(pareto_90_idx)} products")
    with cols[3]:
        st.metric("📦 Long Tail Products", f"{len(product_revenue) - len(pareto_80_idx)}", 
                 f"{(product_revenue_sorted.tail(len(product_revenue) - len(pareto_80_idx))['Revenue_Pct'].sum()):.1f}% revenue")

# ==========================================
# REPORT 10: PRODUCT PERFORMANCE (NUMERIC FOCUS)
# ==========================================
elif report == "🔧 Product Performance":
    st.markdown("## 🔧 Product Performance Analytics")
    
    # Calculate comprehensive metrics
    product_stats = df.groupby('Product').agg({
        'Total_Amount': ['sum', 'mean', 'count', 'std'],
        'Qty': ['sum', 'mean'],
        'Company': 'nunique',
        'State': 'nunique'
    }).round(2)
    
    product_stats.columns = [
        'Total_Revenue', 'Avg_Order_Value', 'Total_Orders', 'Revenue_StdDev',
        'Total_Qty', 'Avg_Qty_Per_Order', 'Unique_Customers', 'States_Present'
    ]
    
    # Calculate additional metrics
    total_market_revenue = product_stats['Total_Revenue'].sum()
    product_stats['Market_Share_Pct'] = (product_stats['Total_Revenue'] / total_market_revenue * 100).round(2)
    product_stats['Revenue_Per_Customer'] = (product_stats['Total_Revenue'] / product_stats['Unique_Customers']).round(2)
    
    # Sort by revenue
    product_stats = product_stats.sort_values('Total_Revenue', ascending=False)
    
    # TOP SUMMARY CARDS
    st.markdown("### 📊 Market Overview")
    cols = st.columns(5)
    with cols[0]:
        st.metric("Total Products", len(product_stats))
    with cols[1]:
        st.metric("Top Product", product_stats.index[0], f"{CURRENCY}{product_stats.iloc[0]['Total_Revenue']:,.0f}")
    with cols[2]:
        st.metric("Market Leader Share", f"{product_stats.iloc[0]['Market_Share_Pct']:.1f}%")
    with cols[3]:
        st.metric("Avg Order Value", f"{CURRENCY}{product_stats['Avg_Order_Value'].mean():,.0f}")
    with cols[4]:
        st.metric("Total Units Sold", f"{product_stats['Total_Qty'].sum():,.0f}")
    
    st.markdown("---")
    
    # TOP 10 RANKING TABLE (Main View)
    st.markdown("### 🏆 Top 10 Products - Detailed Ranking")
    
    top_10 = product_stats.head(10).copy()
    top_10['Rank'] = range(1, 11)
    top_10['Total_Revenue_Fmt'] = top_10['Total_Revenue'].apply(lambda x: f"{CURRENCY}{x:,.0f}")
    top_10['Avg_Order_Fmt'] = top_10['Avg_Order_Value'].apply(lambda x: f"{CURRENCY}{x:,.0f}")
    top_10['Market_Share_Fmt'] = top_10['Market_Share_Pct'].apply(lambda x: f"{x:.1f}%")
    
    # Reorder columns for display
    display_cols = [
        'Rank', 'Total_Revenue_Fmt', 'Market_Share_Fmt', 'Total_Orders', 
        'Total_Qty', 'Avg_Order_Fmt', 'Unique_Customers', 'States_Present'
    ]
    
    st.table(top_10[display_cols].rename(columns={
        'Total_Revenue_Fmt': 'Revenue',
        'Market_Share_Fmt': 'Market Share',
        'Total_Orders': 'Orders',
        'Total_Qty': 'Units',
        'Avg_Order_Fmt': 'Avg Order',
        'Unique_Customers': 'Customers',
        'States_Present': 'States'
    }))
    
    st.markdown("---")
    
    # COMPARISON SECTION - Select products to compare
    st.markdown("### 🔍 Product Comparison Tool")
    
    col1, col2 = st.columns(2)
    with col1:
        prod1 = st.selectbox("Select Product 1:", product_stats.index, index=0)
    with col2:
        prod2 = st.selectbox("Select Product 2:", product_stats.index, index=1 if len(product_stats) > 1 else 0)
    
    if prod1 and prod2:
        p1_data = product_stats.loc[prod1]
        p2_data = product_stats.loc[prod2]
        
        comparison_df = pd.DataFrame({
            'Metric': ['Revenue', 'Market Share %', 'Orders', 'Units Sold', 'Avg Order Value', 'Customers', 'States'],
            prod1: [
                f"{CURRENCY}{p1_data['Total_Revenue']:,.0f}",
                f"{p1_data['Market_Share_Pct']:.2f}%",
                f"{int(p1_data['Total_Orders'])}",
                f"{int(p1_data['Total_Qty'])}",
                f"{CURRENCY}{p1_data['Avg_Order_Value']:,.0f}",
                f"{int(p1_data['Unique_Customers'])}",
                f"{int(p1_data['States_Present'])}"
            ],
            prod2: [
                f"{CURRENCY}{p2_data['Total_Revenue']:,.0f}",
                f"{p2_data['Market_Share_Pct']:.2f}%",
                f"{int(p2_data['Total_Orders'])}",
                f"{int(p2_data['Total_Qty'])}",
                f"{CURRENCY}{p2_data['Avg_Order_Value']:,.0f}",
                f"{int(p2_data['Unique_Customers'])}",
                f"{int(p2_data['States_Present'])}"
            ],
            'Difference': [
                f"{CURRENCY}{p1_data['Total_Revenue'] - p2_data['Total_Revenue']:,.0f}",
                f"{p1_data['Market_Share_Pct'] - p2_data['Market_Share_Pct']:.2f}%",
                f"{int(p1_data['Total_Orders'] - p2_data['Total_Orders'])}",
                f"{int(p1_data['Total_Qty'] - p2_data['Total_Qty'])}",
                f"{CURRENCY}{p1_data['Avg_Order_Value'] - p2_data['Avg_Order_Value']:,.0f}",
                f"{int(p1_data['Unique_Customers'] - p2_data['Unique_Customers'])}",
                f"{int(p1_data['States_Present'] - p2_data['States_Present'])}"
            ]
        })
        
        st.table(comparison_df.set_index('Metric'))
    
    st.markdown("---")
    
    # ONLY 1 CHART - Top 10 Revenue (Horizontal Bar for quick visual reference)
    st.markdown("### 📊 Quick Visual Reference (Top 10)")
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=top_10.index[::-1],
        x=top_10['Total_Revenue'][::-1],
        orientation='h',
        marker_color='royalblue',
        text=top_10['Total_Revenue'][::-1].apply(lambda x: f'{x/100000:.1f}L'),
        textposition='outside'
    ))
    fig.update_layout(
        height=400,
        xaxis_title=f"Revenue ({CURRENCY})",
        showlegend=False,
        margin=dict(l=200, r=50, t=30, b=30)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # FULL DATA TABLE (Expandable)
    with st.expander("📋 View All Products Data"):
        st.dataframe(
            product_stats.style.format({
                'Total_Revenue': lambda x: f"{CURRENCY}{x:,.0f}",
                'Avg_Order_Value': lambda x: f"{CURRENCY}{x:,.0f}",
                'Revenue_Per_Customer': lambda x: f"{CURRENCY}{x:,.0f}",
                'Market_Share_Pct': lambda x: f"{x:.2f}%"
            }),
            use_container_width=True,
            height=500
        )

# ==========================================
# REPORT 11: PRODUCT TRENDS
# ==========================================
elif report == "🔧 Product Trends":
    st.markdown("## 🔧 Product Trends Over Time")
    
    # Select products to compare
    top_products = df.groupby('Product')['Total_Amount'].sum().nlargest(10).index.tolist()
    selected_products = st.multiselect("🔧 Select Products to Compare:", top_products, default=top_products[:5])
    
    if selected_products:
        fig = go.Figure()
        for product in selected_products:
            prod_df = df[df['Product'] == product]
            monthly = prod_df.groupby(prod_df['Date'].dt.to_period('M'))['Total_Amount'].sum()
            monthly.index = monthly.index.to_timestamp()
            fig.add_trace(go.Scatter(x=monthly.index, y=monthly.values, 
                                   mode='lines+markers', name=product))
        
        fig.update_layout(title='Product-wise Monthly Trends', height=500)
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# REPORT 12: BEST SELLERS BY STATE
# ==========================================
elif report == "🔧 Best Sellers by State":
    st.markdown("## 🔧 Best Selling Products by State")
    
    state = st.selectbox("🗺️ Select State:", sorted(df['State'].unique()))
    
    if state:
        state_df = df[df['State'] == state]
        
        col1, col2 = st.columns([2, 1])
        with col1:
            top_products = state_df.groupby('Product')['Total_Amount'].sum().nlargest(15)
            fig = px.bar(top_products, orientation='h', color=top_products.values,
                        color_continuous_scale='Spectral')
            fig.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown(f"### 📋 Top Products in {state}")
            st.dataframe(top_products.reset_index().rename(columns={'Total_Amount': 'Revenue'}),
                        use_container_width=True)

# ==========================================
# REPORT 13: COMPANY ANALYSIS
# ==========================================
elif report == "🏢 Company Analysis":
    st.markdown("## 🏢 Customer/Company Deep Dive")
    
    # Top companies
    top_companies = df.groupby('Company').agg({
        'Total_Amount': ['sum', 'count', 'mean'],
        'Qty': 'sum'
    }).round(2)
    top_companies.columns = ['Total_Revenue', 'Orders', 'Avg_Order', 'Total_Qty']
    top_companies = top_companies.sort_values('Total_Revenue', ascending=False).head(50)
    
    # Filters
    min_orders = st.slider("📊 Minimum Orders:", 1, int(top_companies['Orders'].max()), 1)
    filtered_companies = top_companies[top_companies['Orders'] >= min_orders]
    
    st.dataframe(filtered_companies.style.format({
        'Total_Revenue': lambda x: f"{CURRENCY}{x:,.0f}",
        'Avg_Order': lambda x: f"{CURRENCY}{x:,.0f}"
    }), use_container_width=True)
    
    # Visualization
    fig = px.scatter(filtered_companies.reset_index(), x='Orders', y='Total_Revenue',
                    size='Total_Qty', color='Avg_Order', hover_name='Company',
                    color_continuous_scale='Viridis')
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# REPORT 14: CUSTOMER SEGMENTATION (ENHANCED WITH LISTS)
# ==========================================
elif report == "🏢 Customer Segmentation":
    st.markdown("## 🏢 Customer Segmentation (ABC Analysis)")
    
    # ABC Analysis
    company_revenue = df.groupby('Company')['Total_Amount'].sum().sort_values(ascending=False)
    total_revenue = company_revenue.sum()
    
    company_revenue_pct = company_revenue / total_revenue * 100
    cumulative_pct = company_revenue_pct.cumsum()
    
    # Classify
    def classify_abc(x):
        if x <= 80:
            return 'A (Top 80%)'
        elif x <= 95:
            return 'B (Next 15%)'
        else:
            return 'C (Bottom 5%)'
    
    abc_classification = cumulative_pct.apply(classify_abc)
    
    abc_summary = pd.DataFrame({
        'Revenue': company_revenue,
        'Cumulative_%': cumulative_pct,
        'Segment': abc_classification
    })
    
    # Select Segment to View (NEW FILTER)
    segment_filter = st.selectbox("📊 Select Segment to View:", ["All Segments", "A (Top 80%)", "B (Next 15%)", "C (Bottom 5%)"])
    
    # Filter and display companies
    if segment_filter != "All Segments":
        filtered_segment = abc_summary[abc_summary['Segment'] == segment_filter]
        st.markdown(f"### 📋 Companies in {segment_filter}")
        st.dataframe(filtered_segment.style.format({
            'Revenue': lambda x: f"{CURRENCY}{x:,.0f}",
            'Cumulative_%': lambda x: f"{x:.2f}%"
        }), use_container_width=True, height=400)
        st.info(f"Total {len(filtered_segment)} companies in {segment_filter}")
    else:
        # Show all segments summary
        col1, col2, col3 = st.columns(3)
        segments = ['A (Top 80%)', 'B (Next 15%)', 'C (Bottom 5%)']
        colors = ['#2ecc71', '#f39c12', '#e74c3c']
        
        for col, segment, color in zip([col1, col2, col3], segments, colors):
            with col:
                count = (abc_classification == segment).sum()
                revenue = company_revenue[abc_classification == segment].sum()
                st.markdown(f"<div style='background-color:{color}; padding:20px; border-radius:10px; color:white; text-align:center;'>"
                           f"<h3>{segment}</h3>"
                           f"<h2>{count}</h2><p>Companies</p>"
                           f"<h4>{CURRENCY}{revenue:,.0f}</h4></div>", 
                           unsafe_allow_html=True)
        
        # Show lists for each segment
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🟢 A Segment Companies (Top)")
            a_companies = abc_summary[abc_summary['Segment'] == 'A (Top 80%)'].head(10)
            for idx, (company, row) in enumerate(a_companies.iterrows(), 1):
                st.write(f"{idx}. **{company}** - {CURRENCY}{row['Revenue']:,.0f}")
        
        with col2:
            st.markdown("### 🟡 B Segment Companies")
            b_companies = abc_summary[abc_summary['Segment'] == 'B (Next 15%)'].head(10)
            for idx, (company, row) in enumerate(b_companies.iterrows(), 1):
                st.write(f"{idx}. **{company}** - {CURRENCY}{row['Revenue']:,.0f}")
        
        with col3:
            st.markdown("### 🔴 C Segment Companies")
            c_companies = abc_summary[abc_summary['Segment'] == 'C (Bottom 5%)'].head(10)
            for idx, (company, row) in enumerate(c_companies.iterrows(), 1):
                st.write(f"{idx}. **{company}** - {CURRENCY}{row['Revenue']:,.0f}")

# ==========================================
# REPORT 15: LEAD TIME ANALYSIS (NO CHARTS - NUMBERS ONLY)
# ==========================================
elif report == "⚡ Lead Time Analysis":
    st.markdown("## ⚡ Production & Delivery Lead Time Analysis")
    
    # Calculate lead time stats
    df['Lead_Time_Days'] = (df['EDD'] - df['Date']).dt.days
    
    # Filter valid lead times
    valid_lead = df[(df['Lead_Time_Days'] > 0) & (df['Lead_Time_Days'] < 365)]
    
    if not valid_lead.empty:
        # Overall Statistics (NO CHARTS)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("⏱️ Average Lead Time", f"{valid_lead['Lead_Time_Days'].mean():.1f} days")
        with col2:
            st.metric("⚡ Fastest Delivery", f"{valid_lead['Lead_Time_Days'].min()} days")
        with col3:
            st.metric("🐌 Slowest Delivery", f"{valid_lead['Lead_Time_Days'].max()} days")
        with col4:
            st.metric("📊 Median Lead Time", f"{valid_lead['Lead_Time_Days'].median():.1f} days")
        
        st.markdown("---")
        
        # Lead Time by Product (TABLE ONLY - NO GRAPHS)
        st.markdown("### ⏱️ Lead Time by Product (Numbers Only)")
        lead_by_product = valid_lead.groupby('Product')['Lead_Time_Days'].agg(['mean', 'min', 'max', 'count']).round(1)
        lead_by_product.columns = ['Avg_Days', 'Min_Days', 'Max_Days', 'Order_Count']
        lead_by_product = lead_by_product.sort_values('Avg_Days', ascending=False)
        
        # Add interpretation
        lead_by_product['Interpretation'] = lead_by_product['Avg_Days'].apply(
            lambda x: '🔴 Long Time' if x > 30 else ('🟡 Medium' if x > 15 else '🟢 Fast')
        )
        
        st.dataframe(lead_by_product, use_container_width=True)
        
        # Products that take MORE TIME (Text Analysis)
        st.markdown("---")
        st.markdown("### 🐌 Products with Longest Lead Time")
        slow_products = lead_by_product.head(5)
        for idx, (product, row) in enumerate(slow_products.iterrows(), 1):
            st.write(f"{idx}. **{product}** - Avg: **{row['Avg_Days']:.1f} days** "
                    f"(Range: {row['Min_Days']:.0f} to {row['Max_Days']:.0f} days)")
        
        st.markdown("### ⚡ Products with Fastest Delivery")
        fast_products = lead_by_product.tail(5)
        for idx, (product, row) in enumerate(fast_products.iterrows(), 1):
            st.write(f"{idx}. **{product}** - Avg: **{row['Avg_Days']:.1f} days**")
    else:
        st.warning("No valid lead time data available (check EDD dates format in your sheet)")

# ==========================================
# REPORT: RAW DATA EXPLORER  
# ==========================================
elif report == "📋 Raw Data Explorer":
    st.markdown("## 📋 Interactive Data Explorer")
    
    # Advanced filters
    with st.expander("🔍 Advanced Filters", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            f_states = st.multiselect("States:", df['State'].unique(), default=[])
        with col2:
            f_products = st.multiselect("Products:", df['Product'].unique(), default=[])
        with col3:
            date_range = st.date_input("Date Range:", [df['Date'].min(), df['Date'].max()])
    
    # Apply filters
    filtered = df.copy()
    if f_states:
        filtered = filtered[filtered['State'].isin(f_states)]
    if f_products:
        filtered = filtered[filtered['Product'].isin(f_products)]
    if len(date_range) == 2:
        filtered = filtered[(filtered['Date'] >= pd.Timestamp(date_range[0])) & 
                           (filtered['Date'] <= pd.Timestamp(date_range[1]))]
    
    # Show the data table
    st.dataframe(filtered, use_container_width=True, height=600)

# Global Footer
st.sidebar.markdown("---")
st.sidebar.caption(f"🔄 Auto-refresh: 5 min | 📊 Records: {len(df):,}")