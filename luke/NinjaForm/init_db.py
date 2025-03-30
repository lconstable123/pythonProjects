from NF import db, app

with app.app_context():
    db.drop_all()  # Drop all tables (be careful, this deletes all data)
    print("Database dropped!")
    db.create_all()  # Recreate all tables based on your models
    print("Database initialized!")