# python -m streamlit run "C:\Users\AMRUTHA PR\PycharmProjects\PythonProject\projectsample\sample2.py"


import streamlit as st
from datetime import datetime,date
import csv
st.set_page_config(
    page_title="Warehouse Stock & Logistics Management System",
    layout="wide",
    page_icon="🏭")

# Custom background and style
st.markdown("""
    <style>
    body {background-color: #f0f4f8; color: #1a1a1a;}
    .stApp {background: linear-gradient(to bottom right, #e9f1f7, #ffffff);}
    .stButton>button {background-color: #004c91; color: white; border-radius: 8px; height: 2.5em; width: 100%;}
    .stButton>button:hover { background-color: #0078d7; color: white;}
    .low-stock {
        background-color: #fff3cd;
        color: #856404;
        padding: 6px;
        border-radius: 5px;
        font-weight: 600;
    }
    .critical-stock { background-color: #f8d7da; color: #721c24; padding: 6px; border-radius: 5px; font-weight: 600;}
    </style>
""", unsafe_allow_html=True)

# Compatibility for old/new rerun
if not hasattr(st, "rerun"):
    st.rerun = st.experimental_rerun


# CSV helper functions
def load_csv(file, fieldnames):
    try:
        with open(file, "r", newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        return []
def save_csv(file, data, fieldnames):
    clean_data = [{k: v for k, v in row.items() if k in fieldnames} for row in data]
    with open(file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(clean_data)

# Initialize session state
if "users" not in st.session_state:
    st.session_state.users = load_csv("users.csv", ["username", "password", "warehouse", "role"])
    if not st.session_state.users:
        st.session_state.users = [{
            "username": "admin", "password": "1234",
            "warehouse": "Admin WH", "role": "superadmin"}]
        save_csv("users.csv", st.session_state.users, ["username", "password", "warehouse", "role"])
if "warehouses" not in st.session_state:
    st.session_state.warehouses = load_csv("warehouses.csv", ["name", "location"])
    if not any(w.get("name") == "Admin WH" for w in st.session_state.warehouses):
        st.session_state.warehouses.append({"name": "Admin WH", "location": "HQ"})
        save_csv("warehouses.csv", st.session_state.warehouses, ["name", "location"])


if "products" not in st.session_state:
    st.session_state.products = load_csv("products.csv", ["sku", "name", "category", "supplier", "unit"])
if "inventory" not in st.session_state:
    st.session_state.inventory = load_csv("inventory.csv", ["product", "warehouse", "qty"])
if "shipments" not in st.session_state:
    st.session_state.shipments = load_csv("shipments.csv", ["no", "product", "from", "qty", "address", "date", "status"])
if "transfers" not in st.session_state:
    st.session_state.transfers = load_csv("transfers.csv", ["product", "from", "to", "qty", "status", "time", "approved"])
if "logged_user" not in st.session_state:
    st.session_state.logged_user = None


# Utility functions
def find_inventory(product, warehouse):
    for inv in st.session_state.inventory:
        if inv.get("product") == product and inv.get("warehouse") == warehouse:
            return inv
    return None
def change_inventory(product, warehouse, delta):
    inv = find_inventory(product, warehouse)
    if inv:
        new_qty = int(inv.get("qty", 0)) + delta
        if new_qty < 0:
            return False, "Not enough stock"
        inv["qty"] = str(new_qty)
        return True, "Updated"
    else:
        if delta < 0:
            return False, "No stock available"
        st.session_state.inventory.append({"product": product, "warehouse": warehouse, "qty": str(delta)})
        return True, "Added"


def save_all():
    save_csv("users.csv", st.session_state.users, ["username", "password", "warehouse", "role"])
    save_csv("warehouses.csv", st.session_state.warehouses, ["name", "location"])
    save_csv("products.csv", st.session_state.products, ["sku", "name", "category", "supplier", "unit"])
    save_csv("inventory.csv", st.session_state.inventory, ["product", "warehouse", "qty"])
    save_csv("shipments.csv", st.session_state.shipments, ["no", "product", "from", "qty", "address", "date", "status"])
    save_csv("transfers.csv", st.session_state.transfers, ["product", "from", "to", "qty", "status", "time", "approved"])

# Login & Registration
def login_register_ui():
    st.title("🏭 Warehouse Stock & Logistics System")
    st.markdown("Manage products, stock, transfers, and shipments across multiple warehouses efficiently.")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Welcome to the System")
        st.info("Login below or register a new warehouse admin from the sidebar.")
    with col2:
        try:
            st.image("C:\\Users\\AMRUTHA PR\\OneDrive\\Pictures\\warehouse.image 3.png", use_container_width=True)
        except:
            st.warning("⚠️ Warehouse image not found.")


# Sidebar login
    st.sidebar.title("🔐 Login / Register")
    username = st.sidebar.text_input("Username", key="login_username")
    password = st.sidebar.text_input("Password", type="password", key="login_password")
    if st.sidebar.button("Login", key="login_button"):
        user = next((u for u in st.session_state.users
                     if u.get("username") == username and u.get("password") == password), None)
        if user:
            st.session_state.logged_user = user
            st.rerun()
        else:
            st.sidebar.error("Invalid credentials!")

# Registration
    st.sidebar.markdown("---")
    st.sidebar.subheader("Register New Warehouse + Admin")
    new_wh = st.sidebar.text_input("Warehouse Name", key="reg_wh_name")
    new_loc = st.sidebar.text_input("Location", key="reg_location")
    new_user = st.sidebar.text_input("Admin Username", key="reg_username")
    new_pass = st.sidebar.text_input("Admin Password", type="password", key="reg_password")
    if st.sidebar.button("Register Warehouse", key="reg_button"):
        if not new_wh or not new_user or not new_pass:
            st.sidebar.error("All fields required.")
        elif any(w.get("name") == new_wh for w in st.session_state.warehouses):
            st.sidebar.error("Warehouse already exists.")
        elif any(u.get("username") == new_user for u in st.session_state.users):
            st.sidebar.error("Username taken.")
        else:
            st.session_state.warehouses.append({"name": new_wh, "location": new_loc})
            st.session_state.users.append({"username": new_user,"password": new_pass,"warehouse": new_wh,"role": "admin"})
            save_all()
            st.sidebar.success("Warehouse + Admin registered successfully!")


# Pages
def dashboard_page():
    user = st.session_state.logged_user
    st.header("📊 Dashboard")
    if user.get("role") == "superadmin":
        st.subheader("All Warehouses Inventory Overview")
        st.dataframe(st.session_state.inventory)
    else:
        user_wh = user.get("warehouse", "")
        st.subheader(f"Inventory in {user_wh}")
        inv = [i for i in st.session_state.inventory if i.get("warehouse") == user_wh]
        st.dataframe(inv)

# Low stock visual alerts
        st.subheader("Low Stock Alerts (≤5)")
        for item in inv:
            qty = int(item.get("qty", 0))
            if qty <= 2:
                st.markdown(f"<div class='critical-stock'>🚨 Critical: {item['product']} — {qty} left</div>", unsafe_allow_html=True)
            elif qty <= 5:
                st.markdown(f"<div class='low-stock'>⚠️ Low: {item['product']} — {qty} left</div>", unsafe_allow_html=True)

# Pending transfers
        st.subheader("Pending Transfer Requests")
        pend = [t for t in st.session_state.transfers if t.get("to") == user_wh and t.get("approved") == "No"]
        if pend:
            for i, t in enumerate(pend):
                st.write(f"Request: {t.get('qty')} {t.get('product')} from {t.get('from')}")
                if st.button(f"Approve {i}"):
                    ok, _ = change_inventory(t.get('product'), user_wh, int(t.get('qty', 0)))
                    if ok:
                        t["approved"] = "Yes"
                        t["status"] = "Completed"
                        save_all()
                        st.success("Transfer approved.")
                        st.rerun()

def products_page():
    st.header("📦 Products")
    sku = st.text_input("SKU")
    name = st.text_input("Name")
    cat = st.text_input("Category")
    sup = st.text_input("Supplier")
    unit = st.text_input("Unit", value="pcs")
    if st.button("Add Product"):
        st.session_state.products.append({"sku": sku, "name": name, "category": cat, "supplier": sup, "unit": unit})
        save_all()
        st.success("✅ Product added successfully.")
    st.subheader("Product List")
    st.dataframe(st.session_state.products)

def inventory_page():
    st.header("📋 Inventory Management")
    user_wh = st.session_state.logged_user.get("warehouse", "")
    p = st.selectbox("Select Product", [x.get("name") for x in st.session_state.products])
    q = st.number_input("Quantity", min_value=0, step=1)
    if st.button("Set Inventory"):
        inv = find_inventory(p, user_wh)
        if inv:
            inv["qty"] = str(q)
        else:
            st.session_state.inventory.append({"product": p, "warehouse": user_wh, "qty": str(q)})
        save_all()
        st.success("Inventory updated.")
    st.subheader(f"Current Inventory for {user_wh}")
    st.dataframe([i for i in st.session_state.inventory if i.get("warehouse") == user_wh])

def transfers_page():
    st.header("🔄 Stock Transfers")
    user_wh = st.session_state.logged_user.get("warehouse", "")
    p = st.selectbox("Product", [x.get("name") for x in st.session_state.products])
    direction = st.radio("Direction", ["Request to my warehouse", "Send from my warehouse"])
    other_wh = [w.get("name") for w in st.session_state.warehouses if w.get("name") != user_wh]
    if direction == "Request to my warehouse":
        from_wh = st.selectbox("From Warehouse", other_wh)
        to_wh = user_wh
    else:
        from_wh = user_wh
        to_wh = st.selectbox("To Warehouse", other_wh)
    qty = st.number_input("Quantity", min_value=1, step=1)
    if st.button("Submit Transfer"):
        inv_from = find_inventory(p, from_wh)
        if not inv_from or int(inv_from.get("qty", 0)) < qty:
            st.error("❌ Not enough stock.")
        else:
            inv_from["qty"] = str(int(inv_from.get("qty", 0)) - qty)
            st.session_state.transfers.append({"product": p, "from": from_wh, "to": to_wh,
                "qty": str(qty), "status": "Requested", "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "approved": "No"})
            save_all()
            st.success(f"✅ Transfer request created: {qty} {p} from {from_wh} to {to_wh}")
    st.subheader("All Transfers")
    st.dataframe(st.session_state.transfers)

def shipments_page():
    st.header("🚚 Shipments")
    user_wh = st.session_state.logged_user.get("warehouse", "")
    s_no = st.text_input("Shipment No")
    p = st.selectbox("Product", [x.get("name") for x in st.session_state.products])
    qty = st.number_input("Quantity", min_value=1, step=1)
    addr = st.text_input("Destination")
    d = st.date_input("Date", value=date.today())
    if st.button("Create Shipment"):
        ok, msg = change_inventory(p, user_wh, -qty)
        if ok:
            st.session_state.shipments.append({
                "no": s_no, "product": p, "from": user_wh,
                "qty": str(qty), "address": addr, "date": str(d), "status": "Shipped"})
            save_all()
            st.success("✅ Shipment created.")
        else:
            st.error(msg)
    st.subheader("Shipments from your warehouse")
    st.dataframe([s for s in st.session_state.shipments if s.get("from") == user_wh])

def reports_page():
    st.header("📈 Reports")
    user_wh = st.session_state.logged_user.get("warehouse", "")
    st.subheader("Inventory")
    st.dataframe([i for i in st.session_state.inventory if i.get("warehouse") == user_wh])
    st.subheader("Transfers")
    st.dataframe([t for t in st.session_state.transfers if t.get("from") == user_wh or t.get("to") == user_wh])
    st.subheader("Shipments")
    st.dataframe([s for s in st.session_state.shipments if s.get("from") == user_wh])


# Main
def main():
    login_register_ui()
    if st.session_state.logged_user is None:
        return
    user = st.session_state.logged_user
    st.sidebar.markdown(f"👤 **User:** {user.get('username')}  \n🏢 **Warehouse:** {user.get('warehouse')}  \n🎯 **Role:** {user.get('role')}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_user = None
        st.rerun()

    menu = st.sidebar.radio("Navigation", ["Dashboard", "Products", "Inventory", "Transfers", "Shipments", "Reports"])
    if menu == "Dashboard": dashboard_page()
    elif menu == "Products": products_page()
    elif menu == "Inventory": inventory_page()
    elif menu == "Transfers": transfers_page()
    elif menu == "Shipments": shipments_page()
    elif menu == "Reports": reports_page()

if __name__ == "__main__":
    main()
