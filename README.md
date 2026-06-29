# BazaarX

A fully working e-commerce web app built with Django. Customers can shop, sellers can list products, and there's a custom admin panel to manage the whole thing. No templates bought, no shortcuts — built from scratch.


## Why I Built This

I wanted to build something that actually feels like a real product, not just a CRUD app. So I added things like OTP-based registration, Razorpay payments, a loyalty points system, PDF invoice downloads, coupon codes, wishlists, product comparison, return requests, and a custom admin dashboard — all in one project.

It's not perfect, but it works end to end.



## What You Can Do

**As a customer:**
- Sign up and verify your email with an OTP before your account goes live
- Log in either with your password or just your email + OTP (no password needed)
- Reset your password if you forget it — a secure link gets sent to your email
- Browse products, filter by category, search by name
- Compare up to 4 products side by side
- Add things to your wishlist
- Add to cart, apply a coupon code, choose your delivery address, and check out
- Pay online via Razorpay — the payment signature gets verified server-side
- Earn loyalty points on every order and redeem them as discounts later (1 point = ₹1 off)
- View all your past orders and download a proper PDF invoice for any of them
- Write a review and rate products you've bought
- Submit a return request if something goes wrong
- See flash sale deals on the homepage

**As a seller:**
- Register your shop and wait for admin approval
- Once approved, add and manage your own products
- See which orders contain your products

**As an admin:**
- Log into a completely custom admin panel at `/bazarx-admin/`
- See overall stats — total orders, revenue, users, products
- Add, edit, delete products and categories (with image uploads)
- Update order statuses
- Approve or reject seller applications
- Handle return requests
- Create and manage flash sales



## Tech Stack

- **Django 6** — backend framework
- **MySQL** — main database
- **Razorpay** — online payments
- **Cloudinary** — cloud image storage
- **Gmail SMTP** — for sending OTPs and password reset emails
- **ReportLab** — PDF invoice generation
- **Bootstrap 5** — frontend styling
- **Gunicorn** — production server
- Hosted on **Railway**



## Folder Overview

```
BazaarX/
├── bazarx/       → project settings & main URL config
├── users/        → auth, OTP, profile, addresses, loyalty points
├── products/     → listings, categories, search, reviews, compare
├── cart/         → cart logic
├── orders/       → checkout, Razorpay, invoice PDF
├── coupons/      → coupon codes
├── seller/       → seller registration & seller dashboard
├── returns/      → return requests
├── extras/       → wishlist & flash sales
├── dashboard/    → custom admin panel
├── utils/        → shared helpers (email utils etc.)
├── templates/    → all HTML
├── static/       → CSS, JS
└── media/        → uploaded images
```



## Setting It Up Locally

**Clone and enter the project**
```bash
git clone https://github.com/your-username/BazaarX.git
cd BazaarX
```

**Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

**Install dependencies**
```bash
pip install -r requirements.txt
```

**Set up the MySQL database**

Run this in your MySQL shell:
```sql
CREATE DATABASE bazarx_db;
CREATE USER 'bazarx_user'@'localhost' IDENTIFIED BY 'bazarx123';
GRANT ALL PRIVILEGES ON bazarx_db.* TO 'bazarx_user'@'localhost';
FLUSH PRIVILEGES;
```

**Create a `.env` file in the root folder**

```env
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret

EMAIL_HOST_USER=youremail@gmail.com
EMAIL_HOST_PASSWORD=your_gmail_app_password

CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

> For Gmail, use an **App Password** — not your actual password. Generate one from Google Account → Security → 2-Step Verification → App Passwords.

**Run migrations**
```bash
python manage.py migrate
```

**Create a superuser (for the admin panel)**
```bash
python manage.py createsuperuser
```

**Start the server**
```bash
python manage.py runserver
```

Go to `http://127.0.0.1:8000` and you're good.

---

## A Few Things Worth Knowing

**OTP verification** — When someone registers, their account is set to inactive. They only get activated after they paste the OTP from their email. The OTP expires in 10 minutes.

**Razorpay** — The payment flow is proper. After payment, the signature gets verified on the server before anything is confirmed. The frontend saying "payment done" is not enough.

**Loyalty points** — Points are awarded automatically after a successful payment. At checkout, users can choose how many points to redeem.

**PDF invoices** — Generated on the fly using ReportLab. Hit download and it streams directly to you.

**Admin security** — The custom admin at `/bazarx-admin/` is locked behind a `@staff_required` decorator and a custom middleware. If you're not staff, you get bounced. The default Django admin still exists but it's hidden at `/bazarx-secret-2026/`.

---

## Deployment

Deployed on Railway. The production command is:
```bash
gunicorn bazarx.wsgi:application --bind 0.0.0.0:$PORT
```

---

## License

MIT. Use it however you want.
