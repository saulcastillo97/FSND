import os
import unittest
import json

from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from models import setup_db, db,Actor, Movie
from app import create_app
from auth.auth import AuthError, requires_auth, verify_decode_jwt

#load_dotenv()

database_name = 'capstonedb'
database_path = 'postgres://{}/{}'.format('localhost:5432', database_name)

casting_assistant_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ2MDhjMjkxYTQwMDZhNzMzZjdkIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxMzUwMTc0NywiZXhwIjoxNjEzNTA4OTQ3LCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiXX0.GIvpeB0w8b9UmiN80WmzovGq3h60z3Sy0XElOrQxL_po73y-d7Q7YQAEk3nStGL5QQ78-gOvwT9BuPun6UzGbNnt5f0WLEWlC_3Av10ZhTrObDGVKJRvWUJ7ea1f-g9W075hPiUGCXhiFtjcmMG3vTZDj3iyeTZgzG6z6gxMZbRVoLAX0iLv4YlW1KY1a_nXTc-dAwQCJLbei4U4HqbH630k6ep5SqAgqPUtr3grjtowkDiLhWATGdG4x-Xjd1GuGXGFdiJirlMvALRk2e31IzCuf0_Nu7yZt_TK_YD5MzSnfWE8hDAJ9qTnMgk5yqmgODVhPcmpBRNpQ7tYHowg7Q')
casting_director_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ3N2UyZGQ5NTgwMDY5ODk5MDBhIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxMzUwMTk4NywiZXhwIjoxNjEzNTA5MTg3LCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIiwicGF0Y2g6YWN0b3JzIiwicGF0Y2g6bW92aWVzIiwicG9zdDphY3RvcnMiXX0.VWegbnQLuHckEcG7W5aBz1JKa0YLIYyR7MWgcshMtWs5eTzJsb1dy2my67AI06zM_5WlaHxYXBnlEW11HpEgEq6a0gxU4AJ65zwfCT2kAwWs3O-05UFiDEd-UsyJVkUwWIk64nIficzOBZKWiX9Dv41gFk-qOhDQLEfwY-eF9vK4sNC1H6r39SDgBbHYN34T1P6Jxn5U6hmYkZvodBcrcU58c96YSewCguHA3lg7oQIcmUn0au3A5mJ6xhE1OCv_ZSC6OG-aOt1Jq5DI7_YSslvM2qAscwNUsWP5J49i-feQ0oNQr8b0NL2oYRxyd-xEIfYAJ8p4T5klwNpSreFTeQ')
executive_producer_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ3ZjU2MzUwNGMwMDcxZGU5OTVmIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxMzUwMjA5NSwiZXhwIjoxNjEzNTA5Mjk1LCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImRlbGV0ZTptb3ZpZXMiLCJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyIsInBhdGNoOmFjdG9ycyIsInBhdGNoOm1vdmllcyIsInBvc3Q6YWN0b3JzIiwicG9zdDptb3ZpZXMiXX0.EhsfvAef7k6StSx7UfE1h4hClev0p0XLTgfwiRraXcwnS4ECMOEN5n9x-rlFTwbdZJYHaNMwsT5gCOoUEhvRaLT83jb8_B2qYCj7T2Fz3ePf6icGgQhJ25lHXDBUXDRz98YE_JKcC88aUJC9h-CWYWusJGpiWaW_M9NOm9d-rIHxgZiOIYMkCrmu0oYe7qc0SJiSshnWac6DU4NJoGt07hzBIFVKIktvk2hJ6W9oswxCnG5JfDqw_x0sJSmYW2W5nntLiRCQ1VMMcswImZlwiNwM0_0C36-ExG7GUNC1N3uVOaPem8S5Jt5xOZ2p8JRsbN7nx7B5b6BYe3UJa1AwUg')


class CapstoneTestCase(unittest.TestCase):
    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = 'capstonedb'
        self.database_path = 'postgres://{}/{}'.format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        casting_assistant_header = {'Authorization': 'Bearer ' + self.casting_assistant_token}
        casting_director_header = {'Authorization': 'Bearer ' + self.casting_director_token}
        executive_producer_header = {'Authorization': 'Bearer ' + self.executive_producer_token }

        self.new_actor = {
            'name': 'Brad Pitt',
            'age': '57',
            'gender': 'Male'
        }

        self.new_movie = {
            'title': 'Fight Club',
            'release_date': '09-10-1999'
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self, app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass
##---------------------------------------------------------------
## GET actor and movie Endpoint Tests
##---------------------------------------------------------------
    def test_get_actors_success(self):
        res = self.client().get('/actors')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_get_actors_failure(self):
        res = self.client().get('/actors1-100')
        data = json.loads(res.data)

        self.asserEqual(res.status_code, 404)
        self.assertEqual(data['successs'], False)

    def test_get_movies_success(self):
        res = self.client().get('/movies')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_get_movies_failure(self):
        res = self.client().get('/movies1-100')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], False)

##---------------------------------------------------------------
## DELETE actor and movie Endpoint Tests
##---------------------------------------------------------------

    def test_delete_actors_success(self):
        res = self.client().delete('/actors/1', headers = casting_director_header)
        data = json.laods(res.data)

        actor = Actor.query.filter(Actor.id==1).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], actor)

    def test_delete_actors_failure(self):
        res = self.client().delete('/actors/1000')

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_delete_movies_success(self):
        res = self.client().delete('/actors/1', headers = executive_producer_header)
        data = json.laods(res.data)

        movie = Movie.query.filter(Movie.id==1).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], movie)

    def test_delete_movies_failure(self):
        res = self.client().delete('/movies/1000')

        self.assertEqual(res.stauts_code, 404)
        self.assertEqual(data['success'], False)

##---------------------------------------------------------------
## POST actor and movie Endpoint Tests
##---------------------------------------------------------------

    def test_post_actors_success(self):
        res = self.client().post('/actors', headers = casting_director_header)
        data = json.laods(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_post_actors_failure(self):
        res = self.client().delete('/actors', headers = casting_director_header, json = json.loads['release_date': '08-10-2000'])

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

    def test_post_movies_success(self):
        res = self.client().post('/movies', headers = executive_producer_header)
        data = json.laods(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_post_movies_failure(self):
        res = self.client().delete('/movies', headers = executive_producer_header, json = json.loads['age': '31'])

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

##---------------------------------------------------------------
## PATCH actor and movie Endpoint Tests
##---------------------------------------------------------------
    def test_patch_actors_success(self):
        res = self.client().patch('/actors/1', headers = casting_director_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_patch_actors_failure(self):
        res = self.client().patch('/actors/1', headers = casting_assistant_header)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)

    def test_patch_movies_success(self):
        res = self.client().patch('/movies/1', headers = executive_producer_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_patch_movies_failure(self):
        res = self.client().patch('/movies/1a', headers = casting_assistant_header)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)

if __name__ == '__main__':
    unittest.main()
