"""
Interactive Mortgage Calculator Dashboard
==========================================
Using Pure PV-Based Formulas

Run with: streamlit run mortgage_dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mortgage_pv_calculator import (
    generate_amortization_schedule,
    calculate_accelerated_payoff,
    format_currency,
    format_percentage
)

# Page configuration
st.set_page_config(
    page_title="Mortgage Calculator - PV Based",
    page_icon="🏠",
    layout="wide"
)

# Title and description
st.title("🏠 Mortgage Calculator")
st.subheader("Using Pure Present Value (PV) Formulas")
st.markdown("---")

# Sidebar for inputs
st.sidebar.header("📊 Loan Parameters")

# Input fields with default values
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
) / 100  # Convert to decimal

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

# Generate amortization schedule
try:
    df, payment, y, n = generate_amortization_schedule(
        principal, annual_rate, years, frequency.lower()
    )
    
    # Display key metrics in columns
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
    
    # Amortization Schedule Table
    st.markdown("## 📋 Amortization Schedule (PV-Based)")
    
    # Format DataFrame for display
    display_df = df.copy()
    display_df['Payment_Amount'] = display_df['Payment_Amount'].apply(lambda x: f"${x:,.2f}")
    display_df['Interest_Paid'] = display_df['Interest_Paid'].apply(lambda x: f"${x:,.2f}")
    display_df['Principal_Paid'] = display_df['Principal_Paid'].apply(lambda x: f"${x:,.2f}")
    display_df['PV_of_Principal'] = display_df['PV_of_Principal'].apply(lambda x: f"${x:,.2f}")
    display_df['Outstanding_Balance'] = display_df['Outstanding_Balance'].apply(lambda x: f"${x:,.2f}")
    display_df['Cumulative_Interest'] = display_df['Cumulative_Interest'].apply(lambda x: f"${x:,.2f}")
    display_df['Cumulative_Principal'] = display_df['Cumulative_Principal'].apply(lambda x: f"${x:,.2f}")
    
    # Rename columns for better display
    display_df.columns = [
        'Payment #', 'Payment', 'Interest', 'Principal', 
        'PV(Principal)', 'Outstanding', 'Cum. Interest', 'Cum. Principal'
    ]
    
    # Show full table with option to download
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400
    )
    
    # Download button
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Schedule as CSV",
        data=csv,
        file_name=f"mortgage_schedule_{principal}_{annual_rate*100}pct_{years}yr.csv",
        mime="text/csv"
    )
    
    st.markdown("---")
    
    # Visualization
    st.markdown("## 📊 Visualization")
    
    tab1, tab2, tab3 = st.tabs(["Outstanding Balance", "Principal vs Interest", "Cumulative Analysis"])
    
    with tab1:
        st.markdown("### Outstanding Balance Over Time")
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(df['Payment_Number'], df['Outstanding_Balance'], 
                linewidth=2, color='#1f77b4', label='Outstanding Balance')
        ax.fill_between(df['Payment_Number'], df['Outstanding_Balance'], 
                        alpha=0.3, color='#1f77b4')
        ax.set_xlabel(f'Payment Number (Total: {n})', fontsize=12)
        ax.set_ylabel('Outstanding Balance ($)', fontsize=12)
        ax.set_title('Loan Balance Reduction Over Time', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
        st.pyplot(fig)
    
    with tab2:
        st.markdown("### Principal vs Interest Per Payment")
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(df['Payment_Number'], df['Principal_Paid'], 
                linewidth=2, color='green', label='Principal', alpha=0.8)
        ax.plot(df['Payment_Number'], df['Interest_Paid'], 
                linewidth=2, color='red', label='Interest', alpha=0.8)
        ax.fill_between(df['Payment_Number'], df['Principal_Paid'], 
                        alpha=0.2, color='green')
        ax.fill_between(df['Payment_Number'], df['Interest_Paid'], 
                        alpha=0.2, color='red')
        ax.set_xlabel(f'Payment Number', fontsize=12)
        ax.set_ylabel('Amount ($)', fontsize=12)
        ax.set_title('Principal vs Interest Components', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        st.pyplot(fig)
    
    with tab3:
        st.markdown("### Cumulative Analysis")
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(df['Payment_Number'], df['Cumulative_Principal'], 
                linewidth=2, color='green', label='Cumulative Principal', alpha=0.8)
        ax.plot(df['Payment_Number'], df['Cumulative_Interest'], 
                linewidth=2, color='red', label='Cumulative Interest', alpha=0.8)
        ax.set_xlabel(f'Payment Number', fontsize=12)
        ax.set_ylabel('Cumulative Amount ($)', fontsize=12)
        ax.set_title('Cumulative Principal vs Interest Paid', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
        st.pyplot(fig)
    
    st.markdown("---")
    
    # EXTRA CREDIT: Accelerated Payoff
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
            value=float(payment * 1.2),  # Default: 20% more
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
            
            # Comparison chart
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Plot original schedule
            ax.plot(df['Payment_Number'], df['Outstanding_Balance'], 
                   linewidth=2, color='#1f77b4', label=f'Original ({n} payments)', alpha=0.7)
            
            # Plot accelerated schedule
            ax.plot(new_df['Payment_Number'], new_df['Outstanding_Balance'], 
                   linewidth=2, color='green', label=f'Accelerated ({n_new} payments)', alpha=0.7)
            
            ax.fill_between(df['Payment_Number'], df['Outstanding_Balance'], 
                           alpha=0.2, color='#1f77b4')
            ax.fill_between(new_df['Payment_Number'], new_df['Outstanding_Balance'], 
                           alpha=0.2, color='green')
            
            ax.set_xlabel('Payment Number', fontsize=12)
            ax.set_ylabel('Outstanding Balance ($)', fontsize=12)
            ax.set_title('Original vs Accelerated Payoff Schedule', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.legend()
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
            
            st.pyplot(fig)
            
            # Show accelerated schedule table
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
