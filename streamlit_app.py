import streamlit as st
import requests
import pandas as pd
import time
import random

# --- Page Config & API URL ---
st.set_page_config(
    page_title="SecureBank Fraud Detection",
    page_icon="💳",
    layout="centered"
)

# !! CRITICAL: This is your LIVE backend API on Render !!
API_URL = "https://fraud-detection-api-ddtn.onrender.com" 

# --- Custom CSS for "Bank" Theme ---
st.markdown("""
<style>
    /* Main app styling */
    .stApp {
        background-color: #f5f5f5; /* Light grey background */
    }
    
    /* Custom button styling */
    .stButton > button {
        border: 2px solid #004A99; /* Dark blue border */
        background-color: #0056B3; /* Dark blue background */
        color: white; /* White text */
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #004A99; /* Slightly darker on hover */
        border-color: #003D80;
    }
    .stButton > button:active {
        background-color: #003D80; /* Darker on click */
        border-color: #003D80;
    }
    
    /* Style headers to match the theme */
    h1, h2, h3 {
        color: #004A99; /* Dark blue headers */
    }

    /* Style for the form */
    .stForm {
        background-color: #ffffff;
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    /* Style for tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 8px 8px 0 0;
        gap: 5px;
        padding: 10px 15px;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0056B3;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# --- Header & Logo ---
# Using a placeholder for a clean "bank" logo
st.image("https://placehold.co/600x100/004A99/FFFFFF?text=SecureBank+Portal&font=lato", use_column_width=True)
st.title("💳 Real-Time Transaction Analysis")

# --- Helper Function to Get History ---
# Use caching to avoid re-fetching data on every interaction
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
tab1, tab2 = st.tabs(["🏦 Make a Payment", "📈 Transaction Ledger"])

# --- TAB 1: Payment Form ---
with tab1:
    st.header("New Transaction")
    
    with st.form("payment_form"):
        st.markdown("Enter payment details to simulate a transaction.")
        
        # Realistic form fields
        col1, col2 = st.columns(2)
        with col1:
            cardholder_name = st.text_input("Cardholder Name", "John M. Doe")
            card_number = st.text_input("Card Number (mock)", "4242 4242 4242 4242")
            merchant = st.text_input("Merchant Name", "Amazon Web Services")
        
        with col2:
            # This is the 'Amount' that will be sent to the model
            amount = st.number_input("Amount ($)", min_value=0.01, value=199.99, step=10.0, format="%.2f")
            expiry_date = st.text_input("Expiry Date (MM/YY)", "12/26")
            cvv = st.text_input("CVV (mock)", "123", type="password")
            
        # Submit button for the form
        submit_button = st.form_submit_button("Submit Secure Payment")

    if submit_button:
        # Clear history cache to show new transaction later
        st.cache_data.clear()
        
        with st.spinner("Processing transaction... Contacting bank..."):
            # --- SIMULATION ---
            # Generate the 'V' features and 'Time' for the model
            # The user doesn't see this; it mimics real feature extraction.
            v_features = {f'V{i}': random.uniform(-5, 5) for i in range(1, 29)}
            
            # Construct the transaction data payload for the API
            transaction_data = {
                "Time": time.time() % 172800,  # Use seconds, modulo 2 days (as in the original dataset)
                "Amount": amount,
                **v_features
            }
            
            try:
                # Send data to the FastAPI backend
                response = requests.post(f"{API_URL}/predict/", json=transaction_data)
                
                if response.status_code == 200:
                    prediction = response.json()
                    
                    is_fraud = prediction['is_fraud']
                    prob_fraud = prediction['probability_fraud'] * 100
                    
                    if is_fraud == 1:
                        st.error(f"**Transaction DENIED: High Fraud Risk!** (Probability: {prob_fraud:.2f}%)")
                        st.warning("This transaction has been flagged and saved to the ledger for review.")
                    else:
                        st.success(f"**Transaction Approved** (Fraud Probability: {prob_fraud:.2f}%)")
                        st.balloons()
                else:
                    st.error(f"Error from API ({response.status_code}): {response.text}")
            
            except requests.exceptions.ConnectionError:
                st.error(f"Connection Error: Could not connect to the API at {API_URL}.")
            except Exception as e:
                st.error(f"An error occurred during submission: {e}")

# --- TAB 2: Transaction History ---
with tab2:
    st.header("Transaction Ledger")
    st.markdown("View all processed transactions from the secure database.")
    
    if st.button("Refresh History"):
        st.cache_data.clear()
        st.toast("Refreshing history...")

    # Get data from our helper function
    history_df = get_history()
    
    if history_df.empty:
        st.info("No transaction history found. Submit a payment to see it appear here.")
    else:
        # --- Format the DataFrame for a clean look ---
        # Add a human-readable 'Status' column
        history_df['Status'] = history_df['is_fraud'].apply(lambda x: "FRAUD 🚨" if x == 1 else "Genuine ✅")
        
        # Format probability as a percentage string
        history_df['Fraud Probability'] = history_df['probability_fraud'].apply(lambda p: f"{p*100:.2f}%")
        
        # Format Amount to 2 decimal places
        history_df['Amount'] = history_df['Amount'].apply(lambda a: f"${a:.2f}")

        # Select and reorder columns for display
        display_cols = ['id', 'Amount', 'Status', 'Fraud Probability', 'Time']
        
        st.dataframe(
            history_df.sort_values(by="id", ascending=False)[display_cols],
            use_container_width=True,
            hide_index=True
        )
