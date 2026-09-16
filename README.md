🍞 AL Zamin Bakers & Fast Food — Order Automation System
A modern, multi‑page Streamlit dashboard designed to automate order entry, analytics, invoicing, and admin operations for AL Zamin Bakers & Fast Food.
Built with a clean orange/cream theme, multi‑item order extraction, and a fully editable confirmation workflow.

📦 Features
1. Smart Order Input (with Editable Review)
Extracts multi‑item orders from natural text

Lets the user edit & confirm before saving

Saves each item as its own row with a shared Order ID

Prevents accidental auto‑saving

Fully resets after confirmation

2. Daily Sales Report
Total revenue

Total orders

Total items sold

Payment breakdown

Clean charts and metrics

3. Item Analytics Dashboard
Top‑selling items

Revenue per item

Category performance (Fast Food, Bakery, Drinks, Others)

Demand trends

Revenue distribution charts

4. Customer Insights
Customer selector

Total orders

Total spend

Favorite items

Payment behavior

Full order history table

5. Invoice Generator
Printable invoice layout

Auto‑generated invoice number

Multi‑item invoice table

Downloadable PDF (if enabled)

Branded orange/cream design

6. Admin Panel
Full database view

Filters (Customer, Payment Status, Date Range)

Export filtered or full data

Unpaid orders summary

Maintenance tools (Clear, Refresh)

🎨 Brand Theme
The entire system uses a custom bakery/fast‑food aesthetic:

Primary Color: #f47b20 (Orange)

Secondary Color: Cream (#f1e4d8)

Rounded cards

Soft shadows

Emoji‑enhanced headers

Clean, friendly typography

🗂️ Project Structure
Code
/alzamin-order-automation
│ app.py
│ extract.py
│ requirements.txt
│ orders.xlsx   (auto-generated)
│
└── pages/
      1_📦_Order_Input.py
      2_📊_Daily_Sales_Report.py
      3_🍕_Item_Analytics.py
      4_👤_Customer_Insights.py
      5_🧾_Invoice_Generator.py
      6_⚙️_Admin_Panel.py
⚙️ Installation
Clone the repository:

Code
git clone https://github.com/YOUR_USERNAME/alzamin-order-automation.git
cd alzamin-order-automation
Install dependencies:

Code
pip install -r requirements.txt
Run the app:

Code
streamlit run app.py
🌐 Deployment (Streamlit Cloud)
Push the project to GitHub

Go to streamlit.io/cloud

Click New App

Select your repo

Set main file to app.py

Deploy

Streamlit Cloud will automatically install dependencies and host your app.

📊 Excel Schema
Each item in an order becomes its own row:

Column	Description
Order ID	Unique ID shared across all items in the same order
Customer	Customer name
Item	Item name
Quantity	Quantity ordered
Payment	Total payment for the order
Payment Status	paid / unpaid / pending
Timestamp	Date & time of order


This structure ensures accurate analytics and easy grouping.

🧠 Tech Stack
Python 3.x

Streamlit

Pandas

OpenPyXL

Custom NLP extraction logic

🥐 About
This system was built to modernize and automate order processing for AL Zamin Bakers & Fast Food, providing fast, reliable, and visually branded tools for daily operations.

📬 Contact
For improvements, issues, or collaboration, feel free to open an issue or reach out.
