from app import app, init_database

# Initialize database when the module is imported
init_database()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
