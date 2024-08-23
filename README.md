# Promotify - Bridging Sponsors and Influencers

### Author
**Name:-**  **Deepesh Kumar Dawar**

---

## 📜 Description

Introducing **Promotify**, a dynamic and user-friendly web application designed to bridge the gap between Sponsors and Influencers in the digital marketing landscape. **Promotify** offers a seamless experience, allowing Sponsors to create and manage advertising campaigns while enabling Influencers to discover and apply for these opportunities.

**Promotify** goes beyond basic connectivity by providing comprehensive management tools for both Sponsors and Influencers. Sponsors can effortlessly create campaigns, review applications, and track the progress of their marketing initiatives. Influencers, on the other hand, can explore a variety of campaigns, apply with ease, and manage their engagements all in one place.

The platform takes the collaboration experience a step further by incorporating an admin interface for overseeing all activities, ensuring smooth operations and maintaining the integrity of the ecosystem. Whether it's campaign management, user oversight, or performance analytics, **Promotify** simplifies these tasks within a unified platform.

Designed with user-friendliness in mind, **Promotify** makes it effortless for Sponsors to find the right Influencers for their campaigns and for Influencers to discover exciting marketing opportunities. It brings the power of influencer marketing to your fingertips, whether you're a brand looking to expand your reach or an influencer aiming to monetize your online presence. Dive into the world of **Promotify** and experience a new dimension of digital marketing collaboration!

---

## 🛠️ Technologies Used

- **Flask:** A micro web framework used to build the web application.
- **Flask-SQLAlchemy:** A Flask extension that simplifies the integration of SQLAlchemy with Flask.
- **SQLAlchemy:** An Object-Relational Mapping (ORM) library used to interact with the database.
- **SQLite:** A lightweight, serverless database engine used for data storage.
- **HTML, CSS, Bootstrap:** Web development technologies used to create the user interface and styling.
- **Jinja2:** A template engine used to render dynamic HTML templates in Flask.
- **Chart.js:** A JavaScript library used for creating interactive charts and graphs.

---

## 🗂️ DB Schema Design

The database model includes tables for **Sponsors**, **Influencers**, **Campaigns**, and **Applications**.  
- **Sponsors** and **Influencers** are defined by `id`, `username`, `email`, `password`, and additional profile information.  
- **Campaigns** encompass details such as `name`, `description`, `dates`, and `budget`.  
- **Applications** link Influencers to Campaigns with a `status` field. 

This schema forms the foundation for managing user accounts, campaign information, and application processes in the **Promotify** application.

---

## 🏛️ Architecture and Features

In the root folder, we have the following key components:
1. **main.py:**  
   Acts as the main controller for the app and contains all the routes to different pages.

2. **templates folder:**  
   Contains HTML templates for rendering different pages of the application.

3. **static folder:**  
   Stores static assets such as CSS files, JavaScript, and images.

---

## 🌟 Key Features

- **User registration and authentication** for Sponsors and Influencers
- **Campaign creation and management** for Sponsors
- **Campaign discovery and application system** for Influencers
- **Admin dashboard** for overseeing platform activities
- **Search functionality** for campaigns and users
- **Analytics and statistics** for user growth and campaign performance
- **CRUD operations** for campaigns and user profiles

The application implements proper front-end and back-end validation for user inputs. It features separate login forms for **Sponsors**, **Influencers**, and **Admins**, with secure role-based access control. The platform includes comprehensive CRUD features for **Campaigns** and **Applications**. Sponsors can review and manage applications, while Admins have the ability to oversee all platform activities, including user management and campaign moderation.
