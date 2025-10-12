# Arts Sell - Art Marketplace Platform

A modern web application for buying and selling artwork, built with Flask and featuring a beautiful, responsive frontend.

## 🌟 Features

- **User Authentication**: Secure login/registration system with role-based access (Customer, Artist, Admin)
- **Artwork Gallery**: Browse and search through available artworks
- **Shopping Cart**: Add artworks to cart and manage quantities
- **Checkout System**: Complete purchase flow with order management
- **Artist Dashboard**: Artists can manage their portfolio and track sales
- **Admin Dashboard**: Administrative controls for platform management
- **Responsive Design**: Modern UI that works on all devices
- **Profile Management**: Users can update their personal information

## 🎨 Frontend Improvements

- Enhanced form styling with improved textarea handling
- Better focus states and visual feedback
- Improved floating label positioning
- Professional color scheme and typography
- Mobile-responsive design
- Smooth animations and transitions

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: MySQL
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF
- **Styling**: Custom CSS with modern design patterns

## 📋 Prerequisites

- Python 3.8+
- MySQL 5.7+
- pip (Python package installer)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Karol-96/arts-sell.git
   cd arts-sell
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the database**
   - Create a MySQL database named `artspace`
   - Import the database schema:
     ```bash
     mysql -u your_username -p artspace < database.sql
     mysql -u your_username -p artspace < add_data.sql
     ```

4. **Configure the application**
   - Update database credentials in `project/__init__.py`:
     ```python
     app.config['MYSQL_HOST'] = 'localhost'
     app.config['MYSQL_USER'] = 'your_username'
     app.config['MYSQL_PASSWORD'] = 'your_password'
     app.config['MYSQL_DB'] = 'artspace'
     ```

5. **Run the application**
   ```bash
   python run.py
   ```

6. **Access the application**
   - Open your browser and go to `http://127.0.0.1:5000`

## 📱 User Roles

- **Customer**: Browse and purchase artworks
- **Artist**: Upload and manage artworks, track sales
- **Admin**: Manage users, artworks, and platform settings

## 🎯 Key Pages

- **Home**: Featured artworks and platform introduction
- **Artworks**: Browse all available artworks
- **Profile**: Manage personal information and view order history
- **Cart**: Shopping cart management
- **Checkout**: Complete purchase process
- **Artist Dashboard**: Portfolio and sales management
- **Admin Dashboard**: Platform administration

## 🔧 Development

The application is built with a modular structure:

```
project/
├── __init__.py          # Flask app initialization
├── views.py             # Route handlers
├── models.py            # Database models
├── forms.py             # WTForms definitions
├── db.py                # Database operations
├── static/
│   ├── css/
│   │   └── styles.css   # Custom styling
│   └── img/             # Images and assets
└── templates/           # HTML templates
```

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

If you have any questions or need help, please open an issue on GitHub.

---

**Made with ❤️ for art lovers and creators**