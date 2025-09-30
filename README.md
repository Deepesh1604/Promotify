# 🚀 Promotify - Influencer Marketing Platform

<div align="center">

![Promotify Logo](static/images/promotify.png)

**Professional Influencer Marketing Platform with Integrated Payment System**

[![Flask](https://img.shields.io/badge/Flask-2.3+-blue.svg)](https://flask.palletsprojects.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-orange.svg)](https://sqlalchemy.org/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

</div>

## 🎯 Overview

**Promotify** is a comprehensive influencer marketing platform that facilitates seamless collaboration between brands and content creators. Built with Flask and modern web technologies, it features an integrated digital wallet system, campaign management tools, and advanced analytics.

### Key Differentiators
- **🔄 End-to-End Workflow**: Complete campaign lifecycle from creation to payment
- **💳 Integrated Payments**: Automatic wallet processing with real-time transactions
- **📊 Advanced Analytics**: Multi-role dashboards with filtering and export capabilities  
- **🎨 Modern Interface**: Professional UI with responsive design and dark theme

## ✨ Core Features

### 🏢 Sponsor Dashboard
- **Campaign Creation**: Define budgets, timelines, and target demographics
- **Influencer Discovery**: Search and filter by niche, followers, and engagement
- **Automated Payments**: Instant wallet transfers upon campaign acceptance
- **Application Management**: Streamlined approval workflows with bulk actions
- **Performance Analytics**: Campaign ROI tracking and detailed reporting

### 🌟 Influencer Portal
- **Campaign Discovery**: Browse and apply for relevant opportunities
- **Social Integration**: Link Instagram, YouTube, LinkedIn, and Twitter profiles
- **Instant Earnings**: Real-time wallet updates with secure withdrawals
- **Portfolio Management**: Showcase content and track collaboration history
- **Analytics Dashboard**: Earnings insights and performance metrics

### �‍💼 Admin Control Center  
- **Platform Oversight**: User management and content moderation
- **Financial Monitoring**: Transaction tracking and dispute resolution
- **Advanced Filtering**: Filter by applications, campaigns, transactions, users
- **Data Export**: Download filtered data or complete platform analytics
- **System Analytics**: Platform growth metrics and user engagement insights

## 💰 Digital Wallet System

**Secure, automated payment processing with multi-method support:**

- **Payment Methods**: UPI, Credit/Debit Cards, Net Banking
- **Instant Transfers**: Automatic balance updates on campaign acceptance  
- **Withdrawal System**: Direct bank account integration for influencers
- **Transaction Logging**: Complete audit trails with reference tracking
- **Balance Management**: Real-time balance updates with notification system


## 🛠️ Technology Stack

**Backend Architecture:**
- **Flask 2.3+** - Lightweight WSGI web framework
- **SQLAlchemy** - Object-relational mapping and database abstraction
- **SQLite/PostgreSQL** - Development and production database support
- **Jinja2** - Server-side template rendering

**Frontend Technologies:**
- **Modern CSS3** - Custom styling with CSS Grid and Flexbox
- **JavaScript ES6** - Interactive UI components and AJAX functionality  
- **Font Awesome** - Professional icon library
- **Responsive Design** - Mobile-first approach with breakpoints

**Security & Performance:**
- Session-based authentication with secure cookie handling
- Input validation and SQL injection prevention
- Optimized database queries with proper indexing
- Professional error handling and logging

## 🚀 Quick Start Guide

### 1. Installation
```bash
# Clone repository
git clone https://github.com/Deepesh1604/Promotify.git
cd Promotify

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup
```bash
python3 main.py  # Creates database on first run
```

### 3. Launch Application
```bash
python3 main.py
# Open browser: http://localhost:5007
```

### 4. Demo Credentials
```
🏢 Sponsor: sponsor@demo.com / password123
🌟 Influencer: influencer@demo.com / password123  
👨‍💼 Admin: admin@promotify.com / admin123
```

## 📁 Project Architecture

```
Promotify/
├── main.py              # Application entry point and Flask configuration
├── routes.py            # Route handlers and business logic (2000+ lines)
├── models.py            # SQLAlchemy database models and relationships
├── static/
│   ├── css/            # Component-specific stylesheets
│   └── images/         # Platform assets and branding
├── templates/          # Jinja2 HTML templates for all user roles
├── instance/           # Database files and sensitive configuration
└── requirements.txt    # Production dependencies
```

## 🎪 Live Features Demo

- **Multi-Role Authentication**: Separate interfaces for sponsors, influencers, and admins
- **Real-Time Payments**: Instant wallet processing with balance validation
- **Campaign Invitations**: Direct sponsor-to-influencer campaign invitations
- **Advanced Filtering**: Filter platform data by time, users, categories, and date ranges
- **Data Export**: Download complete or filtered platform analytics
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices

---

<div align="center">

**Built by [Deepesh Kumar Dawar](https://github.com/Deepesh1604)** 

*Connecting brands with creators through innovative technology*

[![⭐ Star this repo](https://img.shields.io/github/stars/Deepesh1604/Promotify?style=social)](https://github.com/Deepesh1604/Promotify)

</div>
