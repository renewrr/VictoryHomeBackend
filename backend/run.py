from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(port=8002, debug=True, ssl_context='adhoc')
