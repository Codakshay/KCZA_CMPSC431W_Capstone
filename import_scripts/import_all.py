import subprocess

import_scripts = [
    "import_addresses.py",
    "import_buyers.py",
    "import_categories.py",
    "import_credit_cards.py",
    "import_helpdesk.py",
    "import_listings.py",
    "import_orders.py",
    "import_requests.py",
    "import_reviews.py",
    "import_sellers.py",
    "import_users.py",
    "import_zipcode_info.py"
]

for script in import_scripts:
    subprocess.run(["python", script])
