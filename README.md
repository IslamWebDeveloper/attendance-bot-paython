# 🤖 Odoo ERP Daily Auto Checkout Bot (GitHub Actions)

This repository contains an automated GitHub Actions bot that logs into **https://techsup-erp.com/my/attendance** and automatically checks out from attendance every day at **5:00 PM Saudi Arabia Time (14:00 UTC)**.

---

## 📁 Repository Structure

```
.
├── .github/
│   └── workflows/
│       └── checkout.yml    # GitHub Actions workflow schedule (14:00 UTC)
├── checkout.py            # Main Playwright automation script
├── checkout_requests.py   # Alternative lightweight HTTP session script
└── README.md              # Setup instructions
```

---

## ⚡ Setup Instructions (5 Minutes)

### Step 1: Create a GitHub Repository
1. Go to [GitHub.com](https://github.com/new) and create a new **Private** or Public repository.
2. Name it e.g., `odoo-auto-checkout`.

### Step 2: Configure Repository Secrets 🔐
To protect your email and password, save them in GitHub Secrets:
1. In your GitHub repository, go to **Settings** > **Secrets and variables** > **Actions**.
2. Click **New repository secret** and add the following:

| Secret Name | Value | Description |
| :--- | :--- | :--- |
| `ERP_EMAIL` | `Islam@techsupbusiness.com` | Your Odoo login email |
| `ERP_PASSWORD` | `Ii@123123` | Your Odoo password |
| `ERP_URL` | `https://techsup-erp.com/my/attendance` | ERP URL base |
| `DISCORD_WEBHOOK` | *(Optional)* | Discord Webhook URL for alerts |
| `TELEGRAM_BOT_TOKEN` | *(Optional)* | Telegram Bot Token for alerts |
| `TELEGRAM_CHAT_ID` | *(Optional)* | Telegram Chat ID for alerts |

### Step 3: Add Files to your Repository 📤
1. Create the file `.github/workflows/checkout.yml` and paste the generated workflow code.
2. Create the file `checkout.py` in the root of your repo and paste the generated Python code.
3. Commit and push the files to your `main` or `master` branch.

### Step 4: Test Manually 🧪
1. Go to your repository on GitHub.
2. Click the **Actions** tab.
3. Select **Odoo Daily Auto Checkout Bot** on the left menu.
4. Click **Run workflow** > **Run workflow** button.
5. Watch the execution logs live!

---

## ⏰ Schedule Details

- **Schedule Time**: Every workday at **17:00 (5:00 PM) AST (UTC+3)**.
- **GitHub Actions Cron Expression**: `0 14 * * 0-4`
- **Workdays**: Sunday, Monday, Tuesday, Wednesday, Thursday.

---

## 🔐 Security & Privacy
- Your credentials are encrypted using **GitHub Secrets**.
- No credentials are hardcoded or visible in logs.
- Execution runs inside standard GitHub-hosted Ubuntu runners.
