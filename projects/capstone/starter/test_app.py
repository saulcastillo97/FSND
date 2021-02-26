import os
import unittest
import json

from mock import patch
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from models import setup_db, db,Actor, Movie
from app import create_app
from auth.auth import AuthError, requires_auth, verify_decode_jwt


database_name = 'capstonedb'
database_path = 'postgres://{}/{}'.format('localhost:5432', database_name)

casting_assistant_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ2MDhjMjkxYTQwMDZhNzMzZjdkIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxNDM3MTQ4NCwiZXhwIjoxNjE0Mzc4Njg0LCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiXX0.W4asu3dNKL-Gs3knBBMS1Kixg7yl0uD30TGhBjD_q9oyQ3CiCqBNXWjyQM07SV5Jw9hGXHmj4GmR9z8ADDUoUjQ-lgwdEM1IqktlYeQ24fPJee1YiGgO_Kx2trEia7aVEOpyRcCcXSkzZw76Igu6vhzknbnLjSIQXYO8wQmzWZ_ncX1iV5S2_6LEVP5vEc0ATlA4s_guwgxWvjpC0SWf2E42oTUjmLUWJ0r-Pfi5oFWaHllvAREi0ZvFNpBnx53Q0GOEUiHVIOS1jIGoP8l4Ep5aWH29iKaVXHL6U1XttBhArKgf70wu4Rjn8uUYnj7n8itDbMNlwhNYyxLCawZf8w')
casting_director_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ3N2UyZGQ5NTgwMDY5ODk5MDBhIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxNDM3MTYzNSwiZXhwIjoxNjE0Mzc4ODM1LCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIiwicGF0Y2g6YWN0b3JzIiwicGF0Y2g6bW92aWVzIiwicG9zdDphY3RvcnMiXX0.s3o_FlRsh37HdWPOZvh3eB4th43ckCG1o-ECesKBgKocdtoWuyDsyYQBlihGnxKzGjtzrCRa73fDvmiK2ErhNvwb2antRzYGqVVPvLk9FkU0wmpQzl1LItYwr5laNtRp7JO-J4_5MPgrqky-akIcknaeA44hNL1BLol4DOA4jBtWjjBiRC_zr59hin4nsyIbXzIGQCkga41FhSatntphmrptTSrhHBkHsvX1ZHTaIsVXm_qgsWtubtSLxS4EjmChp9aVw2HWugGPv7kW3Nd6qXCWrSu_MhksvNORL1-0nirZTq50H4hZ2WDVyi4L8HBi9qDrWKUsSLaL9OwaJVdP7w')
executive_producer_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ3ZjU2MzUwNGMwMDcxZGU5OTVmIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxNDM3MTcxNCwiZXhwIjoxNjE0Mzc4OTE0LCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImRlbGV0ZTptb3ZpZXMiLCJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyIsInBhdGNoOmFjdG9ycyIsInBhdGNoOm1vdmllcyIsInBvc3Q6YWN0b3JzIiwicG9zdDptb3ZpZXMiXX0.a1U4M1AnHm9TMI2HSShgwDnTaI3So4AfNAmz8Kdo7a_fuU32FPid5BSmVz27bWjGojDw-LyhcpQHe-Toy2P3iWLK2Z_VNI7YhfefMMzy1WHDS9Mc_uhhKNUkMTmP5cwx9nN5_WExvQTaQs7CWvYN0CSbYbqhTEdlfpiM9dYvabttYY7YMO0Kq9dq8S0DOsNndKVoZX_CzH2koUiMFAV_OtHZ5RFTun4zvj3Ea6l1sb7iecG1WGTD_MnC2wLZ6GG_x5etKOtnCNb15udeStIdnswp4mONvKu7Jmmyo_76MhZdI_sWETDGz6wz359x_zFx70w90QrEKBxWTlTpmSS9UQ')

ROLES = {
    "casting_assistant": {
        "permissions": [
            "get:movies",
            "get:actors"
        ]
    },
    "casting_director": {
        "permissions": [
            "get:movies",
            "get:actors",
            "post:actors",
            "delete:actors",
            "patch:movies",
            "patch:actors"
        ]
    },
    "executive_producer": {
        "permissions": [
            "get:movies",
            "get:actors",
            "post:actors",
            "delete:actors",
            "patch:movies",
            "patch:actors",
            "post:movies",
            "delete:movies"
        ]
    }
}

def mock_requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            role_name = request.headers.get("ROLE", None)
            if role_name is None:
                raise AuthError({
                    'code': 'auth_header_missing',
                    'description': 'Authorization header is expected'
                }, 401)
            payload = {
                "permissions": ROLES[role_name]["permissions"]
            }
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator

patch('auth.auth.requires_auth', mock_requires_auth).start()

class CapstoneTestCase(unittest.TestCase):
    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = 'capstonedb'
        self.database_path = 'postgres://{}/{}'.format('localhost:5432', self.database_name)
        self.casting_assistant_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ2MDhjMjkxYTQwMDZhNzMzZjdkIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxNDM3MTQ4NCwiZXhwIjoxNjE0Mzc4Njg0LCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiXX0.W4asu3dNKL-Gs3knBBMS1Kixg7yl0uD30TGhBjD_q9oyQ3CiCqBNXWjyQM07SV5Jw9hGXHmj4GmR9z8ADDUoUjQ-lgwdEM1IqktlYeQ24fPJee1YiGgO_Kx2trEia7aVEOpyRcCcXSkzZw76Igu6vhzknbnLjSIQXYO8wQmzWZ_ncX1iV5S2_6LEVP5vEc0ATlA4s_guwgxWvjpC0SWf2E42oTUjmLUWJ0r-Pfi5oFWaHllvAREi0ZvFNpBnx53Q0GOEUiHVIOS1jIGoP8l4Ep5aWH29iKaVXHL6U1XttBhArKgf70wu4Rjn8uUYnj7n8itDbMNlwhNYyxLCawZf8w')
        self.casting_director_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ3N2UyZGQ5NTgwMDY5ODk5MDBhIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxNDM3MTYzNSwiZXhwIjoxNjE0Mzc4ODM1LCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIiwicGF0Y2g6YWN0b3JzIiwicGF0Y2g6bW92aWVzIiwicG9zdDphY3RvcnMiXX0.s3o_FlRsh37HdWPOZvh3eB4th43ckCG1o-ECesKBgKocdtoWuyDsyYQBlihGnxKzGjtzrCRa73fDvmiK2ErhNvwb2antRzYGqVVPvLk9FkU0wmpQzl1LItYwr5laNtRp7JO-J4_5MPgrqky-akIcknaeA44hNL1BLol4DOA4jBtWjjBiRC_zr59hin4nsyIbXzIGQCkga41FhSatntphmrptTSrhHBkHsvX1ZHTaIsVXm_qgsWtubtSLxS4EjmChp9aVw2HWugGPv7kW3Nd6qXCWrSu_MhksvNORL1-0nirZTq50H4hZ2WDVyi4L8HBi9qDrWKUsSLaL9OwaJVdP7w')
        self.executive_producer_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ3ZjU2MzUwNGMwMDcxZGU5OTVmIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxNDM3MTcxNCwiZXhwIjoxNjE0Mzc4OTE0LCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImRlbGV0ZTptb3ZpZXMiLCJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyIsInBhdGNoOmFjdG9ycyIsInBhdGNoOm1vdmllcyIsInBvc3Q6YWN0b3JzIiwicG9zdDptb3ZpZXMiXX0.a1U4M1AnHm9TMI2HSShgwDnTaI3So4AfNAmz8Kdo7a_fuU32FPid5BSmVz27bWjGojDw-LyhcpQHe-Toy2P3iWLK2Z_VNI7YhfefMMzy1WHDS9Mc_uhhKNUkMTmP5cwx9nN5_WExvQTaQs7CWvYN0CSbYbqhTEdlfpiM9dYvabttYY7YMO0Kq9dq8S0DOsNndKVoZX_CzH2koUiMFAV_OtHZ5RFTun4zvj3Ea6l1sb7iecG1WGTD_MnC2wLZ6GG_x5etKOtnCNb15udeStIdnswp4mONvKu7Jmmyo_76MhZdI_sWETDGz6wz359x_zFx70w90QrEKBxWTlTpmSS9UQ')
        setup_db(self.app, self.database_path)

        self.casting_assistant_header = [('Content-Type', 'application/json'), ('Authorization', f'Bearer {self.casting_assistant_token}')]
        self.casting_director_header = [('Content-Type', 'application/json'), ('Authorization', f'Bearer {self.casting_director_token}')]
        self.executive_producer_header = [('Content-Type', 'application/json'), ('Authorization', f'Bearer {self.executive_producer_token}')]

        #self.casting_assistant_header = {'Authorization': 'Bearer ' + self.casting_assistant_token}
        #self.casting_director_header = {'Authorization': 'Bearer ' + self.casting_director_token}
        #self.executive_producer_header = {'Authorization': 'Bearer ' + self.executive_producer_token }

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
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass
##---------------------------------------------------------------
## GET actor and movie Endpoint Tests
##---------------------------------------------------------------

    def test_get_movies_success(self):
        movie = Movie(title='Test', release_date='11-11-1111')
        movie.insert()
        res = self.client().get('/movies', headers={"ROLE": "casting_assistant"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['movies'], [movie.format()])

    def test_get_actors_success(self):
        res = self.client().get('/actors', headers=self.casting_assistant_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_get_actors_failure(self):
        res = self.client().get('/actors1-100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    #def test_get_movies_success(self):
    #    res = self.client().get('/movies', headers=self.casting_assistant_header)
    #    data = json.loads(res.data)

    #    self.assertEqual(res.status_code, 200)
    #    self.assertEqual(data['success'], True)

    def test_get_movies_failure(self):
        res = self.client().get('/movies1-100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

##---------------------------------------------------------------
## DELETE actor and movie Endpoint Tests
##---------------------------------------------------------------

    def test_delete_actors_success(self):
        res = self.client().delete('/actors/1', headers=self.casting_director_header)
        data = json.loads(res.data)

        actor = Actor.query.filter(Actor.id==1).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], actor)

    def test_delete_actors_failure(self):
        res = self.client().delete('/actors/1000a')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_delete_movies_success(self):
        res = self.client().delete('/actors/1', headers=self.executive_producer_header)
        data = json.loads(res.data)

        movie = Movie.query.filter(Movie.id==1).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], movie)

    def test_delete_movies_failure(self):
        res = self.client().delete('/movies/1000a')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

##---------------------------------------------------------------
## POST actor and movie Endpoint Tests
##---------------------------------------------------------------

    def test_post_actors_success(self):
        #res = self.client().post('/actors', headers={
        #    'Authorization':"Bearer {}".format(self.casting_director_token)
        #}, json = {
        #    "name": "test",
        #    "age":"test",
        #    "gender":"test"
        #})
        #res = self.client().post('/actors', headers={'ROLE':'casting_director'})
        res = self.client().post('/actors', headers=self.casting_director_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_post_actors_failure(self):
        res = self.client().post('/actors/1', headers={'ROLE':'casting_assistant'})
        #res = self.client().post('/actors', headers=self.casting_director_header, json={'age': 31})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

    def test_post_movies_success(self):
        res = self.client().post('/movies', headers=self.executive_producer_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_post_movies_failure(self):
        res = self.client().post('/movies/1', headers={'ROLE':'casting_assistant'})
        #res = self.client().post('/movies', headers=self.executive_producer_header, json={'release_date': 8-10-2000})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

##---------------------------------------------------------------
## PATCH actor and movie Endpoint Tests
##---------------------------------------------------------------
    def test_patch_actors_success(self):
        res = self.client().patch('/actors/1', headers=self.casting_director_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_patch_actors_failure(self):
        res = self.client().patch('/actors/1', headers=self.casting_assistant_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)

    def test_patch_movies_success(self):
        res = self.client().patch('/movies/1', headers=self.executive_producer_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_patch_movies_failure(self):
        res = self.client().patch('/movies/1', headers={'ROLE':'casting_assistant'})
        #res = self.client().patch('/movies/1', headers=self.casting_assistant_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)

if __name__ == '__main__':
    unittest.main()
