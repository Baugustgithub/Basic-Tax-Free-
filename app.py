import streamlit as st

# --- Title ---
st.title("VCU Pay Stub Simulator: 2025 (with Tax + Savings Rate Fixes)")

# --- Inputs ---
st.sidebar.header("Your Inputs")
gross_annual_income = st.sidebar.number_input("Annual Gross Income ($)", value=145125)
paychecks_per_year = 24
gross_per_paycheck = gross_annual_income / paychecks_per_year

# Health Plan
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
annual_403b = st.sidebar.number_input("Annual 403(b) Contribution", value=18000)
is_roth_403b = st.sidebar.checkbox("403(b) as Roth?", value=False)
annual_457b = st.sidebar.number_input("Annual 457(b) Contribution", value=18000)
is_roth_457b = st.sidebar.checkbox("457(b) as Roth?", value=False)

# Post-paycheck savings
annual_hsa = st.sidebar.number_input("HSA Contribution (post-paycheck)", value=0)
annual_brokerage = st.sidebar.number_input("Brokerage/Other Investments (post-paycheck)", value=0)

# Other deductions
parking_per_paycheck = st.sidebar.number_input("Parking (per paycheck)", value=46.00)

# Per-paycheck conversions
per_check_403b = annual_403b / paychecks_per_year
per_check_457b = annual_457b / paychecks_per_year
per_check_hsa = annual_hsa / paychecks_per_year
per_check_brokerage = annual_brokerage / paychecks_per_year

# --- Deductions ---
pension_contrib = gross_per_paycheck * 0.05
pretax_deductions = pension_contrib + health_plan_cost + parking_per_paycheck
posttax_deductions = per_check_hsa + per_check_brokerage

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
def estimate_fed_tax(annual_taxable):
    brackets = [(0, 0.10), (11925, 0.12), (48475, 0.22), (103350, 0.24)]
    tax = 0
    prev = 0
    for limit, rate in brackets:
        if annual_taxable > prev:
            taxed = min(annual_taxable, limit) - prev
            tax += taxed * rate
            prev = limit
    return tax

def estimate_va_tax(annual_taxable):
    brackets = [(0, 0.02), (3000, 0.03), (5000, 0.05), (17000, 0.0575)]
    tax = 0
    prev = 0
    for limit, rate in brackets:
        if annual_taxable > prev:
            taxed = min(annual_taxable, limit) - prev
            tax += taxed * rate
            prev = limit
    return tax

# Annualized AGI
annual_pretax_contribs = (
    (annual_403b if not is_roth_403b else 0) +
    (annual_457b if not is_roth_457b else 0) +
    gross_annual_income * 0.05 +  # pension
    health_plan_cost * paychecks_per_year +
    parking_per_paycheck * paychecks_per_year
)
annual_agi = gross_annual_income - annual_pretax_contribs
standard_deduction = 14600
taxable_income_annual = max(annual_agi - standard_deduction, 0)

# Total taxes
fed_tax_annual = estimate_fed_tax(taxable_income_annual)
va_tax_annual = estimate_va_tax(taxable_income_annual)
fica_annual = gross_annual_income * 0.062
medicare_annual = gross_annual_income * 0.0145
total_tax = fed_tax_annual + va_tax_annual + fica_annual + medicare_annual
effective_tax_rate = total_tax / gross_annual_income

# Net pay
fed_tax = fed_tax_annual / paychecks_per_year
va_tax = va_tax_annual / paychecks_per_year
net_pay = gross_per_paycheck - pretax_deductions - fed_tax - va_tax - fica - medicare - posttax_deductions

# --- Results ---
st.subheader("Per-Paycheck Summary")
st.write(f"**Gross Pay:** ${gross_per_paycheck:,.2f}")
st.write(f"**Health Plan ({health_plan}):** -${health_plan_cost:,.2f}")
st.write(f"**Parking:** -${parking_per_paycheck:,.2f}")
st.write(f"**Pension (5%):** -${pension_contrib:,.2f}")
if not is_roth_403b:
    st.write(f"**403(b) Pre-Tax:** -${per_check_403b:,.2f}")
else:
    st.write(f"**403(b) Roth (Post-Tax):** -${per_check_403b:,.2f}")
if not is_roth_457b:
    st.write(f"**457(b) Pre-Tax:** -${per_check_457b:,.2f}")
else:
    st.write(f"**457(b) Roth (Post-Tax):** -${per_check_457b:,.2f}")
st.write(f"**HSA (Post-Tax):** -${per_check_hsa:,.2f}")
st.write(f"**Brokerage (Post-Tax):** -${per_check_brokerage:,.2f}")
st.write(f"**Federal Tax:** -${fed_tax:,.2f}")
st.write(f"**VA State Tax:** -${va_tax:,.2f}")
st.write(f"**FICA:** -${fica:,.2f}")
st.write(f"**Medicare:** -${medicare:,.2f}")
st.success(f"**Net Pay (Per Paycheck):** ${net_pay:,.2f}")

# Annual summaries
total_net = net_pay * paychecks_per_year
monthly_take_home = total_net / 12
total_savings = annual_403b + annual_457b + annual_hsa + annual_brokerage + gross_annual_income * 0.05
savings_rate = total_savings / gross_annual_income

st.subheader("Annual Summary")
st.write(f"**Total Net Pay (Annual):** ${total_net:,.2f}")
st.write(f"**Monthly Take-Home Pay:** ${monthly_take_home:,.2f}")
st.write(f"**Total Savings (403b, 457b, HSA, Pension, Brokerage):** ${total_savings:,.2f}")
st.write(f"**Savings Rate:** {savings_rate:.2%}")
st.write(f"**Effective Tax Rate:** {effective_tax_rate:.2%}")