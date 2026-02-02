# Simple Blog System

A simple blog application built with Flask and MongoDB.

## Features
- Create posts with title, content, and author
- Add comments to posts
- Sort posts by date, title, or author
- View post count per author
- MongoDB database storage

## 🗂️ Project Structure
```
Python-blog-system-with-MongoDB/
├── simple-blog/
│   ├── app.py                # App implementation 
|   ├── templates/
|       ├── home.html                  # Front-end of the Page
|       └── post.html                  # Front-end of the Post
├── .gitignore
├── LICENSE
└── README.md
```


## Installation

1. Install dependencies:
```bash
pip install flask pymongo
```

2. Start MongoDB locally or use MongoDB Atlas

3. Run the app:
```bash
python app.py
```

4. Open browser: `http://localhost:5000`

## Technologies
- Python Flask
- MongoDB
- HTML/CSS
- Jinja2 Templates
