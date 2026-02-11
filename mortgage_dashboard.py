"""
Interactive Mortgage Calculator Dashboard
==========================================
Using Pure PV-Based Formulas

Run with: streamlit run mortgage_dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
from mortgage_pv_calculator import (
    generate_amortization_schedule,
    calculate_accelerated_payoff,
    format_currency,
    format_percentage
)

st.set_page_config(
    page_title="Mortgage Calculator - PV Based",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 Mortgage Calculator")
st.subheader("Using Pure Present Value (PV) Formulas")
st.markdown("---")

st.sidebar.header("📊 Loan Parameters")

principal = st.sidebar.number_input(
    "Principal Amount ($)",
    min_value=10000,
    max_value=10000000,
    value=300000,
    step=10000,
    help="Total loan amount"
)

annual_rate = st.sidebar.slider(
    "Annual Interest Rate (%)",
    min_value=0.0,
    max_value=15.0,
    value=6.0,
    step=0.25,
    help="Annual interest rate as percentage"
) / 100

years = st.sidebar.slider(
    "Loan Term (Years)",
    min_value=1,
    max_value=40,
    value=30,
    step=1,
    help="Duration of the loan"
)

frequency = st.sidebar.selectbox(
    "Payment Frequency",
    options=['Monthly', 'Quarterly', 'Annual'],
    index=0,
    help="How often you make payments"
)

try:
    df, payment, y, n = generate_amortization_schedule(
        principal, annual_rate, years, frequency.lower()
    )
    
    st.markdown("## 💰 Payment Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label=f"{frequency} Payment",
            value=format_currency(payment)
        )
    
    with col2:
        total_interest = df['Cumulative_Interest'].iloc[-1]
        st.metric(
            label="Total Interest",
            value=format_currency(total_interest)
        )
    
    with col3:
        total_paid = payment * n
        st.metric(
            label="Total Paid",
            value=format_currency(total_paid)
        )
    
    with col4:
        st.metric(
            label="Number of Payments",
            value=f"{n:,}"
        )
    
    st.markdown("---")
    
    st.markdown("## 📋 Amortization Schedule (PV-Based)")
    
    display_df = df.copy()
    display_df['Payment_Amount'] = display_df['Payment_Amount'].apply(lambda x: f"${x:,.2f}")
    display_df['Interest_Paid'] = display_df['Interest_Paid'].apply(lambda x: f"${x:,.2f}")
    display_df['Principal_Paid'] = display_df['Principal_Paid'].apply(lambda x: f"${x:,.2f}")
    display_df['PV_of_Principal'] = display_df['PV_of_Principal'].apply(lambda x: f"${x:,.2f}")
    display_df['Outstanding_Balance'] = display_df['Outstanding_Balance'].apply(lambda x: f"${x:,.2f}")
    display_df['Cumulative_Interest'] = display_df['Cumulative_Interest'].apply(lambda x: f"${x:,.2f}")
    display_df['Cumulative_Principal'] = display_df['Cumulative_Principal'].apply(lambda x: f"${x:,.2f}")
    
    display_df.columns = [
        'Payment #', 'Payment', 'Interest', 'Principal', 
        'PV(Principal)', 'Outstanding', 'Cum. Interest', 'Cum. Principal'
    ]
    
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400
    )
    
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Schedule as CSV",
        data=csv,
        file_name=f"mortgage_schedule_{principal}_{annual_rate*100}pct_{years}yr.csv",
        mime="text/csv"
    )
    
    st.markdown("---")
    
    st.markdown("## 📊 Visualization")
    
    tab1, tab2, tab3 = st.tabs(["Outstanding Balance", "Principal vs Interest", "Cumulative Analysis"])
    
    with tab1:
        st.markdown("### Outstanding Balance Over Time")
        st.line_chart(df.set_index('Payment_Number')['Outstanding_Balance'])
    
    with tab2:
        st.markdown("### Principal vs Interest Per Payment")
        chart_data = df.set_index('Payment_Number')[['Principal_Paid', 'Interest_Paid']]
        st.line_chart(chart_data)
    
    with tab3:
        st.markdown("### Cumulative Analysis")
        chart_data = df.set_index('Payment_Number')[['Cumulative_Principal', 'Cumulative_Interest']]
        st.line_chart(chart_data)
    
    st.markdown("---")
    
    st.markdown("## 🚀 Extra Credit: Accelerated Payoff Analysis")
    
    st.markdown("""
    See how increasing your payment amount affects the loan payoff time and total interest paid.
    """)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        increased_payment = st.number_input(
            f"Increased {frequency} Payment ($)",
            min_value=float(payment),
            max_value=float(payment * 3),
            value=float(payment * 1.2),
            step=50.0,
            help="Enter a payment amount higher than the minimum"
        )
    
    if increased_payment > payment:
        n_new, periods_saved, interest_saved, new_df = calculate_accelerated_payoff(
            principal, annual_rate, payment, increased_payment, frequency.lower()
        )
        
        if n_new is not None:
            with col2:
                st.success(f"### Results:")
                st.write(f"**New Payoff Time:** {n_new} payments ({n_new / (12 if frequency.lower() == 'monthly' else 4 if frequency.lower() == 'quarterly' else 1):.1f} years)")
                st.write(f"**Payments Saved:** {periods_saved}")
                st.write(f"**Interest Saved:** {format_currency(interest_saved)}")
                st.write(f"**New Total Interest:** {format_currency(new_df['Cumulative_Interest'].iloc[-1])}")
            
            st.markdown("### 📊 Accelerated Payoff Schedule Comparison")
            
            max_len = min(len(df), len(new_df))
            comparison_df = pd.DataFrame({
                'Original': df['Outstanding_Balance'].values[:max_len],
                'Accelerated': new_df['Outstanding_Balance'].values[:max_len]
            })
            comparison_df.index = range(1, max_len + 1)
            comparison_df.index.name = 'Payment Number'
            
            st.line_chart(comparison_df)
            
            with st.expander("📋 View Accelerated Payment Schedule"):
                display_new_df = new_df.copy()
                display_new_df['Payment_Amount'] = display_new_df['Payment_Amount'].apply(lambda x: f"${x:,.2f}")
                display_new_df['Interest_Paid'] = display_new_df['Interest_Paid'].apply(lambda x: f"${x:,.2f}")
                display_new_df['Principal_Paid'] = display_new_df['Principal_Paid'].apply(lambda x: f"${x:,.2f}")
                display_new_df['PV_of_Principal'] = display_new_df['PV_of_Principal'].apply(lambda x: f"${x:,.2f}")
                display_new_df['Outstanding_Balance'] = display_new_df['Outstanding_Balance'].apply(lambda x: f"${x:,.2f}")
                display_new_df['Cumulative_Interest'] = display_new_df['Cumulative_Interest'].apply(lambda x: f"${x:,.2f}")
                
                display_new_df.columns = [
                    'Payment #', 'Payment', 'Interest', 'Principal', 
                    'PV(Principal)', 'Outstanding', 'Cum. Interest'
                ]
                
                st.dataframe(display_new_df, use_container_width=True, height=400)
        else:
            st.error("⚠️ The increased payment is not sufficient to pay off the loan. Must be greater than interest-only payment.")

except Exception as e:
    st.error(f"Error generating amortization schedule: {str(e)}")
    st.exception(e)
