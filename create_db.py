from app import app, db, User
from werkzeug.security import generate_password_hash

# Activate the app context
with app.app_context():
    print("⚙️ Checking and creating tables if they don't exist...")

    db.create_all()  # ✅ Only creates missing tables, doesn't delete anything

    # Check if admin already exists
    admin_email = "admin@quizmaster.com"
    admin_password = "admin123"

    admin_user = User.query.filter_by(email=admin_email).first()

    if not admin_user:
        # If admin doesn't exist, create one
        admin_user = User(
            email=admin_email,
            password=generate_password_hash(admin_password),
            full_name="Admin",
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print(f"✅ Admin user created: {admin_email} / {admin_password}")
    else:
        print(f"ℹ️ Admin user already exists: {admin_email}")

    print("✅ Database setup complete!")

