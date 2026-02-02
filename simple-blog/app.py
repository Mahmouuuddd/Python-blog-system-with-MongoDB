from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

app = Flask(__name__)
# ==========================================
# DATABASE CONNECTION
# ==========================================
# Connect to MongoDB (update connection string if using MongoDB Atlas)
client = MongoClient('mongodb://localhost:27017/')
db = client['simple_blog']
posts_collection = db['posts']
# ==========================================
# API ROUTES
# ==========================================
@app.route('/')
def home():
    """Display all posts with sorting option"""
    # Get sort parameter from URL (default: newest first)
    sort_by = request.args.get('sort', 'date_desc')
   
    # Determine sort criteria
    if sort_by == 'date_desc':
        sort_dict = {'created_at': -1}
    elif sort_by == 'date_asc':
        sort_dict = {'created_at': 1}
    elif sort_by == 'title_asc':
        sort_dict = {'title': 1}
    elif sort_by == 'title_desc':
        sort_dict = {'title': -1}
    elif sort_by == 'author_asc':
        sort_dict = {'author': 1}
    else:
        sort_dict = {'created_at': -1}
    
    # Use aggregation with $facet to get both posts and author counts in one query
    pipeline = [
        {"$facet": {
            "posts": [
                {"$sort": sort_dict}
            ],
            "author_counts": [
                {"$group": {"_id": "$author", "count": {"$sum": 1}}}
            ]
        }}
    ]
    result = list(posts_collection.aggregate(pipeline))
    posts = result[0]['posts']
    author_counts = {ac['_id']: ac['count'] for ac in result[0]['author_counts'] if ac['_id'] is not None}
   
    return render_template('home.html', posts=posts, current_sort=sort_by, author_counts=author_counts)

@app.route('/create_post', methods=['POST'])
def create_post():
    """Create a new post"""
    title = request.form.get('title')
    content = request.form.get('content')
    author = request.form.get('author')
   
    # Create post document
    post = {
        'title': title,
        'content': content,
        'author': author,
        'created_at': datetime.now(),
        'comments': []
    }
   
    posts_collection.insert_one(post)
    return redirect(url_for('home'))
@app.route('/post/<post_id>')
def view_post(post_id):
    """View a single post with comments"""
    post = posts_collection.find_one({'_id': ObjectId(post_id)})
    return render_template('post.html', post=post)
@app.route('/add_comment/<post_id>', methods=['POST'])
def add_comment(post_id):
    """Add a comment to a post"""
    username = request.form.get('username')
    comment_text = request.form.get('comment')
   
    # Create comment object
    comment = {
        'username': username,
        'text': comment_text,
        'created_at': datetime.now()
    }
   
    # Add comment to post's comments array
    posts_collection.update_one(
        {'_id': ObjectId(post_id)},
        {'$push': {'comments': comment}}
    )
   
    return redirect(url_for('view_post', post_id=post_id))
# ==========================================
# TEMPLATES (Create these files in 'templates' folder)
# ==========================================
# templates/home.html
HOME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Simple Blog</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        .post { border: 1px solid #ddd; padding: 15px; margin: 15px 0; border-radius: 5px; }
        .post h3 { margin-top: 0; }
        .post-meta { color: #666; font-size: 0.9em; }
        form { background: #f5f5f5; padding: 20px; border-radius: 5px; margin: 20px 0; }
        input, textarea { width: 100%; padding: 8px; margin: 5px 0; box-sizing: border-box; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; border-radius: 3px; }
        button:hover { background: #0056b3; }
        .sort-container { background: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .sort-container label { font-weight: bold; margin-right: 10px; }
        .sort-container select { padding: 8px; border-radius: 3px; border: 1px solid #ccc; }
    </style>
</head>
<body>
    <h1>📝 Simple Blog System</h1>
   
    <h2>Create New Post</h2>
    <form action="/create_post" method="POST">
        <input type="text" name="author" placeholder="Your name" required>
        <input type="text" name="title" placeholder="Post title" required>
        <textarea name="content" placeholder="Write your post..." rows="4" required></textarea>
        <button type="submit">Post</button>
    </form>
   
    <div class="sort-container">
        <label for="sort">Sort by:</label>
        <select id="sort" onchange="window.location.href='/?sort=' + this.value">
            <option value="date_desc" {% if current_sort == 'date_desc' %}selected{% endif %}>Newest First</option>
            <option value="date_asc" {% if current_sort == 'date_asc' %}selected{% endif %}>Oldest First</option>
            <option value="title_asc" {% if current_sort == 'title_asc' %}selected{% endif %}>Title (A-Z)</option>
            <option value="title_desc" {% if current_sort == 'title_desc' %}selected{% endif %}>Title (Z-A)</option>
            <option value="author_asc" {% if current_sort == 'author_asc' %}selected{% endif %}>Author (A-Z)</option>
        </select>
    </div>
   
    <h2>All Posts</h2>
    {% for post in posts %}
    <div class="post">
        <h3><a href="/post/{{ post._id }}">{{ post.title }}</a></h3>
        <p>{{ post.content }}</p>
        <div class="post-meta">
            By {{ post.author }} ({{ author_counts.get(post.author, 0) }} posts) | {{ post.created_at.strftime('%Y-%m-%d %H:%M') }} |
            {{ post.comments|length }} comments
        </div>
    </div>
    {% endfor %}
</body>
</html>
"""
# templates/post.html
POST_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ post.title }}</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        .post { border: 1px solid #ddd; padding: 20px; border-radius: 5px; }
        .comment { background: #f9f9f9; padding: 10px; margin: 10px 0; border-left: 3px solid #007bff; }
        form { background: #f5f5f5; padding: 20px; border-radius: 5px; margin: 20px 0; }
        input, textarea { width: 100%; padding: 8px; margin: 5px 0; box-sizing: border-box; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; border-radius: 3px; }
    </style>
</head>
<body>
    <a href="/">← Back to all posts</a>
   
    <div class="post">
        <h1>{{ post.title }}</h1>
        <p>{{ post.content }}</p>
        <small>By {{ post.author }} | {{ post.created_at.strftime('%Y-%m-%d %H:%M') }}</small>
    </div>
   
    <h2>Comments ({{ post.comments|length }})</h2>
    {% for comment in post.comments %}
    <div class="comment">
        <strong>{{ comment.username }}</strong>: {{ comment.text }}
        <br><small>{{ comment.created_at.strftime('%Y-%m-%d %H:%M') }}</small>
    </div>
    {% endfor %}
   
    <h3>Add a Comment</h3>
    <form action="/add_comment/{{ post._id }}" method="POST">
        <input type="text" name="username" placeholder="Your name" required>
        <textarea name="comment" placeholder="Write your comment..." rows="3" required></textarea>
        <button type="submit">Comment</button>
    </form>
</body>
</html>
"""
if __name__ == '__main__':
    # Save templates to files in the correct location
    import os
   
    # Get the directory where app.py is located
    base_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(base_dir, 'templates')
   
    # Create templates folder
    os.makedirs(templates_dir, exist_ok=True)
   
    # Write template files
    with open(os.path.join(templates_dir, 'home.html'), 'w', encoding='utf-8') as f:
        f.write(HOME_TEMPLATE)
    with open(os.path.join(templates_dir, 'post.html'), 'w', encoding='utf-8') as f:
        f.write(POST_TEMPLATE)
   
    app.run(debug=True)