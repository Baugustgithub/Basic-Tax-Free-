import streamlit as st

# --- Title ---
st.title("VCU Pay Stub Simulator: 2025")

# --- User Inputs ---
st.sidebar.header("Your Inputs")
gross_annual_income = st.sidebar.number_input("Annual Gross Income ($)", value=145125)
paychecks_per_year = 24  # Semi-monthly
gross_per_paycheck = gross_annual_income / paychecks_per_year

# Health Plan Dropdown
health_plan = st.sidebar.selectbox("Health Plan", {
    "COVA Care": 51.50,
    "COVA Care + Expanded Dental": 68.00,
    "COVA Care + Dental + Vision": 78.00,
    "COVA Care + OON + Full": 88.50,
    "COVA HealthAware": 8.50,
    "COVA HealthAware + Dental + Vision": 30.00,
    "COVA HDHP": 0.00,
    "Kaiser HMO": 43.00,
    "Sentara HMO": 43.00
}.keys())

health_plan_cost = {
    "COVA Care": 51.50,
    "COVA Care + Expanded Dental": 68.00,
    "COVA Care + Dental + Vision": 78.00,
    "COVA Care + OON + Full": 88.50,
    "COVA HealthAware": 8.50,
    "COVA HealthAware + Dental + Vision": 30.00,
    "COVA HDHP": 0.00,
    "Kaiser HMO": 43.00,
    "Sentara HMO": 43.00
}[health_plan]

# Retirement Contributions
contrib_403b = st.sidebar.number_input("403(b) Contribution per Paycheck", value=750)
is_roth_403b = st.sidebar.checkbox("Is 403(b) Roth?", value=False)

contrib_457b = st.sidebar.number_input("457(b) Contribution per Paycheck", value=750)
is_roth_457b = st.sidebar.checkbox("Is 457(b) Roth?", value=False)

# HSA and pension
contrib_hsa = st.sidebar.number_input("HSA Contribution per Paycheck", value=0)
pension_pct = 5.0

# --- Calculations ---
pension_contrib = gross_per_paycheck * pension_pct / 100
pretax_deductions = 0
posttax_deductions = 0

pretax_deductions += pension_contrib
pretax_deductions += contrib_hsa
pretax_deductions += health_plan_cost

if not is_roth_403b:
    pretax_deductions += contrib_403b
else:
    posttax_deductions += contrib_403b

if not is_roth_457b:
    pretax_deductions += contrib_457b
else:
    posttax_deductions += contrib_457b

taxable_income = gross_per_paycheck - pretax_deductions
fica = gross_per_paycheck * 0.062
medicare = gross_per_paycheck * 0.0145

# Federal tax brackets
def estimate_federal_tax(income):
    brackets = [(0, 0.10), (11925, 0.12), (48475, 0.22), (103350, 0.24)]
    tax = 0
    prev = 0
    for limit, rate in brackets:
        if income > prev:
            taxed = min(income, limit) - prev
            tax += taxed * rate
            prev = limit
    return tax

# Virginia state tax brackets
def estimate_va_tax(income):
    brackets = [(0, 0.02), (3000, 0.03), (5000, 0.05), (17000, 0.0575)]
    tax = 0
    prev = 0
    for limit, rate in brackets:
        if income > prev:
            taxed = min(income, limit) - prev
            tax += taxed * rate
            prev = limit
    return tax

fed_tax = estimate_federal_tax(taxable_income)
va_tax = estimate_va_tax(taxable_income)

net_pay = gross_per_paycheck - pretax_deductions - fed_tax - va_tax - fica - medicare - posttax_deductions

# --- Outputs ---
st.subheader("Pay Stub Summary")
st.write(f"**Gross Pay:** ${gross_per_paycheck:,.2f}")
st.write(f"**Pension Contribution (5%):** ${pension_contrib:,.2f}")
st.write(f"**Pre-Tax Deductions Total:** ${pretax_deductions:,.2f}")
st.write(f"**Post-Tax Deductions Total:** ${posttax_deductions:,.2f}")
st.write(f"**Taxable Income:** ${taxable_income:,.2f}")
st.write(f"**Federal Tax:** ${fed_tax:,.2f}")
st.write(f"**VA State Tax:** ${va_tax:,.2f}")
st.write(f"**FICA:** ${fica:,.2f}")
st.write(f"**Medicare:** ${medicare:,.2f}")
st.success(f"**Estimated Net Pay (Per Paycheck):** ${net_pay:,.2f}")