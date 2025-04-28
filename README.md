# NittanyBusiness

NittanyBusiness is an online marketplace platform designed to connect small and medium-sized businesses (SMEs) with trusted suppliers. This prototype demonstrates key functionalities such as user management, category browsing, product listing, order management, review systems, and search functionality.

## Features

- **User Login:** Secure login for Buyers, Sellers, and HelpDesk Staff (passwords stored as hashes).
- **Category Hierarchy:** Dynamic browsing of product categories and subcategories.
- **Product Listing Management:** Sellers can publish, edit, and remove product listings.
- **Order Management:** Buyers can purchase products, with inventory updates and order tracking.
- **Product/Seller Review:** Buyers can rate and review products and sellers after purchase.
- **Product Search:** Buyers can search for products using keywords and price ranges.
- **User Registration:** New users can register as Buyers or Sellers (HelpDesk accounts managed separately).
- **User Profile Update:** Users can update their personal information and reset their passwords.
- **Helpdesk Support:** Helpdesk staff can complete requests like changing emails, etc.

## Prerequisites

- Python 3.9
- [Flask](https://flask.palletsprojects.com/)
- SQLite

## Installation

1. **Clone the Repository or Download the Files:**

   ```bash
   git clone https://github.com/Codakshay/KCZA_CMPSC431W_Capstone.git
   cd KCZA_CMPSC431W_Capstone
   
2. **Set up virtual environment and install dependencies**
    ```bash
   python -m venv .venv
    source .venv/bin/activate
   pip install flask
   
3. **Run the application and navigate to browser**
    ```bash
   python app.py
   
## File Structure

    ├── app.py                          # Main Flask application
    ├── import_scripts                  # contains import scripts for all tables
    │   └── NittanyBusinessDataset_v3   # CSV files for each table (one for each table)
    │   └── import_[table_name].py      # script for importing data from CSV file to the table (one script for each table)
    │   └── import_all.py               # script for running all import scripts
    ├── nittanybusiness.db              # SQLite database
    ├── templates                       # Folder for HTML templates
    │   └── index.html                  # HTML template for the main interface (login/registration)
    │   └── add_listing.html            # HTML template for adding a listing
    │   └── buyer_dashboard.html        # HTML template for the buyer dashboard
    │   └── categories.html             # HTML template for viewing categories and subcategories
    │   └── order_product.html          # HTML template for ordering a product
    │   └── product.html                # HTML template for product page
    │   └── profile.html                # HTML template for profile page
    │   └── request_email_change.html   # HTML template for requesting email change
    │   └── review_product.html         # HTML template for reviewing product
    │   └── search.html                 # HTML template for searching for products
    │   └── seller_dashboard.html       # HTML template for the seller dashboard
    │   └── support_request.html        # HTML template for support requests
    └── README.md                       # Project documentation

