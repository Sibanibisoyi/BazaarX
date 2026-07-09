# BazaarX

A fully working multi-vendor e-commerce platform built with Django 6. Customers can shop, sellers can list products, and admins manage everything through a completely custom dashboard. No templates bought — built from scratch.

---

## Why I Built This

I wanted to build something that actually feels like a real product, not just another tutorial CRUD app. BazaarX has OTP-based authentication, Razorpay payments with server-side signature verification, a loyalty points system, live search autocomplete, infinite scroll, PDF invoice generation, flash sales, coupon codes, wishlists, product comparison, return requests, and a custom admin panel — all in a single project.

It's not perfect, but it works end to end.

---

## Features

### For Customers
- **Passwordless Login** — sign in with just your email + OTP, no password required
- **Email OTP Registration** — accounts stay inactive until OTP is verified (expires in 10 min)
- **Password Reset** — secure reset link sent to email via Gmail SMTP
- **Live Search Autocomplete** — instant product suggestions as you type, with image, price, category, and keyboard navigation
- **Infinite Scroll** — products load automatically as you scroll down, no pagination clicks
- **Browse & Filter** — browse by category, filter from the navbar or sidebar
- **Product Comparison** — compare up to 4 products side by side
- **Wishlist** — save products for later
- **Flash Sales** — time-limited deals shown on the homepage
- **Cart** — add products, apply coupon codes, pick delivery address
- **Coupon Codes** — time-limited, minimum-cart-value enforced, per-user abuse prevention
- **Razorpay Checkout** — pay online with server-side signature verification before order confirmation
- **Loyalty Points** — earn points on every order (1 point = ₹1), redeem at checkout
- **Order History** — view all past orders with full details
- **PDF Invoice** — download a proper PDF invoice for any order
- **Product Reviews** — rate and review products you've bought (one review per product)
- **Return Requests** — submit a return with a reason, track its status (pending / approved / rejected)
- **Recently Viewed** — last 6 viewed products stored in session

### For Sellers
- Register a shop and wait for admin approval
- Once approved: add, edit, and manage products with images (stored on Cloudinary)
- View orders that contain your products
- Separate seller dashboard with its own navigation

### For Admins
- Fully custom admin panel at `/bazarx-admin/` — no default Django admin UI
- Dashboard with stats: total orders, revenue, users, products
- Manage products and categories (create, edit, delete with image uploads)
- Update order statuses
- Approve or reject seller applications
- Handle return requests
- Create and manage flash sales
- Hidden default Django admin still available at `/bazarx-secret-2026/`

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 6 |
| Database | MySQL (production) / SQLite (local dev) |
| Payments | Razorpay |
| Image Storage | Cloudinary |
| Email | Gmail SMTP |
| PDF Generation | ReportLab |
| Frontend | Bootstrap 5 + Vanilla JS |
| Production Server | Gunicorn |
| Hosting | Railway |

---

## Project Structure

```
BazaarX/
├── bazarx/         → project settings & main URL config
├── users/          → auth, OTP, profile, addresses, loyalty points
├── products/       → listings, categories, search, autocomplete, reviews, compare
├── cart/           → cart logic, save for later
├── orders/         → checkout, Razorpay, invoice PDF
├── coupons/        → coupon codes
├── seller/         → seller registration & seller dashboard
├── returns/        → return requests
├── extras/         → wishlist & flash sales
├── dashboard/      → custom admin panel
├── utils/          → shared helpers (email utils etc.)
├── templates/      → all HTML templates
├── static/         → CSS, JS, images
└── media/          → uploaded images (local dev)
```

---

## Running Locally

**1. Clone the repo**
```bash
git clone https://github.com/your-username/BazaarX.git
cd BazaarX
```

**2. Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up MySQL** (or skip and use SQLite — just change `DATABASES` in settings)

Run this in your MySQL shell:
```sql
CREATE DATABASE bazarx_db;
CREATE USER 'bazarx_user'@'localhost' IDENTIFIED BY 'bazarx123';
GRANT ALL PRIVILEGES ON bazarx_db.* TO 'bazarx_user'@'localhost';
FLUSH PRIVILEGES;
```

**5. Create a `.env` file in the root folder**
```env
SECRET_KEY=your_django_secret_key

RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret

EMAIL_HOST_USER=youremail@gmail.com
EMAIL_HOST_PASSWORD=your_gmail_app_password

CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

> For Gmail, generate an **App Password** from: Google Account → Security → 2-Step Verification → App Passwords

**6. Run migrations**
```bash
python manage.py migrate
```

**7. Create a superuser**
```bash
python manage.py createsuperuser
```

**8. Start the dev server**
```bash
python manage.py runserver
```

Go to `http://127.0.0.1:8000` and you're good.

---

## Things Worth Knowing

**OTP verification** — New accounts are set to inactive on registration. They activate only after pasting the correct OTP from email. OTP expires in 10 minutes.

**Live search** — The autocomplete dropdown fires after 2+ characters with a 300ms debounce. Supports keyboard navigation (↑ ↓ Enter Escape). Returns top 6 matching products with image, price, and category.

**Infinite scroll** — Uses the browser's native `IntersectionObserver` API. An invisible sentinel sits 200px below the last product card. When it enters the viewport, the next batch of 12 products is fetched silently and appended to the grid.

**Razorpay payments** — The frontend saying "payment done" is not enough. The payment signature is verified server-side before anything is confirmed.

**Loyalty points** — Awarded automatically after a successful payment. At checkout, users can choose how many points to redeem (1 point = ₹1 off).

**Coupon abuse prevention** — Each coupon tracks which users have used it via a `ManyToManyField`. Re-use is blocked. Minimum cart amount is enforced before the discount applies.

**Flash sales** — Evaluated in real time using `timezone.now()`. Sales that haven't started yet or have expired are automatically excluded.

**PDF invoices** — Generated on the fly with ReportLab, streamed directly to the browser. No static files stored.

**Admin security** — The custom admin at `/bazarx-admin/` is protected by a `@staff_required` decorator and custom middleware. Non-staff users get redirected. The default Django admin is hidden at a non-standard URL.

---

## Deployment

Deployed on Railway. The production startup command is:
```bash
gunicorn bazarx.wsgi:application --bind 0.0.0.0:$PORT
```

---

## License

MIT. Use it however you want.
