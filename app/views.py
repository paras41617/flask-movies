from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
import datetime
from app.models import User, Movie, Rating
from flask import request, jsonify
from .utils import hash_password, check_password_hash, is_valid_date

# Simple endpoint to check if the api is running or not
@app.route('/')
def index():
    return "Hello"

# Simple endpoint to check if the authentication is working or not
@app.route('/protected', methods=['GET', 'POST'])
@login_required
def protected():
    return "Hello, Flask!"

# Endpoint for user login
@app.route('/login', methods=['GET','POST'])
def login():
    if request.is_json:
        # Extract JSON data from the request
        data = request.get_json()

        # Check if the request contains valid JSON data
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400

        # Extract username and password from the JSON data
        username = data.get('username')
        password = data.get('password')

        # Check if both username and password are present
        if not username or not password:
            return jsonify({'error': 'Missing required fields'}), 400

        # Query the database to find the user by username
        user = User.query.filter_by(username=username).first()

        # Check if the user exists and the password is correct
        if user and check_password_hash(user.password, password):
            # Update the user's authenticated status, commit changes, and log in the user
            user.authenticated = True
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return jsonify({'message': 'Login successful!'}), 200
        else:
            # Return an error message if the login fails
            return jsonify({'error': 'Invalid username or password'}), 401
    else:
        # Handle form submission or other non-JSON requests
        return "Invalid request"


# Endpoint for user logout
@app.route('/logout', methods=['GET','POST'])
@login_required  # Ensures that the user is logged in before accessing this endpoint
def logout():
    # Get the current user from the Flask-Login extension
    user = current_user

    # Update the user's authenticated status to False
    user.authenticated = False

    # Commit the changes to the database
    db.session.add(user)
    db.session.commit()

    # Log the user out using Flask-Login
    logout_user()

    # Return a JSON response indicating successful logout
    return jsonify({'message': 'Logout successful!'}), 200


# Endpoint for user registration
@app.route('/register', methods=['POST'])
def register():
    # Extract JSON data from the request
    data = request.get_json()

    # Check if the request contains valid JSON data
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    # Extract username, email, and password from the JSON data
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Check if all required fields are present
    if not username or not email or not password:
        return jsonify({'error': 'Missing required fields'}), 400

    # Check if the username is already taken
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'error': 'Username already taken'}), 400

    # Hash the password using a utility function (replace with your actual hash function)
    hashed_password = hash_password(password)

    # Create a new user object with the provided information
    new_user = User(username=username, email=email, password=hashed_password)

    # Add the new user to the database and commit changes
    db.session.add(new_user)
    db.session.commit()

    # Return a JSON response indicating successful account creation
    return jsonify({'message': 'Account created successfully!'}), 201


# Endpoint for creating a movie
@app.route('/movies', methods=['POST'])
@login_required  # Requires authentication to access this endpoint
def create_movie():
    data = request.json

    # Validate title, release date, and average rating
    title = data.get('title')
    release_date = data.get('release_date')
    average_rating = data.get('average_rating')

    # Check if title, release date, and average rating are provided
    if not title or not release_date or not average_rating:
        return jsonify({"message": "Title, release date, and average rating are required"}), 400

    # Check if release date has a valid format (YYYY-MM-DD)
    if not is_valid_date(release_date):
        return jsonify({"message": "Invalid release date format. Use YYYY-MM-DD"}), 400

    try:
        # Convert average rating to float and check if it is within the range [1, 10]
        average_rating = float(average_rating)
        if not (1 <= average_rating <= 10):
            raise ValueError("Average rating must be between 1 and 10")
    except ValueError as e:
        return jsonify({"message": str(e)}), 400

    # Check if release date is not in the future
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    if release_date > current_date:
        return jsonify({"message": "Release date cannot be in the future"}), 400

    # Create and save the new movie with the current user as the creator
    new_movie = Movie(**data, creator_id=current_user.id)
    db.session.add(new_movie)
    db.session.commit()

    return jsonify({"message": "Movie created successfully"})


# endpoint for reteriving list of movies
@app.route('/movies', methods=['GET'])
def get_movies():
    # Pagination parameters
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    # Filtering parameters
    genre = request.args.get('genre')
    director = request.args.get('director')
    release_year = request.args.get('release_year', type=int)

    # Search parameters
    search_query = request.args.get('search_query')

    # Sorting parameters
    sort_by = request.args.get('sort_by')
    if sort_by not in ['release_date', 'ticket_price']:
        sort_by = 'release_date'  # Default sorting

    # Base query
    query = Movie.query

    # Apply filters
    if genre:
        query = query.filter_by(genre=genre)
    if director:
        query = query.filter_by(director=director)
    if release_year:
        query = query.filter(db.extract('year', Movie.release_date) == release_year)

    # Apply search
    if search_query:
        query = query.filter(
            (Movie.title.ilike(f'%{search_query}%')) |
            (Movie.cast.ilike(f'%{search_query}%')) |
            (Movie.description.ilike(f'%{search_query}%')) |
            (Movie.genre.ilike(f'%{search_query}%'))
        )

    # Apply sorting
    if sort_by == 'release_date':
        query = query.order_by(Movie.release_date.desc())
    elif sort_by == 'ticket_price':
        query = query.order_by(Movie.ticket_price.asc())

    # Pagination
    movies = query.paginate(page=page, per_page=per_page, error_out=False)

    # Serialize the paginated movies
    serialized_movies = [movie.serialize() for movie in movies.items]

    return jsonify({
        "page": movies.page,
        "total_pages": movies.pages,
        "total_movies": movies.total,
        "data": serialized_movies
    })


# Endpoint for getting a single movie by ID
@app.route('/movies/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    # Query the database to get the movie by its ID
    movie = Movie.query.get(movie_id)
    
    # Check if the movie exists
    if movie:
        # Return a JSON response with the serialized movie data
        return jsonify({"data": movie.serialize()})
    else:
        # Return a JSON response with an error message and a 404 status code
        return jsonify({"message": "Movie not found"}), 404


# Endpoint for updating a movie by ID
@app.route('/movies/<int:movie_id>', methods=['PUT'])
@login_required  # Requires authentication to access this endpoint
def update_movie(movie_id):
    # Query the database to get the movie by its ID
    movie = Movie.query.get(movie_id)
    
    # Check if the movie exists
    if movie:
        # Check if the current user is the creator of the movie
        if current_user.id == movie.creator_id:
            # Extract JSON data from the request
            data = request.json
            
            # Update the movie attributes with the provided data
            movie.title = data.get('title', movie.title)
            movie.description = data.get('description', movie.description)
            movie.release_date = data.get('release_date', movie.release_date)
            movie.director = data.get('director', movie.director)
            movie.genre = data.get('genre', movie.genre)
            movie.ticket_price = data.get('ticket_price', movie.ticket_price)
            movie.cast = data.get('cast', movie.cast)
            
            # Commit the changes to the database
            db.session.commit()
            
            # Return a JSON response indicating successful update
            return jsonify({"message": "Movie updated successfully"})
        else:
            # Return a JSON response if the current user is not the creator of the movie
            return jsonify({"message": "You are not the creator of this movie"})
    else:
        # Return a JSON response if the movie is not found
        return jsonify({"message": "Movie not found"}), 404
        

# Endpoint for deleting a movie by ID
@app.route('/movies/<int:movie_id>', methods=['DELETE'])
@login_required  # Requires authentication to access this endpoint
def delete_movie(movie_id):
    # Query the database to get the movie by its ID
    movie = Movie.query.get(movie_id)
    
    # Check if the movie exists
    if movie:
        # Check if the current user is the creator of the movie
        if current_user.id == movie.creator_id:
            # Delete the movie from the database
            db.session.delete(movie)
            
            # Commit the changes to the database
            db.session.commit()
            
            # Return a JSON response indicating successful deletion
            return jsonify({"message": "Movie deleted successfully"})
        else:
            # Return a JSON response if the current user is not the creator of the movie
            return jsonify({"message": "You are not the creator of this movie"})
    else:
        # Return a JSON response if the movie is not found
        return jsonify({"message": "Movie not found"}), 404


@app.route('/rate/<int:movie_id>', methods=['POST'])
@login_required
def rate(movie_id):
    # Extract JSON data from the request
    data = request.get_json()
    
    # Extract the rating value from the JSON data
    rating_value = data.get('rating')

    if(int(rating_value) > 10 or int(rating_value) < 0):
        return jsonify({'error': 'Rating should be in the range of 1 to 10'}), 404
    
    # Query the database to get the movie by its ID
    movie = Movie.query.get(movie_id)

    # Check if the movie exists
    if not movie:
        # Return a JSON response if the movie is not found
        return jsonify({'error': 'Movie not found'}), 404
    
    # Check if the user has already rated the movie
    existing_rating = Rating.query.filter_by(user_id=current_user.id, movie_id=movie.id).first()

    if existing_rating:
        # If the user has already rated the movie, update the existing rating
        existing_rating.rating = rating_value
    else:
        # If the user has not yet rated the movie, create a new rating
        new_rating = Rating(rating=rating_value, user_id=current_user.id, movie_id=movie.id)
        db.session.add(new_rating)

    # Commit the changes to the database
    db.session.commit()

    # Return a JSON response indicating successful rating submission
    return jsonify({'message': 'Rating submitted successfully'}), 200
