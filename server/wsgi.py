from webapp import app as application

if __name__ == "__main__":
    print("Starting server...")
    application.run(debug=True)