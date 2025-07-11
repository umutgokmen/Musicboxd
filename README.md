# MusicBoxd

MusicBoxd is a music catalog web application built with Python and Flask, backed by a MySQL database. Users can browse songs, filter by artist, and leave ratings and comments; administrators can add and edit artists, albums, and songs.

## Features

* **User Management**: Registration, login, and secure password hashing
* **Admin Panel**: Add/edit artists, albums, and songs
* **Song Listing**: View all songs on the homepage and filter by artist
* **Ratings & Reviews**: Star-based ratings and user comments
* **Static Assets**: CSS styling and image assets (e.g., YouTube icon)

## Technologies

* Python 3.8+
* Flask
* flask\_mysqldb (MySQL integration)
* MySQL
* Jinja2 (template engine)
* HTML, CSS

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your_username/musicboxd.git
   cd musicboxd/src
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install flask flask_mysqldb
   ```

4. Create the MySQL database and tables:

   ```sql
   CREATE DATABASE musicboxd_db;
   USE musicboxd_db;

   CREATE TABLE users (
     id INT AUTO_INCREMENT PRIMARY KEY,
     username VARCHAR(50) UNIQUE NOT NULL,
     password VARCHAR(255) NOT NULL,
     is_admin TINYINT DEFAULT 0
   );

   CREATE TABLE artists (
     id INT AUTO_INCREMENT PRIMARY KEY,
     name VARCHAR(100) NOT NULL,
     photo_url VARCHAR(255)
   );

   CREATE TABLE albums (
     id INT AUTO_INCREMENT PRIMARY KEY,
     name VARCHAR(100) NOT NULL,
     artist_id INT,
     cover_url VARCHAR(255),
     FOREIGN KEY (artist_id) REFERENCES artists(id)
   );

   CREATE TABLE songs (
     id INT AUTO_INCREMENT PRIMARY KEY,
     title VARCHAR(100) NOT NULL,
     artist_id INT,
     album_id INT,
     song_url VARCHAR(255),
     rating FLOAT DEFAULT 0,
     FOREIGN KEY (artist_id) REFERENCES artists(id),
     FOREIGN KEY (album_id) REFERENCES albums(id)
   );

   CREATE TABLE comments (
     id INT AUTO_INCREMENT PRIMARY KEY,
     song_id INT,
     user_id INT,
     comment TEXT,
     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
     FOREIGN KEY (song_id) REFERENCES songs(id),
     FOREIGN KEY (user_id) REFERENCES users(id)
   );
   ```

5. Update database settings in `src/app.py` (host, user, password, db) to match your environment.

## Usage

```bash
cd src
python app.py
```

Open your browser and navigate to `http://localhost:5000` to use the application.

## Project Structure

```

## Repository Contents

Include the following in your GitHub repository:

- **Include**:
  - `src/` directory (all application code, blueprints, templates, and static files)
  - `README.md`
  - `requirements.txt` (generate with `pip freeze > requirements.txt`)
  - `.gitignore`
  - `.env.example` (if you use environment variables for configuration)

- **Exclude**:
  - `venv/` virtual environment folder
  - `__pycache__/` directories and `*.pyc` files
  - `.env` files containing sensitive credentials

musicboxd/
├── src/
│   ├── app.py          # Application entry point
│   ├── db.py           # Database connection module (template)
│   ├── routes/         # Blueprints (auth, admin, song)
│   ├── templates/      # HTML templates
│   └── static/         # CSS and assets
├── venv/               # Virtual environment
└── README.md           # Project documentation
```

## Contributing

Contributions are welcome! Please open a pull request or create an issue.

## License

This project is licensed under the MIT License.
