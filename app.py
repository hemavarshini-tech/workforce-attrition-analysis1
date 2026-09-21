import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# --------------------------------------------------
# PAGE SETTINGS
# --------------------------------------------------

st.set_page_config(
    page_title="Workforce Attrition Analysis",
    page_icon="📊",
    layout="wide"
)


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

df = pd.read_excel("Palo Alto Networks.xls")


# --------------------------------------------------
# CREATE AGE GROUP
# Same grouping used in your notebook
# --------------------------------------------------

age_bins = [0, 25, 35, 45, 55, 100]

age_labels = [
    "≤25",
    "26-35",
    "36-45",
    "46-55",
    "56+"
]

df["AgeGroup"] = pd.cut(
    df["Age"],
    bins=age_bins,
    labels=age_labels
)


# --------------------------------------------------
# CREATE TENURE GROUP
# Same grouping used in your notebook
# --------------------------------------------------

tenure_bins = [-1, 1, 3, 5, 10, 100]

tenure_labels = [
    "0-1 Years",
    "2-3 Years",
    "4-5 Years",
    "6-10 Years",
    "11+ Years"
]

df["TenureGroup"] = pd.cut(
    df["YearsAtCompany"],
    bins=tenure_bins,
    labels=tenure_labels
)


# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("Workforce Attrition Patterns and Risk Hotspot Analysis")

st.write(
    "Interactive dashboard for analyzing employee attrition "
    "patterns across departments, job roles, demographics, "
    "tenure, overtime and business travel."
)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.header("Dashboard Filters")


# Department selector

departments = sorted(df["Department"].unique())

selected_department = st.sidebar.selectbox(
    "Department",
    ["All"] + departments
)


# Job role selector

roles = sorted(df["JobRole"].unique())

selected_role = st.sidebar.selectbox(
    "Job Role",
    ["All"] + roles
)


# Tenure slider

min_years = int(df["YearsAtCompany"].min())
max_years = int(df["YearsAtCompany"].max())

selected_tenure = st.sidebar.slider(
    "Tenure Range",
    min_years,
    max_years,
    (min_years, max_years)
)


# Overtime filter

selected_overtime = st.sidebar.selectbox(
    "Overtime",
    ["All", "Yes", "No"]
)


# Business travel filter

selected_travel = st.sidebar.selectbox(
    "Business Travel",
    ["All"] + sorted(df["BusinessTravel"].unique())
)


# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------

filtered_df = df.copy()


if selected_department != "All":

    filtered_df = filtered_df[
        filtered_df["Department"] == selected_department
    ]


if selected_role != "All":

    filtered_df = filtered_df[
        filtered_df["JobRole"] == selected_role
    ]


filtered_df = filtered_df[
    (filtered_df["YearsAtCompany"] >= selected_tenure[0])
    &
    (filtered_df["YearsAtCompany"] <= selected_tenure[1])
]


if selected_overtime != "All":

    filtered_df = filtered_df[
        filtered_df["OverTime"] == selected_overtime
    ]


if selected_travel != "All":

    filtered_df = filtered_df[
        filtered_df["BusinessTravel"] == selected_travel
    ]


# --------------------------------------------------
# CHECK DATA
# --------------------------------------------------

if len(filtered_df) == 0:

    st.warning(
        "No employees match the selected filters."
    )

    st.stop()


# ==================================================
# MODULE 1
# ATTRITION OVERVIEW
# ==================================================

st.header("1. Attrition Overview Dashboard")


total_employees = len(filtered_df)

exited = filtered_df["Attrition"].sum()

retained = total_employees - exited

attrition_rate = (
    exited / total_employees
) * 100


# KPI cards

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Total Employees",
        total_employees
    )


with col2:

    st.metric(
        "Overall Attrition Rate",
        f"{attrition_rate:.2f}%"
    )


with col3:

    st.metric(
        "Exited Employees",
        int(exited)
    )


# --------------------------------------------------
# RETAINED VS EXITED
# --------------------------------------------------

col1, col2 = st.columns(2)


with col1:

    st.subheader("Retained vs Exited")

    status_data = pd.DataFrame({
        "Status": [
            "Retained",
            "Exited"
        ],
        "Employees": [
            retained,
            exited
        ]
    })

    fig, ax = plt.subplots()

    sns.barplot(
        data=status_data,
        x="Status",
        y="Employees",
        ax=ax
    )

    ax.set_xlabel("Employee Status")
    ax.set_ylabel("Number of Employees")

    st.pyplot(fig)


with col2:

    st.subheader("Attrition Distribution")

    fig, ax = plt.subplots()

    ax.pie(
        [retained, exited],
        labels=["Retained", "Exited"],
        autopct="%1.1f%%"
    )

    st.pyplot(fig)


# ==================================================
# MODULE 2
# DEPARTMENT & ROLE HEATMAP
# ==================================================

st.header("2. Department & Role Heatmaps")


# Department attrition

department_rate = (
    filtered_df.groupby("Department")["Attrition"]
    .mean() * 100
)


col1, col2 = st.columns(2)


with col1:

    st.subheader("Attrition Rate by Department")

    fig, ax = plt.subplots()

    sns.barplot(
        x=department_rate.index,
        y=department_rate.values,
        ax=ax
    )

    ax.set_xlabel("Department")
    ax.set_ylabel("Attrition Rate (%)")

    ax.tick_params(axis="x", rotation=20)

    st.pyplot(fig)


# --------------------------------------------------
# DEPARTMENT × ROLE HEATMAP
# --------------------------------------------------

with col2:

    st.subheader("Department × Job Role")

    heatmap_data = pd.crosstab(
        filtered_df["Department"],
        filtered_df["JobRole"],
        values=filtered_df["Attrition"],
        aggfunc="mean"
    ) * 100

    fig, ax = plt.subplots(figsize=(9, 6))

    sns.heatmap(
        heatmap_data,
        annot=True,
        fmt=".1f",
        cmap="coolwarm",
        ax=ax
    )

    ax.set_xlabel("Job Role")
    ax.set_ylabel("Department")

    st.pyplot(fig)


# --------------------------------------------------
# HIGH ATTRITION DEPARTMENT
# --------------------------------------------------

st.subheader("Department Attrition Summary")


department_summary = (
    filtered_df.groupby("Department")
    .agg(
        Employees=("Attrition", "count"),
        Exited=("Attrition", "sum"),
        Attrition_Rate=("Attrition", "mean")
    )
)

department_summary["Attrition_Rate"] = (
    department_summary["Attrition_Rate"] * 100
).round(2)


st.dataframe(
    department_summary,
    use_container_width=True
)


# ==================================================
# MODULE 3
# DEMOGRAPHIC ATTRITION EXPLORER
# ==================================================

st.header("3. Demographic Attrition Explorer")


col1, col2 = st.columns(2)


# --------------------------------------------------
# AGE
# --------------------------------------------------

with col1:

    st.subheader("Attrition by Age Group")

    age_rate = (
        filtered_df.groupby(
            "AgeGroup",
            observed=True
        )["Attrition"]
        .mean() * 100
    )

    fig, ax = plt.subplots()

    sns.barplot(
        x=age_rate.index,
        y=age_rate.values,
        ax=ax
    )

    ax.set_xlabel("Age Group")
    ax.set_ylabel("Attrition Rate (%)")

    st.pyplot(fig)


# --------------------------------------------------
# GENDER
# --------------------------------------------------

with col2:

    st.subheader("Attrition by Gender")

    gender_rate = (
        filtered_df.groupby("Gender")["Attrition"]
        .mean() * 100
    )

    fig, ax = plt.subplots()

    sns.barplot(
        x=gender_rate.index,
        y=gender_rate.values,
        ax=ax
    )

    ax.set_xlabel("Gender")
    ax.set_ylabel("Attrition Rate (%)")

    st.pyplot(fig)


# --------------------------------------------------
# EDUCATION
# --------------------------------------------------

st.subheader("Attrition by Education Level")


education_rate = (
    filtered_df.groupby("Education")["Attrition"]
    .mean() * 100
)


fig, ax = plt.subplots(figsize=(9, 5))

sns.barplot(
    x=education_rate.index,
    y=education_rate.values,
    ax=ax
)

ax.set_xlabel("Education Level")
ax.set_ylabel("Attrition Rate (%)")

st.pyplot(fig)


# ==================================================
# MODULE 4
# TENURE & WORKLOAD
# ==================================================

st.header("4. Tenure & Workload Analysis")


col1, col2 = st.columns(2)


# --------------------------------------------------
# TENURE
# --------------------------------------------------

with col1:

    st.subheader("Attrition by Tenure")

    tenure_rate = (
        filtered_df.groupby(
            "TenureGroup",
            observed=True
        )["Attrition"]
        .mean() * 100
    )

    fig, ax = plt.subplots()

    sns.barplot(
        x=tenure_rate.index,
        y=tenure_rate.values,
        ax=ax
    )

    ax.set_xlabel("Tenure")
    ax.set_ylabel("Attrition Rate (%)")

    st.pyplot(fig)


# --------------------------------------------------
# OVERTIME
# --------------------------------------------------

with col2:

    st.subheader("Overtime Impact")

    overtime_rate = (
        filtered_df.groupby("OverTime")["Attrition"]
        .mean() * 100
    )

    fig, ax = plt.subplots()

    sns.barplot(
        x=overtime_rate.index,
        y=overtime_rate.values,
        ax=ax
    )

    ax.set_xlabel("Overtime")
    ax.set_ylabel("Attrition Rate (%)")

    st.pyplot(fig)


# --------------------------------------------------
# BUSINESS TRAVEL
# --------------------------------------------------

st.subheader("Business Travel Impact")


travel_rate = (
    filtered_df.groupby("BusinessTravel")["Attrition"]
    .mean() * 100
)


fig, ax = plt.subplots(figsize=(9, 5))

sns.barplot(
    x=travel_rate.index,
    y=travel_rate.values,
    ax=ax
)

ax.set_xlabel("Business Travel")
ax.set_ylabel("Attrition Rate (%)")

st.pyplot(fig)


# ==================================================
# FILTERED DATA
# ==================================================

st.header("Filtered Employee Data")

st.write(
    f"Currently displaying {len(filtered_df)} employees."
)


display_columns = [
    "Age",
    "Gender",
    "Department",
    "JobRole",
    "YearsAtCompany",
    "OverTime",
    "BusinessTravel",
    "Attrition"
]


st.dataframe(
    filtered_df[display_columns],
    use_container_width=True
)


# ==================================================
# FOOTER
# ==================================================

st.markdown("---")

st.caption(
    "Workforce Attrition Patterns and Risk Hotspot Analysis"
)
