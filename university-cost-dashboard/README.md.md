# 🌍 Global University Cost Dashboard

A comprehensive dashboard for comparing university costs worldwide.

## Features
- Compare costs across multiple universities
- View expenses in USD and INR
- Interactive visualizations
- Cost breakdown analysis  

## 📊 Acknowledgements and Methodology

### ⚠️ Data Limitations
While this dashboard offers some insights, please note that:
- The underlying data is not exhaustive.
- Some universities or programs may be missing.
- Costs may vary significantly based on real-time fees, scholarships, or living standards.

> **"You might not even find your university — and that’s okay."**

### 🏆 Ranking Criteria Used
**"Top 5 Most Expensive Universities"** are ranked by **Total Annual Cost (USD)** calculated as:

| Component        | Description                        | Example    |
|------------------|------------------------------------|------------|
| Tuition Fee      | Annual academic fees               | $45,000    |
| Rent             | Annual housing costs               | $12,000    |
| Visa Fee         | Student visa application fee       | $500       |
| Insurance        | Health insurance (annual)          | $2,000     |
| **Total Cost**   | Sum of all components              | $59,500    |

Python logic:
```python
# Step 1: Calculate total cost for each university
df['Total_Cost_USD'] = df['Tuition_USD'] + df['Rent_USD'] + df['Visa_Fee_USD'] + df['Insurance_USD']

# Step 2: Get top 5 most expensive
top_expensive = df.nlargest(5, 'Total_Cost_USD')

# Step 3: Display results
for _, university in top_expensive.iterrows():
    print(f"{university['University']} ({university['Country']}) - ${university['Total_Cost_USD']:,.0f}")
```

## How to Run Locally
1. Install dependencies: `pip install -r requirements.txt`
2. Run the app: `streamlit run dashboard.py`

## Data
The dashboard uses bundled university cost data from `International_Education_Costs.csv`