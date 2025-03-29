#entry point for app
from website import create_app

app = create_app()

if __name__ == "__main__": #only runs web server if this file is run directly
    app.run(debug = True) #runs server and debug = True means any change to the code will update the server (will be turned off once up)
