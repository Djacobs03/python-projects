import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Page config
st.set_page_config(
    page_title="Global University Cost Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and Introduction
st.title("🌍 Global University Cost Dashboard")
st.markdown("""
Welcome to the **Global University Cost Dashboard** 🌍🎓

This dashboard provides a comprehensive comparative view of university expenses including tuition fees, living costs, and additional fees across different countries and academic programs. 

**Key Features:**
- 📊 Compare costs across multiple universities worldwide
- 💰 View expenses in both USD and INR currencies
- 🏛️ Analyze cost breakdowns by components
- 🔍 Filter by country, university, program, and level
- 📈 Interactive visualizations and metrics

**How to use:** Use the sidebar filters to explore costs for your desired country, university, and program. The dashboard will automatically update all charts and metrics based on your selections.

---
""")

@st.cache_data
def load_data():
    """Load data from bundled CSV file - Deployment Ready"""
    try:
        # Load the bundled CSV file
        df = pd.read_csv('International_Education_Costs.csv')
        st.sidebar.success("✅ Data loaded successfully!")
        
        # Display basic info 
        st.sidebar.info(f"📊 Loaded {len(df)} records from {len(df['Country'].unique())} countries")
        
        return df
    except FileNotFoundError:
        st.sidebar.error("❌ Data file 'International_Education_Costs.csv' not found!")
        st.error("""
        **Data File Missing!** 
        
        Please ensure 'International_Education_Costs.csv' is in the same folder as this app.
        
        **For deployment:** Include the CSV file in your GitHub repository.
        """)
        st.stop()
    except Exception as e:
        st.sidebar.error(f"❌ Error loading data: {str(e)}")
        st.error(f"Error loading data: {str(e)}")
        st.stop()

# Load data
df = load_data()

# IMPROVED DATA CLEANING - PRESERVES ALL LEGITIMATE ENTRIES
def clean_data(df):
    """Clean the dataset while preserving all legitimate program entries"""
    # Clean whitespace from string columns
    string_columns = df.select_dtypes(include=['object']).columns
    for col in string_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    
    # Only remove completely identical rows (all columns identical)
    before_cleaning = len(df)
    df = df.drop_duplicates()
    after_cleaning = len(df)
    
    if before_cleaning != after_cleaning:
        st.sidebar.info(f"ℹ️ Removed {before_cleaning - after_cleaning} completely duplicate rows")
    
    # Check for potential level/degree column variations
    potential_level_cols = ['Level', 'Degree', 'Degree_Level', 'Program_Level', 'Study_Level']
    level_col = None
    for col in potential_level_cols:
        if col in df.columns:
            level_col = col
            break
    
    if level_col:
        st.sidebar.success(f"✅ Found degree level column: {level_col}")
    else:
        st.sidebar.warning("⚠️ No degree level column found. Looking for patterns in Program names...")
        # Try to extract level from program names
        if 'Program' in df.columns:
            df['Level'] = df['Program'].str.extract(r'(Bachelor|Master|PhD|Doctorate|Graduate|Undergraduate)', case=False)
            if df['Level'].notna().any():
                st.sidebar.info("ℹ️ Extracted degree levels from Program names")
            else:
                df['Level'] = 'Not Specified'
                st.sidebar.info("ℹ️ Created default Level column")
    
    return df

# Clean the data
df = clean_data(df)

# Validate COLUMNS
required_columns = ['Country', 'University', 'Tuition_USD', 'Rent_USD', 'Visa_Fee_USD', 'Insurance_USD']
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error(f"❌ Missing required columns in your CSV: {missing_columns}")
    st.error("Please ensure your CSV file has all required columns.")
    st.stop()

# Display dataset info with enhanced details
with st.expander("📋 Dataset Information", expanded=False):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Records", len(df))
    with col2:
        st.metric("Unique Universities", len(df["University"].unique()))
    with col3:
        st.metric("Countries Covered", len(df["Country"].unique()))
    with col4:
        if "Program" in df.columns:
            st.metric("Unique Programs", len(df["Program"].unique()))
        else:
            st.metric("Programs", "N/A")
    
    # Show column information
    st.write("**Available Columns:**")
    cols_info = []
    for col in df.columns:
        non_null_count = df[col].notna().sum()
        cols_info.append(f"• {col}: {non_null_count}/{len(df)} records")
    st.write("\n".join(cols_info))
    
    st.write("**Sample Data:**")
    st.dataframe(df.head(3))

# Exchange rate with fallback
@st.cache_data(ttl=3600)
def fetch_exchange_rate():
    """Fetch USD to INR exchange rate with fallback"""
    try:
        response = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'rates' in data and 'INR' in data['rates']:
                rate = data['rates']['INR']
                st.sidebar.success(f"✅ Live exchange rate: 1 USD = {rate:.2f} INR")
                return rate
    except:
        pass
    
    # Fallback rate
    fallback_rate = 83.5
    st.sidebar.warning(f"⚠️ Using fallback exchange rate: 1 USD = {fallback_rate} INR")
    return fallback_rate

exchange_rate = fetch_exchange_rate()

# Calculate INR values
for col in ["Tuition_USD", "Rent_USD", "Visa_Fee_USD", "Insurance_USD"]:
    if col in df.columns:
        inr_col = col.replace("USD", "INR")
        df[inr_col] = df[col] * exchange_rate

# Calculate total costs
df['Total_Cost_USD'] = df['Tuition_USD'] + df['Rent_USD'] + df['Visa_Fee_USD'] + df['Insurance_USD']
df['Total_Cost_INR'] = df['Total_Cost_USD'] * exchange_rate

# ENHANCED SIDEBAR FILTERS
st.sidebar.header("🎓 Filter Options")
st.sidebar.markdown("Select your preferences to customize the dashboard:")

# Country Filter
countries = sorted(df["Country"].unique())
selected_country = st.sidebar.selectbox(
    "🌍 Select Country", 
    countries,
    help="Choose a country to filter universities"
)

# University Filter
colleges = sorted(df[df["Country"] == selected_country]["University"].unique())
selected_college = st.sidebar.selectbox(
    "🏛️ Select University", 
    colleges,
    help="Choose a university from the selected country"
)

# Program Filter 
programs_filter_data = df[df["University"] == selected_college]
if "Program" in df.columns and not programs_filter_data.empty:
    programs_available = programs_filter_data["Program"].unique()
    if len(programs_available) > 0:
        programs = sorted(programs_available)
        selected_program = st.sidebar.selectbox(
            "📚 Select Program", 
            programs,
            help="Choose an academic program"
        )
        programs_filter_data = programs_filter_data[programs_filter_data["Program"] == selected_program]
    else:
        selected_program = None
else:
    selected_program = None

# Level Filter (if available)
if "Level" in df.columns and not programs_filter_data.empty:
    levels_available = programs_filter_data["Level"].unique()
    levels_available = [level for level in levels_available if pd.notna(level) and level != 'Not Specified']
    if len(levels_available) > 1:
        selected_level = st.sidebar.selectbox(
            "🎓 Select Level", 
            ['All Levels'] + sorted(levels_available),
            help="Choose a degree level"
        )
        if selected_level != 'All Levels':
            programs_filter_data = programs_filter_data[programs_filter_data["Level"] == selected_level]
    elif len(levels_available) == 1:
        selected_level = levels_available[0]
        st.sidebar.info(f"Level: {selected_level}")
    else:
        selected_level = None
else:
    selected_level = None

# Final filtered data
df_filtered = programs_filter_data.copy()

# Check if filtered data exists
if df_filtered.empty:
    st.error("❌ No data found for the selected filters. Please try different selections.")
    st.stop()

# Show multiple entries if they exist
if len(df_filtered) > 1:
    st.sidebar.warning(f"⚠️ Multiple entries found ({len(df_filtered)}). Showing first entry in metrics, all entries in comparison.")
    selected_row = df_filtered.iloc[0]
else:
    selected_row = df_filtered.iloc[0]

# Exchange rate info in sidebar
st.sidebar.markdown("---")
st.sidebar.info(f"💱 Current Exchange Rate: 1 USD = {exchange_rate:.2f} INR")

# Main Dashboard Content
st.markdown("---")

# Key Metrics Section
st.subheader("🎯 Key Financial Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if "Living_Cost_Index" in selected_row and pd.notna(selected_row['Living_Cost_Index']):
        st.metric(
            "Living Cost Index", 
            f"{selected_row['Living_Cost_Index']:.1f}",
            help="Cost of living index compared to global average"
        )
    else:
        st.metric("Living Cost Index", "N/A")

with col2:
    st.metric(
        "Tuition (USD)", 
        f"${selected_row['Tuition_USD']:,.2f}",
        help="Annual tuition fee in US Dollars"
    )

with col3:
    st.metric(
        "Tuition (INR)", 
        f"₹{selected_row['Tuition_INR']:,.0f}",
        help="Annual tuition fee in Indian Rupees"
    )

with col4:
    st.metric(
        "Total Cost (USD)", 
        f"${selected_row['Total_Cost_USD']:,.2f}",
        help="Total annual cost including all components"
    )

# Cost Breakdown Section
st.subheader("💰 Cost Breakdown Analysis")

col1, col2 = st.columns([1, 1])

with col1:
    # Pie Chart
    breakdown = {
        "Tuition": selected_row["Tuition_INR"],
        "Rent": selected_row["Rent_INR"],
        "Visa Fee": selected_row["Visa_Fee_INR"],
        "Insurance": selected_row["Insurance_INR"]
    }
    
    # Filter out zero values
    breakdown = {k: v for k, v in breakdown.items() if v > 0}
    
    fig_pie = px.pie(
        names=list(breakdown.keys()),
        values=list(breakdown.values()),
        title=f"Cost Distribution for {selected_college}",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_pie.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Percentage: %{percent}<br>Amount: ₹%{value:,.0f}<extra></extra>'
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    # Bar chart
    stack_data = pd.DataFrame({
        "Component": list(breakdown.keys()),
        "Cost (INR)": list(breakdown.values())
    })
    
    fig_bar = px.bar(
        stack_data,
        x="Component",
        y="Cost (INR)",
        title=f"Cost Components - {selected_college}",
        color="Component",
        text="Cost (INR)",
        color_discrete_sequence=px.colors.sequential.Blues_r
    )
    fig_bar.update_traces(texttemplate='₹%{text:,.0f}', textposition='outside')
    fig_bar.update_layout(showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

# ENHANCED UNIVERSITY COMPARISON SECTION
st.subheader("🏛️ Enhanced University Comparison")

# University selector for comparison
all_universities = sorted(df["University"].unique())
comparison_unis = st.multiselect(
    "🔍 Select Universities for Comparison (2-3 recommended)",
    options=all_universities,
    default=[selected_college] if selected_college in all_universities else [all_universities[0]],
    help="Select multiple universities to compare their costs and programs"
)

if comparison_unis:
    # Get data for selected universities
    comparison_data = df[df["University"].isin(comparison_unis)].copy()
    
    if not comparison_data.empty:
        # Enhanced comparison options
        st.markdown("### 📊 Comparison Options")
        col1, col2 = st.columns(2)
        
        with col1:
            comparison_mode = st.radio(
                "Choose Comparison View:",
                options=["University Overview", "All Programs & Levels", "Program Comparison"],
                help="University Overview: One entry per university | All Programs: Every program entry | Program Comparison: Same program across universities"
            )
        
        with col2:
            show_inr = st.checkbox("Show INR columns", value=True, help="Toggle INR currency columns")
        
        # Process data based on comparison mode
        if comparison_mode == "University Overview":
            # Show aggregated data per university
            agg_funcs = {col: 'mean' for col in ['Tuition_USD', 'Rent_USD', 'Visa_Fee_USD', 'Insurance_USD', 'Total_Cost_USD'] if col in comparison_data.columns}
            display_data = comparison_data.groupby(['University', 'Country'], as_index=False).agg(agg_funcs)
            
            # Add program count
            program_counts = comparison_data.groupby('University').size()
            display_data['Total_Programs'] = display_data['University'].map(program_counts)
            
            # Add INR columns
            if show_inr:
                for col in ['Tuition_USD', 'Rent_USD', 'Visa_Fee_USD', 'Insurance_USD', 'Total_Cost_USD']:
                    if col in display_data.columns:
                        inr_col = col.replace('USD', 'INR')
                        display_data[inr_col] = display_data[col] * exchange_rate
            
            st.info("📋 Showing averaged costs across all programs for each university")
            
        elif comparison_mode == "All Programs & Levels":
            # Show all entries with enhanced columns
            display_data = comparison_data.copy()
            st.info(f"📋 Showing all {len(display_data)} program entries")
            
        else:  # Program Comparison
            # Filter by program if available
            if 'Program' in comparison_data.columns:
                available_programs = comparison_data['Program'].unique()
                if len(available_programs) > 1:
                    compare_program = st.selectbox(
                        "📚 Select Program to Compare Across Universities:",
                        sorted(available_programs),
                        help="Choose a program that exists in multiple universities"
                    )
                    display_data = comparison_data[comparison_data['Program'] == compare_program].copy()
                    if display_data.empty:
                        st.warning(f"No data found for program: {compare_program}")
                        display_data = comparison_data.copy()
                else:
                    display_data = comparison_data.copy()
            else:
                display_data = comparison_data.copy()
        
        # Define display columns based on available data
        base_columns = ["University", "Country"]
        
        # Add Program and Level columns if available
        if 'Program' in display_data.columns and comparison_mode != "University Overview":
            base_columns.append("Program")
        if 'Level' in display_data.columns and comparison_mode != "University Overview":
            base_columns.append("Level")
        
        # Add cost columns
        cost_columns_usd = ["Tuition_USD", "Rent_USD", "Visa_Fee_USD", "Insurance_USD", "Total_Cost_USD"]
        cost_columns_inr = ["Tuition_INR", "Rent_INR", "Visa_Fee_INR", "Insurance_INR", "Total_Cost_INR"]
        
        if show_inr:
            display_columns = base_columns + cost_columns_usd + cost_columns_inr
        else:
            display_columns = base_columns + cost_columns_usd
        
        # Add Total_Programs for overview mode
        if comparison_mode == "University Overview" and 'Total_Programs' in display_data.columns:
            display_columns.insert(-len(cost_columns_usd) - (len(cost_columns_inr) if show_inr else 0), 'Total_Programs')
        
        # Filter to existing columns
        display_columns = [col for col in display_columns if col in display_data.columns]
        
        # Sort the data
        if 'Program' in display_data.columns and 'Level' in display_data.columns:
            display_data = display_data.sort_values(['University', 'Program', 'Level'])
        elif 'Program' in display_data.columns:
            display_data = display_data.sort_values(['University', 'Program'])
        else:
            display_data = display_data.sort_values(['University'])
        
        # ENHANCED DATA TABLE
        st.subheader(f"📊 {comparison_mode} - Enhanced Data Table")
        
        # Create enhanced column config
        column_config = {
            "University": st.column_config.TextColumn("🏛️ University", width="large"),
            "Country": st.column_config.TextColumn("🌍 Country", width="small"),
            "Program": st.column_config.TextColumn("📚 Program", width="medium"),
            "Level": st.column_config.TextColumn("🎓 Level", width="small"),
            "Total_Programs": st.column_config.NumberColumn("📊 Total Programs", format="%d"),
            "Tuition_USD": st.column_config.NumberColumn("💰 Tuition (USD)", format="$%,.0f"),
            "Rent_USD": st.column_config.NumberColumn("🏠 Rent (USD)", format="$%,.0f"),
            "Visa_Fee_USD": st.column_config.NumberColumn("📄 Visa (USD)", format="$%,.0f"),
            "Insurance_USD": st.column_config.NumberColumn("🏥 Insurance (USD)", format="$%,.0f"),
            "Total_Cost_USD": st.column_config.NumberColumn("💵 Total (USD)", format="$%,.0f"),
            "Tuition_INR": st.column_config.NumberColumn("💰 Tuition (INR)", format="₹%,.0f"),
            "Rent_INR": st.column_config.NumberColumn("🏠 Rent (INR)", format="₹%,.0f"),
            "Visa_Fee_INR": st.column_config.NumberColumn("📄 Visa (INR)", format="₹%,.0f"),
            "Insurance_INR": st.column_config.NumberColumn("🏥 Insurance (INR)", format="₹%,.0f"),
            "Total_Cost_INR": st.column_config.NumberColumn("💵 Total (INR)", format="₹%,.0f"),
        }
        
        # Display the enhanced table
        st.dataframe(
            display_data[display_columns], 
            use_container_width=True,
            hide_index=True,
            column_config=column_config,
            height=400
        )
        
        # Enhanced summary information
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Entries", len(display_data))
        with col2:
            st.metric("🏛️ Universities", len(display_data['University'].unique()))
        with col3:
            if 'Program' in display_data.columns:
                st.metric("📚 Programs", len(display_data['Program'].unique()))
            else:
                st.metric("Programs", "N/A")
        with col4:
            if 'Level' in display_data.columns:
                st.metric("🎓 Levels", len(display_data['Level'].unique()))
            else:
                st.metric("Levels", "N/A")
        
        # ENHANCED VISUALIZATION
        st.subheader("📊 University Cost Comparison Chart")
        
        # Create chart data (always aggregated for clean visualization)
        chart_data = comparison_data.groupby(['University', 'Country'], as_index=False).agg({
            col: 'mean' for col in ['Tuition_INR', 'Rent_INR', 'Visa_Fee_INR', 'Insurance_INR'] 
            if col in comparison_data.columns
        }).round(0)
        
        # Chart options
        chart_type = st.radio(
            "Chart Type:",
            options=["Stacked Bar", "Grouped Bar", "Total Cost Only"],
            horizontal=True
        )
        
        required_inr_cols = ["Tuition_INR", "Rent_INR", "Visa_Fee_INR", "Insurance_INR"]
        available_inr_cols = [col for col in required_inr_cols if col in chart_data.columns]
        
        if available_inr_cols:
            if chart_type == "Total Cost Only":
                # Simple total cost comparison
                fig_comparison = px.bar(
                    chart_data,
                    x="University",
                    y="Total_Cost_INR" if "Total_Cost_INR" in chart_data.columns else chart_data[available_inr_cols].sum(axis=1),
                    title="Total University Cost Comparison",
                    color="University",
                    height=500,
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
                fig_comparison.update_layout(showlegend=False)
            else:
                # Component breakdown
                df_melted = chart_data.melt(
                    id_vars=["University", "Country"], 
                    value_vars=available_inr_cols, 
                    var_name="Cost Component", 
                    value_name="Amount (INR)"
                )
                
                df_melted["Cost Component"] = df_melted["Cost Component"].str.replace("_INR", "").str.replace("_", " ").str.title()
                
                barmode = "stack" if chart_type == "Stacked Bar" else "group"
                
                fig_comparison = px.bar(
                    df_melted,
                    x="University",
                    y="Amount (INR)",
                    color="Cost Component",
                    title=f"University Cost Comparison - {chart_type}",
                    barmode=barmode,
                    height=500,
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
            
            fig_comparison.update_layout(
                xaxis_tickangle=-45,
                xaxis_title="University",
                yaxis_title="Cost (INR)",
                legend_title="Cost Components"
            )
            st.plotly_chart(fig_comparison, use_container_width=True)
        else:
            st.warning("No cost data available for chart visualization.")
    
    else:
        st.error("No data available for selected universities.")
else:
    st.info("Select universities above to see detailed comparison.")

# Additional Analytics
st.subheader("📈 Additional Insights")

col1, col2 = st.columns(2)

with col1:
    # Top 5 most expensive universities
    if len(df) >= 5:
        df_unique = df.groupby(['University', 'Country'])['Total_Cost_USD'].max().reset_index()
        top_expensive = df_unique.nlargest(5, 'Total_Cost_USD')
        
        st.write("**Top 5 Most Expensive Universities:**")
        for idx, row in top_expensive.iterrows():
            st.write(f"• {row['University']} ({row['Country']}) - ${row['Total_Cost_USD']:,.0f}")

with col2:
    # Country-wise average costs
    if len(df['Country'].unique()) > 1:
        country_avg = df.groupby('Country')['Total_Cost_USD'].mean().sort_values(ascending=False)
        st.write("**Average Cost by Country:**")
        for country, cost in country_avg.head(5).items():
            st.write(f"• {country}: ${cost:,.0f}")

# Data Quality Report
with st.expander("🔍 Data Quality Report", expanded=False):
    st.subheader("Data Completeness Analysis")
    
    # Check for missing values
    missing_data = df.isnull().sum()
    if missing_data.sum() > 0:
        st.write("**Missing Values by Column:**")
        for col, missing_count in missing_data[missing_data > 0].items():
            percentage = (missing_count / len(df)) * 100
            st.write(f"• {col}: {missing_count} ({percentage:.1f}%)")
    else:
        st.success("✅ No missing values found in the dataset!")
    
    # Check for duplicate entries
    if 'Program' in df.columns and 'Level' in df.columns:
        duplicate_key = ['University', 'Program', 'Level']
    elif 'Program' in df.columns:
        duplicate_key = ['University', 'Program']
    else:
        duplicate_key = ['University']
    
    duplicates = df.duplicated(subset=duplicate_key).sum()
    if duplicates > 0:
        st.warning(f"⚠️ Found {duplicates} potential duplicate entries based on {', '.join(duplicate_key)}")
    else:
        st.success("✅ No duplicate entries found!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🌍 Global University Cost Dashboard | Built with Streamlit & Plotly</p>
    <p>💡 Data is for informational purposes only. Please verify with official university sources.</p>
    
</div>
""", unsafe_allow_html=True)