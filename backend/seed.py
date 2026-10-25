from models import db, User


def init_db_and_seed(app, seed_demo_data=False):
    with app.app_context():
        db.create_all()

        admin = User.query.filter_by(role="admin").first()
        if not admin:
            admin = User(
                name="Administrator",
                email="admin@emp.edu",
                username="admin",
                role="admin",
                contact_details="",
                department="Examination Office",
                status="Active",
            )
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
