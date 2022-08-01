import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

from models import db, User, Cocktail, Favorites
from forms import RegisterUserForm, SignInForm

os.environ['DATABASE_URL'] = "postgresql:///cocktail_please-test"

from app import app, login, logout

class TestingUtilRoutes(TestCase):
    def setUp(self):
        self.client = app.test_client()
        User.query.delete()
        Cocktail.query.delete()
        Favorites.query.delete()

        self.testuser = User.signup(username="testuser",
        email="test@test.com",
        password="testuser")

        db.session.commit()

    

class TestingUserRoutes(TestCase):
    def setUp(self):
        db.session.rollback()
        self.client = app.test_client()
        User.query.delete()
        Cocktail.query.delete()
        Favorites.query.delete()

        db.session.commit()

        

        self.testuser = User.signup(username="testuser",
        email="test@test.com",
        password="testuser")


        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['curr_user']=self.testuser.id

    def tearDown(self):
        db.session.rollback()

    def authTest(self, url):
        with self.client as c:
            resp = c.get(url,follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
    
    def test_homepage(self):
        with self.client as c:
            resp = c.get("/",follow_redirects=True)
            html1 = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            with c.session_transaction() as session:
                login(self.testuser)
            resp = c.get("/",follow_redirects=True)
            html2 = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)

    def test_delete_user(self):
        with self.client as c:
            
            resp = c.get("/users/profile/password",follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            resp = c.post("/users/profile/delete",follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Your account has been deleted", html)


class TestingCocktailRoutes(TestCase):
    def SetUp(self):
        db.session.rollback()
        self.client = app.test_client()
        User.query.delete()
        Cocktail.query.delete()
        Favorites.query.delete()

        db.session.commit()
    
    def test_random_cocktail(self):
        with self.client as c:
            resp = c.get('/radom', follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Login to favorite cocktails', html)
            