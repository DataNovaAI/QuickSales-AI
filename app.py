import streamlit as st
import pandas as pd

# =========================
# Page Configuration
# =========================
st.set_page_config(
    page_title="QuickSales AI",
    page_icon="📊",
    layout="wide"
)

# =========================
# Title
# =========================
st.title("📊 QuickSales AI")
st.subheader("Sales Intelligence Dashboard")

st.write(
    "Upload your sales data and discover "
    "important business insights."
)

# =========================
# File Upload
# =========================
uploaded_file = st.file_uploader(
    "📂 Upload your sales file",
    type=["csv", "xlsx"]
)

# =========================
# Load Data
# =========================
if uploaded_file is None:

    st.info(
        "Please upload a CSV or Excel sales file to begin."
    )

    st.stop()

try:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)

    else:
        df = pd.read_excel(uploaded_file)

except Exception as e:

    st.error(
        f"Could not read the file: {e}"
    )

    st.stop()

# =========================
# Required Columns
# =========================
required_columns = [
    "Date",
    "Order_ID",
    "Customer",
    "Product",
    "Category",
    "Quantity",
    "Total"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    st.error(
        "The uploaded file is missing required columns:"
    )

    for column in missing_columns:
        st.write(f"- {column}")

    st.info(
        "Required columns: "
        + ", ".join(required_columns)
    )

    st.stop()

# =========================
# Prepare Data
# =========================
try:

    df["Date"] = pd.to_datetime(df["Date"])

except Exception:

    st.error(
        "The Date column could not be converted to a valid date."
    )

    st.stop()

# =========================
# KPI Calculations
# =========================
total_revenue = df["Total"].sum()
total_orders = df["Order_ID"].nunique()
total_customers = df["Customer"].nunique()
total_units = df["Quantity"].sum()

if total_orders > 0:

    average_order_value = (
        total_revenue / total_orders
    )

else:

    average_order_value = 0

# =========================
# KPI Cards
# =========================
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "💰 Total Revenue",
    f"${total_revenue:,.2f}"
)

col2.metric(
    "🛒 Orders",
    f"{total_orders:,}"
)

col3.metric(
    "👥 Customers",
    f"{total_customers:,}"
)

col4.metric(
    "📦 Units Sold",
    f"{total_units:,}"
)

col5.metric(
    "💵 Avg Order Value",
    f"${average_order_value:,.2f}"
)

st.divider()

# =========================
# Monthly Sales
# =========================
st.header("📈 Monthly Sales")

df["Month"] = (
    df["Date"]
    .dt.to_period("M")
    .astype(str)
)

monthly_sales = (
    df.groupby("Month")["Total"]
    .sum()
)

st.line_chart(monthly_sales)

# =========================
# Product & Category
# =========================
col1, col2 = st.columns(2)

with col1:

    st.header("🏆 Top Products")

    product_sales = (
        df.groupby("Product")["Total"]
        .sum()
        .sort_values(ascending=False)
    )

    st.bar_chart(product_sales)

with col2:

    st.header("📂 Sales by Category")

    category_sales = (
        df.groupby("Category")["Total"]
        .sum()
        .sort_values(ascending=False)
    )

    st.bar_chart(category_sales)

st.divider()

# =========================
# Top Customers
# =========================
st.header("👑 Top Customers")

customer_sales = (
    df.groupby("Customer")["Total"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

customer_table = customer_sales.reset_index()

customer_table.columns = [
    "Customer",
    "Total Spending"
]

st.dataframe(
    customer_table,
    use_container_width=True,
    hide_index=True
)

st.divider()

# =========================
# Customer Segmentation
# =========================
st.header("👥 Customer Segmentation")

reference_date = df["Date"].max()

customer_data = df.groupby("Customer").agg(
    Total_Spending=("Total", "sum"),
    Total_Orders=("Order_ID", "nunique"),
    Last_Purchase=("Date", "max")
).reset_index()

customer_data["Days_Since_Last_Purchase"] = (
    reference_date - customer_data["Last_Purchase"]
).dt.days


def classify_customer(row):

    spending = row["Total_Spending"]
    days = row["Days_Since_Last_Purchase"]

    if spending >= 2500:

        return "VIP"

    elif days >= 60:

        return "Lost"

    elif days <= 30 and row["Total_Orders"] <= 2:

        return "New"

    else:

        return "Regular"


customer_data["Segment"] = customer_data.apply(
    classify_customer,
    axis=1
)

# =========================
# Segment Summary
# =========================
segment_counts = (
    customer_data["Segment"]
    .value_counts()
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "⭐ VIP Customers",
    int(segment_counts.get("VIP", 0))
)

col2.metric(
    "⚠️ Lost Customers",
    int(segment_counts.get("Lost", 0))
)

col3.metric(
    "🆕 New Customers",
    int(segment_counts.get("New", 0))
)

col4.metric(
    "👤 Regular Customers",
    int(segment_counts.get("Regular", 0))
)

st.bar_chart(segment_counts)

# =========================
# Segment Details
# =========================
selected_segment = st.selectbox(
    "Select customer segment",
    ["VIP", "Lost", "New", "Regular"]
)

segment_customers = customer_data[
    customer_data["Segment"] == selected_segment
].sort_values(
    "Total_Spending",
    ascending=False
)

st.dataframe(
    segment_customers[
        [
            "Customer",
            "Total_Spending",
            "Total_Orders",
            "Last_Purchase",
            "Days_Since_Last_Purchase",
            "Segment"
        ]
    ],
    use_container_width=True,
    hide_index=True
)

st.divider()

# =========================
# Business Insights
# =========================
st.header("💡 Business Insights")

top_product = product_sales.index[0]
top_product_revenue = product_sales.iloc[0]

top_category = category_sales.index[0]
top_category_revenue = category_sales.iloc[0]

best_month = monthly_sales.idxmax()
best_month_revenue = monthly_sales.max()

st.success(
    f"🏆 **Top Product:** {top_product} "
    f"generated ${top_product_revenue:,.2f}"
)

st.info(
    f"📂 **Top Category:** {top_category} "
    f"generated ${top_category_revenue:,.2f}"
)

st.warning(
    f"📅 **Best Month:** {best_month} "
    f"with ${best_month_revenue:,.2f} revenue"
)

st.divider()

# =========================
# Uploaded Data Preview
# =========================
st.header("📋 Uploaded Data")

st.write(
    f"File: **{uploaded_file.name}**"
)

st.write(
    f"Rows: **{len(df):,}**"
)

st.dataframe(
    df.head(20),
    use_container_width=True,
    hide_index=True
)

# =========================
# Footer
# =========================
st.divider()

st.caption(
    "QuickSales AI — Sales Intelligence & Business Analytics"
)