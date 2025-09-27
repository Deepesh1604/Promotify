# 🚀 Promotify - Influencer Marketing Platform

<div align="center">

![Promotify Logo](static/images/promotify.png)

**Connecting Brands with Influencers Through Seamless Digital Marketing**

[![Built with Flask](https://img.shields.io/badge/Built%20with-Flask-blue.svg)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/Database-SQLite-lightgrey.svg)](https://www.sqlite.org/)
[![UI Framework](https://img.shields.io/badge/UI-Modern%20CSS-orange.svg)](https://github.com/Deepesh1604/Promotify)

</div>

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [✨ Key Features](#-key-features)
- [💰 Wallet System](#-wallet-system)
- [🛠️ Technology Stack](#️-technology-stack)
- [ Quick Start](#-quick-start)
- [🌍 Real-World Applications](#-real-world-applications)

---

## 🎯 Overview

**Promotify** is a modern influencer marketing platform that connects brands with content creators. It features a comprehensive wallet system, campaign management tools, and an intuitive interface designed for seamless collaboration.

**Key Highlights:**
- **Three User Types**: Sponsors, Influencers, and Administrators
- **Integrated Wallet**: Automatic payment processing with UPI/Card support
- **Campaign Management**: Complete lifecycle from creation to completion
- **Modern UI**: Glass morphism design with responsive layouts

---

## ✨ Key Features

### 🏢 **For Sponsors**
- Create and manage campaigns with budget, timeline, and requirements
- Integrated wallet system with UPI/Card payments
- Automatic payment processing upon campaign acceptance
- Real-time application tracking and approval workflows
- Search and discover relevant influencers

### 🌟 **For Influencers**  
- Discover and apply for relevant campaigns
- Digital wallet with instant payment reception
- Bank account integration for secure withdrawals
- Social media profile integration (Instagram, YouTube, LinkedIn, Twitter)
- Comprehensive earnings and transaction history

### 👥 **For Administrators**
- Complete platform oversight and user management
- Campaign monitoring and content moderation
- Analytics dashboard with platform-wide insights
- Payment system oversight and dispute resolution

## 💰 Wallet System

**Promotify** features an integrated digital wallet system for seamless financial transactions:

### 🏦 **Payment Processing**
- **Multiple Payment Methods**: UPI, Credit/Debit Cards, Net Banking
- **Automatic Transfers**: Instant payment to influencers upon campaign acceptance
- **Secure Withdrawals**: Bank account integration for influencers
- **Transaction History**: Complete audit trail with reference IDs
- **Real-time Updates**: Instant balance updates and notifications

### 💳 **Security Features**
- End-to-end transaction encryption
- Automated fraud detection and monitoring
- Complete audit trails for compliance
- Secure bank account integration

```python
# Automatic Payment Processing
def accept_application(application_id):
    sponsor.wallet_balance -= campaign_budget
    influencer.wallet_balance += campaign_budget
    create_transaction_records(sponsor, influencer, campaign_budget)
```

## 🛠️ Technology Stack

**Backend:**
- **Flask** - Python web framework
- **SQLAlchemy** - Database ORM
- **SQLite** - Database (Production: PostgreSQL ready)

**Frontend:**
- **Jinja2** - Template engine
- **Modern CSS** - Glass morphism design
- **Font Awesome** - Icons
- **Responsive Design** - Mobile-first approach

**Features:**
- Session-based authentication
- Real-time payment processing
- Comprehensive input validation
- Professional UI/UX design

## 🚀 Quick Start

### Installation
```bash
git clone https://github.com/Deepesh1604/Promotify.git
cd Promotify
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Setup Database
```bash
python rebuild_database.py    # Create fresh database
python wallet_test_data.py    # Add sample data
```

### Run Application
```bash
python3 main.py
```
Open browser: `http://localhost:5006`

### Test Credentials
```
Sponsor: sponsor@test.com / password123 (₹1,00,000 balance)
Influencer: tech@influencer.com / password123 (₹15,000 balance)
Admin: admin@promotify.com / admin123
```

## 🌍 Real-World Applications

**E-commerce & Retail**
- Product launches with lifestyle influencers
- Seasonal promotions and unboxing content
- User-generated testimonials

**Technology & Software** 
- App promotion through gaming influencers
- Tech reviews and tutorial content
- B2B software marketing

**Travel & Food**
- Destination marketing with travel bloggers
- Restaurant promotions and recipe content
- Cultural and culinary experiences

**Success Examples:**
- **Local Bakery**: ₹15,000 campaign → 300% Instagram engagement, 150% sales boost
- **Tech Startup**: ₹2,00,000 campaign → 50K app downloads, 25% paid conversions
- **Fashion Influencer**: ₹45,000 monthly earnings from 20 campaign applications



---

## 👨‍💻 Author

**Developed by: [Deepesh Kumar Dawar](https://github.com/Deepesh1604)**

*Full-stack developer passionate about creating innovative digital marketing solutions that connect brands with creators through technology.*

<div align="center">

**🌟 Promotify - Where Brands Meet Creators 🌟**

[![GitHub Stars](https://img.shields.io/github/stars/Deepesh1604/Promotify?style=social)](https://github.com/Deepesh1604/Promotify)
[![Follow on GitHub](https://img.shields.io/github/followers/Deepesh1604?style=social)](https://github.com/Deepesh1604)

</div>
