# ArtSpace - Art Lease Platform

A modern web application for leasing artwork through monthly subscriptions, built with Flask and featuring a beautiful, responsive frontend.

## 🌟 Features

- **User Authentication**: Secure login/registration system with role-based access (Customer, Artist, Admin)
- **Artwork Gallery**: Browse and search through available artworks for lease
- **Lease Cart**: Add artworks to cart for monthly subscription
- **Checkout System**: Complete lease subscription flow with order management
- **Artist Dashboard**: Artists can manage their portfolio and track lease history
- **Admin Dashboard**: Administrative controls for platform management
- **Responsive Design**: Modern UI that works on all devices
- **Profile Management**: Users can update their personal information
- **Unique Artwork System**: Each artwork is unique (quantity = 1), when leased, others must wait for return

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

- **Customer**: Browse and lease artworks through monthly subscriptions
- **Artist**: Upload and manage artworks, track lease history
- **Admin**: Manage users, artworks, and platform settings

## 🎯 Key Pages

- **Home**: Featured artworks and platform introduction
- **Artworks**: Browse all available artworks for lease
- **Profile**: Manage personal information and view lease history
- **Cart**: Lease cart management
- **Checkout**: Complete lease subscription process
- **Artist Dashboard**: Portfolio and lease history management
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

## 🖼️ Artwork Data Licensing

**Important Notice**: This application uses artwork data for university demonstration purposes only.

### Data Source and Usage
- **Source**: Artwork data is crawled from open access galleries
- **Purpose**: University demonstration and educational use only
- **Commercial Use**: This data is NOT intended for commercial purposes
- **Data Modifications**: Some metadata (including prices) has been modified to adapt to the assignment requirements

### Attribution
- **Primary Source**: [The Metropolitan Museum of Art Open Access](https://www.metmuseum.org/about-the-met/policies-and-documents/open-access)
- **Credit**: We acknowledge and credit The Metropolitan Museum of Art for providing open access to their collection data

### Legal Compliance
- All artwork data is used in compliance with the source institution's open access policies
- Users are responsible for ensuring compliance with any applicable licensing terms
- For commercial use, users must obtain appropriate licenses from the original data sources

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

If you have any questions or need help, please open an issue on GitHub.

---

**Made with ❤️ for art lovers and creators**
