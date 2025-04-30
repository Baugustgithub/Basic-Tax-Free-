import streamlit as st

# --- Title ---
st.title("VCU Pay Stub Simulator: 2025 (Enhanced Version)")

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

# Annual Contributions
annual_403b = st.sidebar.number_input("Annual 403(b) Contribution", value=18000)
is_roth_403b = st.sidebar.checkbox("403(b) as Roth?", value=False)
annual_457b = st.sidebar.number_input("Annual 457(b) Contribution", value=18000)
is_roth_457b = st.sidebar.checkbox("457(b) as Roth?", value=False)
annual_hsa = st.sidebar.number_input("Annual HSA Contribution", value=0)

# Other deductions
parking_per_paycheck = st.sidebar.number_input("Parking Deduction (Per Paycheck)", value=46.00)

# Convert to per-paycheck
per_check_403b = annual_403b / paychecks_per_year
per_check_457b = annual_457b / paychecks_per_year
per_check_hsa = annual_hsa / paychecks_per_year

# --- Deductions ---
pension_contrib = gross_per_paycheck * 0.05
pretax_deductions = pension_contrib + per_check_hsa + health_plan_cost + parking_per_paycheck
posttax_deductions = 0

if not is_roth_403b:
    pretax_deductions += per_check_403b
else:
    posttax_deductions += per_check_403b

if not is_roth_457b:
    pretax_deductions += per_check_457b
else:
    posttax_deductions += per_check_457b

taxable_income = gross_per_paycheck - pretax_deductions
fica = gross_per_paycheck * 0.062
medicare = gross_per_paycheck * 0.0145

# --- Tax Estimations ---
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
st.subheader("Per-Paycheck Summary")
st.write(f"**Gross Pay:** ${gross_per_paycheck:,.2f}")
st.write(f"**Health Plan ({health_plan}):** -${health_plan_cost:,.2f}")
st.write(f"**Parking Deduction:** -${parking_per_paycheck:,.2f}")
st.write(f"**Pension Contribution (5%):** -${pension_contrib:,.2f}")
st.write(f"**HSA Contribution:** -${per_check_hsa:,.2f}")
if not is_roth_403b:
    st.write(f"**403(b) Pre-Tax Contribution:** -${per_check_403b:,.2f}")
else:
    st.write(f"**403(b) Roth Contribution (post-tax):** -${per_check_403b:,.2f}")
if not is_roth_457b:
    st.write(f"**457(b) Pre-Tax Contribution:** -${per_check_457b:,.2f}")
else:
    st.write(f"**457(b) Roth Contribution (post-tax):** -${per_check_457b:,.2f}")
st.write(f"**Total Pre-Tax Deductions:** ${pretax_deductions:,.2f}")
st.write(f"**Post-Tax Deductions:** ${posttax_deductions:,.2f}")
st.write(f"**Federal Tax:** ${fed_tax:,.2f}")
st.write(f"**VA State Tax:** ${va_tax:,.2f}")
st.write(f"**FICA:** ${fica:,.2f}")
st.write(f"**Medicare:** ${medicare:,.2f}")
st.success(f"**Estimated Net Pay (Per Paycheck):** ${net_pay:,.2f}")

# --- Annual Summary ---
total_net_pay = net_pay * paychecks_per_year
monthly_take_home = total_net_pay / 12
total_contributions = annual_403b + annual_457b + annual_hsa + (gross_annual_income * 0.05)
effective_tax_rate = (fed_tax + va_tax + fica + medicare) * paychecks_per_year / gross_annual_income

st.subheader("Annual Summary")
st.write(f"**Total Net Pay (Annual):** ${total_net_pay:,.2f}")
st.write(f"**Monthly Take-Home Pay (Estimate):** ${monthly_take_home:,.2f}")
st.write(f"**Total Tax-Deferred Savings (403b, 457b, HSA, Pension):** ${total_contributions:,.2f}")
st.write(f"**Effective Tax Rate:** {effective_tax_rate:.2%}")