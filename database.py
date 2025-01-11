import streamlit as st
import gspread
from datetime import datetime
import json

# Sheet configuration
SHEET_ID = "1x6EGxy5N5RmmKRS9A2UFKVNDU-1fugVSR4_k1Yk3_ao"  # Replace with your Google Sheet ID
from oauth2client.service_account import ServiceAccountCredentials

# Initialize Google Sheets connection
@st.cache_resource
def init_google_sheets():
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    try:
        credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        client = gspread.authorize(credentials)
        return client
    except Exception as e:
        st.error(f"ไม่สามารถเชื่อมต่อกับ Google Sheets ได้: {str(e)}")
        return None
   
def get_worksheet(name):
    try:
        sheet = st.session_state.client.open_by_key(SHEET_ID)
        try:
            return sheet.worksheet(name)
        except:
            return sheet.add_worksheet(name, 1000, 20)
    except Exception as e:
        st.error(f"ไม่สามารถเข้าถึงชีต {name} ได้: {str(e)}")
        return None

# Product Management Functions
def load_products():
    products_sheet = get_worksheet('shopproducts')
    if products_sheet:
        products = products_sheet.get_all_records()
        return products if products else []
    return []

def save_product(id,name, brand, price, image_url, qty):
    products_sheet = get_worksheet('shopproducts')
    if products_sheet:
        products_sheet.append_row([id,name, brand,float(price), image_url, qty])
        st.success(f"บันทึกสินค้า '{name}' เรียบร้อยแล้ว")

def update_product(row_idx, id,name, brand, price, image_url, qty):
    products_sheet =get_worksheet('shopproducts')
    if products_sheet:
        try:
            products_sheet.update(f'A{row_idx+2}:F{row_idx+2}', [[id,name, brand,float(price), image_url, qty]])
            st.success(f"อัพเดทสินค้า '{name}' เรียบร้อยแล้ว")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการอัพเดทสินค้า: {e}")

def delete_product(row_idx, products):  # Add products as an argument
    products_sheet = get_worksheet('shopproducts')
    if products_sheet:
        try:
            products_sheet.delete_rows(row_idx + 2)  # Add 2 to account for header row and 0-based index
            st.success("ลบสินค้าเรียบร้อยแล้ว")
            products.pop(row_idx)  # Remove the product from the list to avoid index issues
            return products # Return updated list
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการลบสินค้า: {e}")
            return products # Return original list if deletion fails

# Order Management Functions
def load_orders():
    orders_sheet = get_worksheet('shoporders')
    if orders_sheet:
        orders = orders_sheet.get_all_records()
        return orders if orders else []
    return []

def save_order(customer_name, items, total, special_instructions):
    orders_sheet = get_worksheet('shoporders')
    if orders_sheet:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        orders_sheet.append_row([
            timestamp,
            customer_name,
            json.dumps(items, ensure_ascii=False),
            total,
            special_instructions,
            'pending'
        ])
        st.success("บันทึกออเดอร์เรียบร้อยแล้ว")

def update_order(row_idx,qty):
    orders_sheet = get_worksheet('shoporders')
    if orders_sheet:
        try:
            orders_sheet.update(f'F{row_idx+2}', [[qty]])  # Wrap qty in a list of lists
            st.success("อัพเดทสถานะออเดอร์เรียบร้อยแล้ว")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการอัพเดทสถานะออเดอร์: {e}")
