import streamlit as st
import requests
import pandas as pd
import time
import random

# --- Page Config & API URL ---
st.set_page_config(
    page_title="SecureBank Fraud Detection",
    page_icon="💳",
    layout="centered",
    # [NEW] This tells Streamlit to use the system theme by default
    initial_sidebar_state="auto" 
)

# !! CRITICAL: This is your LIVE backend API on Render !!
API_URL = "https://fraud-detection-api-ddtn.onrender.com" 

# --- [NEW] Initialize Wallet in Session State ---
if 'wallet_balance' not in st.session_state:
    st.session_state.wallet_balance = 500000.00
# -----------------------------------------------

# --- FRAUD SIMULATION TEMPLATE ---
# This is the "secret" data pattern that our model will flag as fraud.
FRAUD_TRANSACTION_TEMPLATE = {
    'V1': -2.3, 'V2': 1.1, 'V3': -4.5, 'V4': 4.1, 'V5': -2.1,
    'V6': -1.2, 'V7': -5.5, 'V8': 0.7, 'V9': -2.1, 'V10': -5.2,
    'V11': 4.0, 'V12': -7.9, 'V13': 0.1, 'V14': -8.1, 'V15': -0.3,
    'V16': -3.1, 'V17': -12.2, 'V18': 0.8, 'V19': 0.1, 'V20': 0.3,
    'V21': 0.6, 'V22': 0.1, 'V23': 0.0, 'V24': -0.2, 'V25': -0.1,
    'V26': 0.1, 'V27': 0.4, 'V28': 0.1
}
# --- Secret Trigger Values ---
SECRET_FRAUD_MERCHANT = "Risk-Wallet.com"
SECRET_FRAUD_AMOUNT = 987654.00

# --- [NEW] Theme-Aware Custom CSS ---
# This CSS uses Streamlit's built-in theme variables
# It will now look good in BOTH light and dark mode automatically
st.markdown("""
<style>
    /* We are no longer forcing a background color on the app.
    We let Streamlit handle it (var(--background-color)).
    */
    
    /* Standard button */
    .stButton > button {
        /* Use Streamlit's primary color for the button */
        border: 2px solid var(--primary-color);
        background-color: var(--primary-color);
        color: white; /* Text on buttons is almost always white */
        border-radius: 8px; 
        padding: 10px 20px; 
        font-weight: bold;
        transition: all 0.3s ease; 
        width: 100%;
    }
    .stButton > button:hover {
        /* Make it slightly darker on hover */
        filter: brightness(0.9);
    }
    
    /* Headers will now use the default theme text color */
    h1, h2, h3 { 
        /* We removed the hard-coded blue color */
        /* It will be dark on a light background, and light on a dark background */
        color: var(--text-color);
    }
    
    /* Forms, Metrics, and Tabs will use the theme's secondary background */
    .stForm, [data-testid="stMetric"] {
        background-color: var(--secondary-background-color);
        border: 1px solid var(--secondary-background-color);
        border-radius: 10px; 
        padding: 20px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text-color);
        opacity: 0.7; /* Make the label a bit lighter */
    }
    [data-testid="stMetricValue"] {
        font-size: 2.5em;
        color: var(--primary-color); /* Use accent color for the value */
    }
    
    .stTabs [data-baseweb="tab-list"] { gap: 2px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; 
        white-space: pre-wrap; 
        background-color: var(--secondary-background-color);
        border-radius: 8px 8px 0 0; 
        gap: 5px; 
        padding: 10px 15px;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] { 
        background-color: var(--primary-color); 
        color: white; 
        font-weight: bold; 
    }
</style>
""", unsafe_allow_html=True)
# ------------------------------------------


# --- Header & Logo ---
# [NEW] Using a theme-aware placeholder. 
# In dark mode, text will be light. In light mode, text will be dark.
st.image("https://placehold.co/600x100?text=SecureBank+Portal&font=lato", use_column_width=True)
st.title("💳 Real-Time Transaction Analysis")

# --- Helper Function to Get History ---
@st.cache_data(ttl=60)
def get_history():
    """Fetches transaction history from the backend."""
    try:
        response = requests.get(f"{API_URL}/history/")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            st.error(f"Failed to fetch history (Status: {response.status_code})")
            return pd.DataFrame()
    except requests.exceptions.ConnectionError:
        st.error(f"Connection Error: Could not connect to the API at {API_URL}.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return pd.DataFrame()

# --- Main App Layout (Tabs) ---
tab1, tab2, tab3 = st.tabs(["💼 My Wallet", "🏦 Make a Payment", "📈 Transaction Ledger"])

# --- TAB 1: My Wallet ---
with tab1:
    st.header("Your Current Balance")
    
    # Display the balance using the session state variable
    st.metric(
        label="Available Funds",
        value=f"₹{st.session_state.wallet_balance:,.2f}"
    )
    
    st.markdown("---")
    st.subheader("Wallet Actions")
    if st.button("Reset Balance to ₹5,00,000"):
        st.session_state.wallet_balance = 500000.00
        st.toast("Wallet balance has been reset.")
        # Rerun to instantly update the metric
        st.rerun()

# --- TAB 2: Make a Payment ---
with tab2:
    st.header("New Transaction")
    
    with st.form("payment_form"):
        st.markdown("Enter payment details to simulate a transaction.")
        
        col1, col2 = st.columns(2)
        with col1:
            cardholder_name = st.text_input("Cardholder Name", "John M. Doe")
            # This is one of our "secret triggers"
            merchant = st.text_input("Merchant Name", "Amazon Web Services")
        with col2:
            # This is our other "secret trigger"
            amount = st.number_input("Amount (₹)", min_value=0.01, value=15000.00, step=100.0, format="%.2f")
            
        st.markdown("---")
        # Only one submit button
        submit_button = st.form_submit_button("Submit Secure Payment")

    if submit_button:
        # Clear history cache to show new transaction later
        st.cache_data.clear()
        
        # --- Insufficient Funds Check ---
        if amount > st.session_state.wallet_balance:
            st.error(f"**Transaction DENIED: Insufficient Funds!**")
            st.warning(f"Your balance is ₹{st.session_state.wallet_balance:,.2f}, but you requested ₹{amount:,.2f}.")
        else:
            # --- Hidden Trigger Logic ---
            is_secret_fraud = (
                merchant == SECRET_FRAUD_MERCHANT or 
                amount == SECRET_FRAUD_AMOUNT
            )
            
            if is_secret_fraud:
                st.toast("High-Risk transaction detected, running extra checks...")
                v_features = {k: v + random.uniform(-0.1, 0.1) for k, v in FRAUD_TRANSACTION_TEMPLATE.items()}
            else:
                # This is the "Genuine" path
                v_features = {f'V{i}': random.uniform(-5, 5) for i in range(1, 29)}
            
            with st.spinner("Processing transaction... Contacting bank..."):
                
                transaction_data = {
                    "Time": time.time() % 172800,
                    "Amount": amount,
                    **v_features
                }
                
                try:
                    response = requests.post(f"{API_URL}/predict/", json=transaction_data)
                    
                    if response.status_code == 200:
                        prediction = response.json()
                        is_fraud = prediction['is_fraud']
                        prob_fraud = prediction['probability_fraud'] * 100
                        
                        if is_fraud == 1:
                            st.error(f"**Transaction DENIED: High Fraud Risk!** (Probability: {prob_fraud:.2f}%)")
                            st.warning("This transaction has been flagged and saved to the ledger. Your balance was not affected.")
                        else:
                            # --- Subtract from wallet on success ---
                            st.session_state.wallet_balance -= amount
                            st.success(f"**Transaction Approved** (Fraud Probability: {prob_fraud:.2f}%)")
                            st.balloons()
                            st.info(f"New balance: ₹{st.session_state.wallet_balance:,.2f}")
                            
                    else:
                        st.error(f"Error from API ({response.status_code}): {response.text}")
                
                except requests.exceptions.ConnectionError:
                    st.error(f"Connection Error: Could not connect to the API at {API_URL}.")
                except Exception as e:
                    st.error(f"An error occurred during submission: {e}")

# --- TAB 3: Transaction Ledger ---
with tab3:
    st.header("Transaction Ledger")
    st.markdown("View all processed transactions from the secure database.")
    
    if st.button("Refresh History"):
        st.cache_data.clear()
        st.toast("Refreshing history...")

    history_df = get_history()
    
    if history_df.empty:
        st.info("No transaction history found. Submit a payment to see it appear here.")
    else:
        # --- Format the DataFrame (changed to ₹) ---
        history_df['Status'] = history_df['is_fraud'].apply(lambda x: "FRAUD 🚨" if x == 1 else "Genuine ✅")
        history_df['Fraud Probability'] = history_df['probability_fraud'].apply(lambda p: f"{p*100:.2f}%")
        history_df['Amount'] = history_df['Amount'].apply(lambda a: f"₹{a:,.2f}")
        display_cols = ['id', 'Amount', 'Status', 'Fraud Probability', 'Time']
        
        st.dataframe(
            history_df.sort_values(by="id", ascending=False)[display_cols],
            use_container_width=True,
            hide_index=True
        )
