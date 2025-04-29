import streamlit as st

st.title("2025 Free Money Tax Estimator")

# --- User Inputs ---
gross_income = st.number_input("Gross Income ($)", value=145125)
contribution_403b = st.number_input("403(b) Contributions ($)", value=18000)
contribution_457b = st.number_input("457(b) Contributions ($)", value=1000)
pension_percent = st.number_input("Pension Contribution (% of Gross Pay)", value=5.0)
contribution_hsa = st.number_input("HSA Contributions ($)", value=0)
filing_status = st.selectbox("Filing Status", ["Single", "Married Filing Jointly", "Head of Household"])
qualifying_children = st.number_input("Number of Qualifying Children Under 17", value=0, step=1)

# --- Calculations ---
pension_contribution = gross_income * (pension_percent / 100)
total_pre_tax = contribution_403b + contribution_457b + pension_contribution + contribution_hsa
AGI = gross_income - total_pre_tax

# Standard Deduction
if filing_status == "Single":
    standard_deduction = 14600
elif filing_status == "Married Filing Jointly":
    standard_deduction = 29200
elif filing_status == "Head of Household":
    standard_deduction = 21900
else:
    standard_deduction = 14600

taxable_income = max(AGI - standard_deduction, 0)

# 2025 Brackets
if filing_status == "Single":
    brackets = [(0, 0.10), (11925, 0.12), (48475, 0.22), (103350, 0.24)]
elif filing_status == "Married Filing Jointly":
    brackets = [(0, 0.10), (23850, 0.12), (96950, 0.22), (206700, 0.24)]
else:  # Head of Household
    brackets = [(0, 0.10), (17900, 0.12), (71900, 0.22), (106350, 0.24)]

# Tax with contributions
tax = 0
prev = 0
for limit, rate in brackets:
    if taxable_income > prev:
        taxed = min(taxable_income, limit) - prev
        tax += taxed * rate
        prev = limit

# Apply Child Tax Credit
child_tax_credit = qualifying_children * 2000
tax -= child_tax_credit
final_tax = max(tax, 0)

# --- Baseline Scenario (No Contributions) ---
agi_baseline = gross_income
taxable_income_baseline = max(agi_baseline - standard_deduction, 0)

tax_baseline = 0
prev = 0
for limit, rate in brackets:
    if taxable_income_baseline > prev:
        taxed = min(taxable_income_baseline, limit) - prev
        tax_baseline += taxed * rate
        prev = limit

tax_baseline -= child_tax_credit
tax_baseline = max(tax_baseline, 0)

# --- Calculated Outputs ---
tax_savings = tax_baseline - final_tax
effective_tax_rate = final_tax / gross_income
effective_tax_rate_baseline = tax_baseline / gross_income

# --- Results ---
st.subheader("Results")
st.write(f"**Pension Contribution:** ${pension_contribution:,.2f}")
st.write(f"**Total Pre-Tax Contributions:** ${total_pre_tax:,.2f}")
st.write(f"**Adjusted Gross Income (AGI):** ${AGI:,.2f}")
st.write(f"**Taxable Income:** ${taxable_income:,.2f}")
st.write(f"**Estimated Federal Tax Owed:** ${final_tax:,.2f}")

st.markdown("### Contribution Impact")
st.write(f"**Federal Tax Without Contributions:** ${tax_baseline:,.2f}")
st.success(f"**Federal Tax Savings from Contributions:** ${tax_savings:,.2f}")
st.write(f"**Effective Tax Rate (With Contributions):** {effective_tax_rate:.2%}")
st.write(f"**Effective Tax Rate (No Contributions):** {effective_tax_rate_baseline:.2%}")