import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    # Port 5000 collides with macOS AirPlay Receiver, which grabs it opportunistically
    # whenever it's free — default to 5001 locally instead.
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, port=port)
