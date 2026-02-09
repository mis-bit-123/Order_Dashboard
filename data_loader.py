import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import numpy as np
import streamlit as st
from config import SHEET_ID, SHEET_NAME, CREDENTIALS_FILE, BRUSH_SHEET_NAME

class OrderDataLoader:
    def __init__(self):
        self.df = None
        
    def connect(self):
        """Connect to Google Sheets"""
        try:
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scope)
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
                
            sheet = client.open_by_key(SHEET_ID)
            worksheet = sheet.worksheet(SHEET_NAME)
            
            # Get all values
            all_values = worksheet.get_all_values()
            data_rows = all_values[1:]  # Skip header
            
            # Extract columns: A=0, B=1, D=3, E=4, G=6, H=7, I=8, O=14, S=18
            processed_data = []
            for row in data_rows:
                if len(row) >= 19:
                    try:
                        processed_data.append({
                            'Date': row[0],           # A: Timestamp
    'Inquiry_No': row[1],     # B: Inquiry No
    'Company': row[3],        # D: Company Name
    'Client_Name': row[5],    # F: Client Name ✅ Correct
    'Product': row[6],        # G: Product Description
    'Qty': row[7],            # H: Quantity
    'City': row[8],           # I: City ✅ Was 9, now 8
    'State': row[9],          # J: State ✅ Was 8, now 9
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
        df['State'] = df['State'].replace({'N/A': 'Not Specified', 'Na': 'Not Specified', '': 'Not Specified'})
        
        # Clean Product & Company & Client
        df['Product'] = df['Product'].str.strip()
        df['Company'] = df['Company'].str.strip().str.title()
        df['Client_Name'] = df['Client_Name'].str.strip().str.title()
        
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
    
    # ==================== BRUSH/SWEEPER/BROOMER FUNCTIONALITY ====================
    
    def identify_brush_products(self, df):
        """Identify products containing Broomer, Sweeper, or Brush"""
        if df is None or df.empty:
            return pd.DataFrame()
        
        # Case-insensitive search for keywords
        keywords = ['broomer', 'sweeper', 'brush']
        pattern = '|'.join(keywords)
        
        mask = df['Product'].str.contains(pattern, case=False, na=False)
        brush_df = df[mask].copy()
        
        return brush_df
    
    def calculate_followup_dates(self, brush_df):
        """Calculate follow-up dates (Purchase Date + 3 months)"""
        if brush_df.empty:
            return brush_df
        
        # Add 3 months (90 days approximation) to purchase date
        brush_df = brush_df.copy()
        brush_df['Follow_Up_Date'] = brush_df['Date'] + pd.DateOffset(days=90)
        brush_df['Days_Until_Followup'] = (brush_df['Follow_Up_Date'] - pd.Timestamp.now()).dt.days
        
        # Categorize urgency
        def categorize_urgency(days):
            if days < 0:
                return '🔴 Overdue'
            elif days <= 7:
                return '🟠 Due This Week'
            elif days <= 30:
                return '🟡 Due This Month'
            else:
                return '🟢 Future'
        
        brush_df['Urgency'] = brush_df['Days_Until_Followup'].apply(categorize_urgency)
        
        return brush_df
    
    def get_brush_summary_stats(self, brush_df):
        """Calculate summary statistics for brush products"""
        if brush_df.empty:
            return {}
        
        total_units = len(brush_df)
        total_revenue = brush_df['Total_Amount'].sum()
        unique_companies = brush_df['Company'].nunique()
        unique_states = brush_df['State'].nunique()
        
        # Urgency breakdown
        urgency_counts = brush_df['Urgency'].value_counts().to_dict()
        
        # Products breakdown
        product_counts = brush_df['Product'].value_counts().head(5).to_dict()
        
        # Upcoming follow-ups (next 30 days)
        upcoming = brush_df[brush_df['Days_Until_Followup'] <= 30]
        
        return {
            'total_units': total_units,
            'total_revenue': total_revenue,
            'unique_companies': unique_companies,
            'unique_states': unique_states,
            'urgency_counts': urgency_counts,
            'top_products': product_counts,
            'upcoming_count': len(upcoming),
            'overdue_count': len(brush_df[brush_df['Days_Until_Followup'] < 0])
        }
    
    def store_to_brush_sheet(self, brush_df, client_email=None):
        """Store brush data to Brommer Brush Data sheet"""
        try:
            client = self.connect()
            if not client:
                return False, "Connection failed"
            
            # Open the spreadsheet
            sheet = client.open_by_key(SHEET_ID)
            
            # Try to get or create the worksheet
            try:
                worksheet = sheet.worksheet(BRUSH_SHEET_NAME)
                # Clear existing data if updating
                worksheet.clear()
            except gspread.WorksheetNotFound:
                # Create new worksheet
                worksheet = sheet.add_worksheet(title=BRUSH_SHEET_NAME, rows=1000, cols=20)
            
            # Prepare data for storage
            storage_df = brush_df[[
                'Date', 'Inquiry_No', 'Company', 'Client_Name', 'Product', 
                'Qty', 'State', 'City', 'Total_Amount', 'Follow_Up_Date', 'Urgency'
            ]].copy()
            
            # Format dates
            storage_df['Date'] = storage_df['Date'].dt.strftime('%d-%m-%Y')
            storage_df['Follow_Up_Date'] = storage_df['Follow_Up_Date'].dt.strftime('%d-%m-%Y')
            
            # Add metadata
            storage_df['Last_Updated'] = pd.Timestamp.now().strftime('%d-%m-%Y %H:%M')
            storage_df['Data_Source'] = 'Order Confirmation Automation'
            
            # Prepare headers and values
            headers = [
                'Purchase Date', 'Inquiry No', 'Company Name', 'Client Name', 'Product',
                'Quantity', 'City', 'State', 'Total Amount (₹)', 'Follow Up Date', 
                'Urgency Status', 'Last Updated', 'Data Source'
            ]
            
            values = [headers] + storage_df.values.tolist()
            
            # Update worksheet
            worksheet.update(values, value_input_option='RAW')
            
            # Formatt header row (make it bold)
            worksheet.format('A1:M1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.6}
            })
            
            # Auto-resize columns
            for i, header in enumerate(headers, 1):
                col_letter = chr(64 + i) if i <= 26 else 'A' + chr(64 + i - 26)
                worksheet.format(f'{col_letter}1:{col_letter}{len(values)}', {
                    'wrapStrategy': 'WRAP',
                    'verticalAlignment': 'MIDDLE'
                })
            
            return True, f"Successfully stored {len(storage_df)} records to {BRUSH_SHEET_NAME}"
            
        except Exception as e:
            return False, f"Error storing data: {str(e)}"
    
    def fetch_existing_brush_data(self):
        """Fetch existing data from Brush Data sheet"""
        try:
            client = self.connect()
            if not client:
                return None
            
            sheet = client.open_by_key(SHEET_ID)
            worksheet = sheet.worksheet(BRUSH_SHEET_NAME)
            
            data = worksheet.get_all_records()
            if data:
                return pd.DataFrame(data)
            return pd.DataFrame()
            
        except gspread.WorksheetNotFound:
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Error fetching brush data: {e}")
            return None
