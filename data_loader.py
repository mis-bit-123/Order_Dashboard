import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import numpy as np
import streamlit as st
import json

class OrderDataLoader:
    def __init__(self):
        self.df = None
        
    def _get_credentials(self):
        """Get Google credentials from HuggingFace secrets"""
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Load from HuggingFace Secrets
        try:
            service_account_info = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
            creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
            return creds
        except Exception as e:
            st.error(f"Credentials Error: {e}")
            return None
    
    def connect(self):
        """Connect to Google Sheets"""
        try:
            creds = self._get_credentials()
            if not creds:
                return None
            client = gspread.authorize(creds)
            return client
        except Exception as e:
            st.error(f"Connection Error: {e}")
            return None
    
    @st.cache_data(ttl=300)
    def fetch_data(_self):
        """Fetch data from Google Sheet"""
        try:
            client = _self.connect()
            if not client:
                return None
            
            # Get Sheet ID and Name from secrets
            sheet_id = st.secrets["SHEET_ID"]
            sheet_name = st.secrets["SHEET_NAME"]
                
            sheet = client.open_by_key(sheet_id)
            worksheet = sheet.worksheet(sheet_name)
            
            # Get all values
            all_values = worksheet.get_all_values()
            data_rows = all_values[1:]  # Skip header
            
            # Extract columns: A=0, B=1, D=3, G=6, H=7, I=8, O=14, S=18
            processed_data = []
            for row in data_rows:
                if len(row) >= 19:
                    try:
                        processed_data.append({
                            'Date': row[0],           # A: Timestamp
                            'Inquiry_No': row[1],     # B: Inquiry No
                            'Company': row[3],        # D: Company Name
                            'Product': row[6],        # G: Product Description
                            'Qty': row[7],            # H: Quantity
                            'State': row[8],          # I: State
                            'Total_Amount': row[14],  # O: Total Amount
                            'EDD': row[18]            # S: Delivery Date
                        })
                    except:
                        continue
            
            df = pd.DataFrame(processed_data)
            df = _self.clean_data(df)
            return df
            
        except Exception as e:
            st.error(f"Data Fetch Error: {e}")
            return None
    
    def clean_data(self, df):
        """Clean and format data"""
        if df.empty:
            return df
            
        # Clean Date
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce', dayfirst=True)
        
        # Clean Amount (remove ₹ and commas)
        df['Total_Amount'] = df['Total_Amount'].astype(str).str.replace(r'[₹,]', '', regex=True)
        df['Total_Amount'] = pd.to_numeric(df['Total_Amount'], errors='coerce')
        
        # Clean Quantity
        df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce').fillna(1)
        
        # Clean State
        df['State'] = df['State'].str.strip().str.title()
        df['State'] = df['State'].replace({'N/A': 'Not Specified', 'Na': 'Not Specified'})
        
        # Clean Product & Company
        df['Product'] = df['Product'].str.strip()
        df['Company'] = df['Company'].str.strip().str.title()
        
        # Process EDD
        df['EDD'] = pd.to_datetime(df['EDD'], errors='coerce', dayfirst=True)
        df['Lead_Time_Days'] = (df['EDD'] - df['Date']).dt.days
        
        # Add derived columns
        df['Year'] = df['Date'].dt.year
        df['Month'] = df['Date'].dt.month
        df['Month_Name'] = df['Date'].dt.month_name()
        
        # Remove invalid rows
        df = df.dropna(subset=['Date', 'Total_Amount'])
        
        return df
    
    def get_stats(self, df):
        """Calculate summary statistics"""
        if df is None or df.empty:
            return {}
            
        return {
            'total_orders': len(df),
            'total_revenue': df['Total_Amount'].sum(),
            'total_qty': df['Qty'].sum(),
            'avg_order': df['Total_Amount'].mean(),
            'top_state': df.groupby('State')['Total_Amount'].sum().idxmax() if not df.empty else "N/A",
            'date_range': {
                'start': df['Date'].min(),
                'end': df['Date'].max()
            }
        }
