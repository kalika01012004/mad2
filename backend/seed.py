from models import db, User


def init_db_and_seed(app, seed_demo_data=False):
    with app.app_context():
        db.create_all()

        admin = User.query.filter_by(role="admin").first()
        if not admin:
            admin = User(
