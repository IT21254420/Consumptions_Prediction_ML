import streamlit as st
import pandas as pd
import pickle
import json
from datetime import datetime
from google.oauth2.service_account import Credentials

# Load the trained models
electricity_model = pickle.load(open('Consumptions/electricity_pkl.sav', 'rb'))
steam_model = pickle.load(open('Consumptions/steam_pkl.sav', 'rb'))
water_model = pickle.load(open('Consumptions/water_pkl.sav', 'rb'))

# Google Sheets setup
def save_to_google_sheet(data):
    try:
        # Load the service account key from Streamlit secrets
        service_account_info = json.loads(st.secrets["google"]["GOOGLE_CLOUD_KEY"])

        # Specify required scopes for Google Sheets API
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]

        # Create credentials with scopes
        credentials = Credentials.from_service_account_info(service_account_info, scopes=scopes)

        # Authorize with Google Sheets
        import gspread
        client = gspread.authorize(credentials)

        # Open the spreadsheet
        sheet = client.open("Predictions Data").sheet1

        # Get the current date and time
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")  # Format: YYYY-MM-DD HH:MM:SS

        # Append the data with the timestamp
        sheet.append_row([current_time] + data)

    except gspread.SpreadsheetNotFound:
        st.error("The specified Google Sheet 'Predictions Data' could not be found. Please ensure it exists and is shared with the service account email.")
    except Exception as e:
        st.error(f"An error occurred while saving to Google Sheets: {str(e)}")

# Streamlit UI
st.markdown(
    "<div style='text-align: center; font-size: 46px; font-weight: bold;'>Multi-Consumption Prediction App</div>",
    unsafe_allow_html=True
)
st.write("")

# Layout for Day and Night Input Counts
st.subheader("Enter Machine Day and Night Counts")
st.write("")

# Function for side-by-side input with labels above the fields
def side_by_side_input(label, key_day, key_night):
    st.write(f"**{label} -**")
    col_day, col_night = st.columns([1, 1])
    with col_day:
        st.markdown("<div style='margin-bottom: -10px;'>Day</div>", unsafe_allow_html=True)
        day_value = st.number_input("", min_value=0, step=1, key=key_day, label_visibility='collapsed', value=None)
    with col_night:
        st.markdown("<div style='margin-bottom: -10px;'>Night</div>", unsafe_allow_html=True)
        night_value = st.number_input("", min_value=0, step=1, key=key_night, label_visibility='collapsed', value=None)
    return day_value, night_value

# Input fields for machines
col1, spacer, col2 = st.columns([2, 0.5, 2])  # Add spacing between the two columns
with col1:
    knitting_day, knitting_night = side_by_side_input("Knitting Machines", 'knit_day', 'knit_night')
    bulk_dye_day, bulk_dye_night = side_by_side_input("Bulk Dye Machines", 'bulk_day', 'bulk_night')
    sample_dye_day, sample_dye_night = side_by_side_input("Sample Dye Machines", 'sample_day', 'sample_night')
    dryers_day, dryers_night = side_by_side_input("Dryers", 'dryers_day', 'dryers_night')
    presetting_day, presetting_night = side_by_side_input("Presetting Machines", 'presetting_day', 'presetting_night')
with col2:
    chillers_day, chillers_night = side_by_side_input("Chillers", 'chill_day', 'chill_night')
    ahu_day, ahu_night = side_by_side_input("AHU", 'ahu_day', 'ahu_night')
    compressor_day, compressor_night = side_by_side_input("Compressors", 'comp_day', 'comp_night')
    luwa_day, luwa_night = side_by_side_input("Luwa", 'luwa_day', 'luwa_night')

st.write("---")

# Prediction Button
if st.button("Predict Consumption"):
    # Replace None values with 0 for missing inputs
    inputs = [
        knitting_day if knitting_day is not None else 0,
        knitting_night if knitting_night is not None else 0,
        bulk_dye_day if bulk_dye_day is not None else 0,
        bulk_dye_night if bulk_dye_night is not None else 0,
        sample_dye_day if sample_dye_day is not None else 0,
        sample_dye_night if sample_dye_night is not None else 0,
        dryers_day if dryers_day is not None else 0,
        dryers_night if dryers_night is not None else 0,
        presetting_day if presetting_day is not None else 0,
        presetting_night if presetting_night is not None else 0,
        chillers_day if chillers_day is not None else 0,
        chillers_night if chillers_night is not None else 0,
        ahu_day if ahu_day is not None else 0,
        ahu_night if ahu_night is not None else 0,
        compressor_day if compressor_day is not None else 0,
        compressor_night if compressor_night is not None else 0,
        luwa_day if luwa_day is not None else 0,
        luwa_night if luwa_night is not None else 0
    ]

    # Check if all inputs are 0
    if all(value == 0 for value in inputs):
        st.error("Please provide at least one non-zero input to make a prediction.")
    else:
        # Create DataFrame for input
        input_data = {
            'Knitting - D': [inputs[0]], 
            'Knitting - N': [inputs[1]], 
            'Bulk Dye - D': [inputs[2]], 
            'Bulk Dye - N': [inputs[3]], 
            'Sample Dye - D': [inputs[4]], 
            'Sample Dye - N': [inputs[5]], 
            'Dryers - D': [inputs[6]], 
            'Dryers - N': [inputs[7]], 
            'Presetting - D': [inputs[8]], 
            'Presetting - N': [inputs[9]], 
            'Chillers - D': [inputs[10]], 
            'Chillers - N': [inputs[11]], 
            'AHU - D': [inputs[12]], 
            'AHU - N': [inputs[13]], 
            'Compressor - D': [inputs[14]], 
            'Compressor - N': [inputs[15]], 
            'Luwa - D': [inputs[16]], 
            'Luwa - N': [inputs[17]]
        }
        input_df = pd.DataFrame(input_data)

        # Predict using the models
        electricity_pred = electricity_model.predict(input_df)
        steam_pred = steam_model.predict(input_df)
        water_pred = water_model.predict(input_df)

        # Save to Google Sheets
        save_to_google_sheet(inputs + [electricity_pred[0], steam_pred[0], water_pred[0]])

        # Display Predictions
        st.subheader("Predicted Consumption Results")
        st.write(f"**Electricity Consumption (kWh):** {electricity_pred[0]:.2f}")
        st.write(f"**Steam Consumption (kg):** {steam_pred[0]:.2f}")
        st.write(f"**Water Consumption (Cu.m.):** {water_pred[0]:.2f}")
