# Import the create_app function from the website module
from website import create_app

# Create an instance of the Flask application using the create_app function
app = create_app()

# Check if the script is being run directly
if __name__ == '__main__':
    # Run the application in debug mode (automatically updates the application when changes are made)
    app.run(debug=True)
