from flask import Flask, render_template

# Create the Flask application instance
app = Flask(__name__)

# Define the route for the homepage
@app.route('/')
def home():
    # Render the index.html file from the templates folder
    return render_template('index.html')

# Run the application if the script is executed directly
if __name__ == '__main__':
    # '0.0.0.0' makes the server accessible from outside the container
    # debug=True enables live reloading for development
    app.run(host='0.0.0.0', debug=True)
