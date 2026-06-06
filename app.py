import streamlit as st
import os
from datetime import datetime
from fpdf import FPDF
import base64

# Get the current folder path
CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(CURRENT_FOLDER, "inventory.txt")

def load_inventory():
    """Load inventory from file"""
    inventory = {}
    try:
        if os.path.exists(FILE_PATH):
            with open(FILE_PATH, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.split(',')
                        if len(parts) == 3:
                            name = parts[0]
                            qty = int(parts[1])
                            price = float(parts[2])
                            inventory[name] = (qty, price)
        else:
            # Create empty file if doesn't exist
            with open(FILE_PATH, 'w', encoding='utf-8') as f:
                pass
    except Exception as e:
        st.error(f"Error loading: {e}")
    return inventory

def save_inventory(inventory):
    """Save inventory to file"""
    try:
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            for name, (qty, price) in inventory.items():
                f.write(f"{name},{qty},{price}\n")
        return True
    except Exception as e:
        st.error(f"Error saving: {e}")
        return False

def generate_pdf_receipt(receipt_data, total_amount):
    """Generate PDF receipt and return as bytes"""
    pdf = FPDF()
    pdf.add_page()
    
    # Add a Unicode font that supports special characters
    pdf.add_font('dejavu', '', 'DejaVuSansCondensed.ttf', uni=True)
    pdf.set_font('dejavu', '', 12)
    
    # Header
    pdf.set_font('dejavu', '', 20)
    pdf.cell(0, 10, "INVENTORY STORES", ln=True, align='C')
    pdf.set_font('dejavu', '', 12)
    pdf.cell(0, 6, "Your billing partner", ln=True, align='C')
    pdf.cell(0, 6, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
    pdf.line(10, 40, 200, 40)
    
    # Receipt title
    pdf.ln(10)
    pdf.set_font('dejavu', '', 16)
    pdf.cell(0, 10, "SALES RECEIPT", ln=True, align='C')
    pdf.ln(5)
    
    # Column headers
    pdf.set_font('dejavu', '', 10)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(80, 8, "Item", 1, 0, 'C', True)
    pdf.cell(30, 8, "Quantity", 1, 0, 'C', True)
    pdf.cell(40, 8, "Unit Price (Rs.)", 1, 0, 'C', True)
    pdf.cell(40, 8, "Total (Rs.)", 1, 1, 'C', True)
    
    # Items
    pdf.set_font('dejavu', '', 10)
    for item in receipt_data:
        pdf.cell(80, 8, item['Item'], 1, 0, 'L')
        pdf.cell(30, 8, str(item['Qty']), 1, 0, 'C')
        pdf.cell(40, 8, f"{item['Price']:.2f}", 1, 0, 'R')
        pdf.cell(40, 8, f"{item['Subtotal']:.2f}", 1, 1, 'R')
    
    # Total
    pdf.ln(5)
    pdf.set_font('dejavu', '', 12)
    pdf.cell(150, 8, "TOTAL AMOUNT:", 0, 0, 'R')
    pdf.set_font('dejavu', '', 14)
    pdf.cell(40, 8, f"Rs. {total_amount:.2f}", 0, 1, 'R')
    
    # Footer
    pdf.ln(15)
    pdf.set_font('dejavu', '', 10)
    pdf.cell(0, 6, "Thank you for shopping with us!", ln=True, align='C')
    pdf.cell(0, 6, "Visit Again!", ln=True, align='C')
    pdf.cell(0, 6, "Arham Inventory System", ln=True, align='C')
    
    # Return PDF as bytes
    return pdf.output(dest='S').encode('latin1')

def get_download_link(pdf_bytes, filename):
    """Generate HTML download link for PDF"""
    b64 = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">📥 Click here to download PDF Receipt</a>'
    return href

# Initialize session state
if 'inventory' not in st.session_state:
    st.session_state.inventory = load_inventory()
if 'cart' not in st.session_state:
    st.session_state.cart = {}
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = None
if 'show_receipt' not in st.session_state:
    st.session_state.show_receipt = False
if 'last_receipt' not in st.session_state:
    st.session_state.last_receipt = None
if 'last_receipt_total' not in st.session_state:
    st.session_state.last_receipt_total = 0

# Page config
st.set_page_config(
    page_title="Awais Inventory System",
    page_icon="📦",
    layout="wide"
)

# Title
st.title("📦 Awais Inventory Management System")
st.markdown("---")

# Show current file location (for debugging)
with st.expander("ℹ️ System Info"):
    st.write(f"**File Location:** `{FILE_PATH}`")
    st.write(f"**File Exists:** {os.path.exists(FILE_PATH)}")
    if os.path.exists(FILE_PATH):
        st.success("✅ Inventory file found!")

# Role Selection
st.subheader("Select Your Role")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button(" 🔑Owner", use_container_width=True):
        st.session_state.logged_in = "owner"
        st.session_state.show_receipt = False
with col2:
    if st.button("💻🖋 Cashier", use_container_width=True):
        st.session_state.logged_in = "cashier"
        st.session_state.show_receipt = False
with col3:
    if st.button("🛒👨🏽‍💼 Customer", use_container_width=True):
        st.session_state.logged_in = "customer"
        st.session_state.show_receipt = False

st.markdown("---")

# ==================== OWNER SECTION ====================
if st.session_state.logged_in == "owner":
    st.header("👑 Owner Portal")
    
    password = st.text_input("Enter Owner Password:", type="password")
    
    if password == "267":
        st.success("✅ Access Granted!")
        
        # Owner menu
        menu = st.selectbox(
            "Select Action:",
            ["View Inventory", "Add New Item", "Add Quantity", "Update Price", "Remove Item", "Remove Quantity", "Logout"]
        )
        
        inv = st.session_state.inventory
        
        if menu == "View Inventory":
            st.subheader("📋 Current Inventory")
            if inv:
                data = []
                for item, (qty, price) in inv.items():
                    status = "🟢 In Stock" if qty > 0 else "🔴 Out of Stock"
                    data.append({
                        "Item": item,
                        "Quantity": qty,
                        "Status": status,
                        "Price": f"Rs. {price:.2f}"
                    })
                st.table(data)
            else:
                st.info("No items in inventory")
        
        elif menu == "Add New Item":
            st.subheader("➕ Add New Item")
            col1, col2 = st.columns(2)
            with col1:
                new_item = st.text_input("Item Name:").strip()
            with col2:
                new_price = st.number_input("Price (Rs.):", min_value=0.0, step=10.0)
            new_qty = st.number_input("Initial Quantity:", min_value=0, step=1)
            
            if st.button("💾 Add Item", type="primary"):
                if not new_item:
                    st.error("Please enter item name")
                elif new_item in inv:
                    st.error("Item already exists!")
                else:
                    inv[new_item] = (new_qty, new_price)
                    if save_inventory(inv):
                        st.success(f"✅ {new_item} added successfully!")
                        st.rerun()
        
        elif menu == "Add Quantity":
            st.subheader("📦 Add Stock")
            if inv:
                item = st.selectbox("Select Item:", list(inv.keys()))
                current_qty = inv[item][0]
                st.info(f"Current quantity: {current_qty}")
                add_qty = st.number_input("Quantity to add:", min_value=1, step=1)
                
                if st.button("➕ Add Stock", type="primary"):
                    new_qty = current_qty + add_qty
                    inv[item] = (new_qty, inv[item][1])
                    if save_inventory(inv):
                        st.success(f"✅ Added {add_qty} units to {item}")
                        st.rerun()
            else:
                st.warning("No items found")
        
        elif menu == "Update Price":
            st.subheader("💰 Update Price")
            if inv:
                item = st.selectbox("Select Item:", list(inv.keys()))
                current_price = inv[item][1]
                new_price = st.number_input("New Price (Rs.):", min_value=0.0, value=current_price, step=10.0)
                
                if st.button("💲 Update Price", type="primary"):
                    inv[item] = (inv[item][0], new_price)
                    if save_inventory(inv):
                        st.success(f"✅ Price updated for {item}")
                        st.rerun()
            else:
                st.warning("No items found")
        
        elif menu == "Remove Item":
            st.subheader("🗑️ Remove Item")
            if inv:
                item = st.selectbox("Select Item to Remove:", list(inv.keys()))
                if st.button("🗑️ Remove Permanently", type="secondary"):
                    del inv[item]
                    if save_inventory(inv):
                        st.success(f"✅ {item} removed from inventory")
                        st.rerun()
            else:
                st.warning("No items found")
        
        elif menu == "Remove Quantity":
            st.subheader("📉 Remove Stock")
            if inv:
                item = st.selectbox("Select Item:", list(inv.keys()))
                current_qty = inv[item][0]
                if current_qty > 0:
                    st.info(f"Current quantity: {current_qty}")
                    remove_qty = st.number_input("Quantity to remove:", min_value=1, max_value=current_qty, step=1)
                    
                    if st.button("➖ Remove Stock", type="secondary"):
                        new_qty = current_qty - remove_qty
                        inv[item] = (new_qty, inv[item][1])
                        if save_inventory(inv):
                            st.success(f"✅ Removed {remove_qty} units from {item}")
                            st.rerun()
                else:
                    st.warning("Item is out of stock")
            else:
                st.warning("No items found")
        
        elif menu == "Logout":
            st.session_state.logged_in = None
            st.rerun()
    
    elif password:
        st.error("❌ Wrong password!")

# ==================== CASHIER SECTION ====================
elif st.session_state.logged_in == "cashier":
    st.header("💵 Cashier Portal")
    
    password = st.text_input("Enter Cashier Password:", type="password")
    
    if password == "2003":
        st.success("✅ Access Granted!")
        
        menu = st.radio("Select Option:", ["View Inventory", "Generate Bill", "Logout"])
        
        inv = st.session_state.inventory
        
        if menu == "View Inventory":
            st.subheader("📋 Inventory Status")
            if inv:
                data = []
                for item, (qty, price) in inv.items():
                    status = "Available" if qty > 0 else "Out of Stock"
                    data.append({
                        "Item": item,
                        "Stock": qty,
                        "Status": status,
                        "Price": f"Rs. {price:.2f}"
                    })
                st.table(data)
            else:
                st.info("No items")
        
        elif menu == "Generate Bill":
            st.subheader("🧾 Billing System")
            
            # Show receipt if it was just generated
            if st.session_state.show_receipt and st.session_state.last_receipt:
                st.success("✅ Transaction Complete!")
                
                # Display receipt in Streamlit
                with st.container():
                    st.markdown("---")
                    st.subheader("📄 RECEIPT")
                    st.markdown(f"**Date & Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    st.markdown("---")
                    
                    for item in st.session_state.last_receipt:
                        st.write(f"**{item['Item']}**")
                        st.write(f"  Quantity: {item['Qty']} x Rs. {item['Price']:.2f} = Rs. {item['Subtotal']:.2f}")
                    
                    st.markdown("---")
                    st.markdown(f"## **TOTAL: Rs. {st.session_state.last_receipt_total:.2f}**")
                    st.markdown("---")
                    st.markdown("**Thank you for shopping with us!**")
                    st.balloons()
                
                # Generate PDF and provide download button
                try:
                    pdf_bytes = generate_pdf_receipt(st.session_state.last_receipt, st.session_state.last_receipt_total)
                    st.markdown("---")
                    st.markdown("### 💾 Save Receipt")
                    
                    # Create download button
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"receipt_{timestamp}.pdf"
                    
                    st.download_button(
                        label="📄 Download PDF Receipt",
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf",
                        type="primary"
                    )
                    
                    st.info("💡 Click the button above to save the receipt as PDF")
                    
                except Exception as e:
                    st.error(f"Error generating PDF: {e}")
                    st.info("You can still see the receipt on screen")
                
                # New bill button
                if st.button("🔄 Start New Bill", type="secondary"):
                    st.session_state.show_receipt = False
                    st.session_state.last_receipt = None
                    st.rerun()
                
                st.markdown("---")
            
            # Show billing interface only if not showing receipt
            if not st.session_state.show_receipt:
                # Show available items
                available_items = {item: (qty, price) for item, (qty, price) in inv.items() if qty > 0}
                
                if available_items:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        item = st.selectbox("Select Product:", list(available_items.keys()))
                        item_qty, item_price = available_items[item]
                        st.info(f"Available: {item_qty} units | Price: Rs. {item_price:.2f}")
                    
                    with col2:
                        quantity = st.number_input("Quantity:", min_value=1, max_value=item_qty, step=1)
                    
                    if st.button("➕ Add to Bill", type="primary"):
                        if quantity <= item_qty:
                            st.session_state.cart[item] = st.session_state.cart.get(item, 0) + quantity
                            st.success(f"✅ Added {quantity}x {item}")
                            st.rerun()
                        else:
                            st.error("Not enough stock!")
                    
                    # Show current bill
                    if st.session_state.cart:
                        st.markdown("---")
                        st.subheader("🧾 Current Bill")
                        
                        bill_items = []
                        total = 0
                        
                        for item, qty in st.session_state.cart.items():
                            price = inv[item][1]
                            subtotal = qty * price
                            total += subtotal
                            bill_items.append({
                                "Item": item,
                                "Qty": qty,
                                "Price": f"Rs. {price:.2f}",
                                "Subtotal": f"Rs. {subtotal:.2f}"
                            })
                        
                        st.table(bill_items)
                        st.metric("💰 Total Amount", f"Rs. {total:.2f}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Checkout & Print Bill", type="primary"):
                                # Save receipt data before clearing
                                receipt_data = []
                                for item, qty in st.session_state.cart.items():
                                    price = inv[item][1]
                                    receipt_data.append({
                                        "Item": item,
                                        "Qty": qty,
                                        "Price": price,
                                        "Subtotal": qty * price
                                    })
                                
                                # Update inventory
                                for item, qty in st.session_state.cart.items():
                                    new_qty = inv[item][0] - qty
                                    inv[item] = (new_qty, inv[item][1])
                                
                                if save_inventory(inv):
                                    # Store receipt in session state
                                    st.session_state.last_receipt = receipt_data
                                    st.session_state.last_receipt_total = total
                                    st.session_state.show_receipt = True
                                    st.session_state.cart = {}
                                    st.rerun()
                        
                        with col2:
                            if st.button("🗑️ Clear Bill"):
                                st.session_state.cart = {}
                                st.rerun()
                else:
                    st.warning("No items available for sale")
        
        elif menu == "Logout":
            st.session_state.logged_in = None
            st.session_state.show_receipt = False
            st.session_state.cart = {}
            st.rerun()
    
    elif password:
        st.error("❌ Wrong password!")

# ==================== CUSTOMER SECTION ====================
elif st.session_state.logged_in == "customer":
    st.header("🛒 Customer Storefront")
    
    st.subheader("Thank you for choosing us!")
    st.markdown("**Available Items:**")
    
    inv = st.session_state.inventory
    
    if inv:
        # Create columns for display
        cols = st.columns(3)
        item_list = list(inv.items())
        
        for idx, (item, (qty, price)) in enumerate(item_list):
            with cols[idx % 3]:
                if qty > 0:
                    st.success(f"✅ **{item}**")
                    st.write(f"💰 Price: **Rs. {price:.2f}**")
                    st.write(f"📦 Available: {qty} units")
                else:
                    st.error(f"❌ **{item}**")
                    st.write(f"💰 Price: Rs. {price:.2f}")
                    st.write(f"🚫 Out of Stock")
                st.markdown("---")
    else:
        st.info("No items available at the moment")
    
    if st.button("🔙 Back to Main Menu"):
        st.session_state.logged_in = None
        st.rerun()

# Footer
st.markdown("---")
st.markdown("### Awais Inventory Management System")
st.markdown("*Your trusted inventory partner*")