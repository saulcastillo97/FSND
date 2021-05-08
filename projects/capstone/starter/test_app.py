import os
import unittest
import json

from jose import jwt
from mock import patch
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from models import setup_db, db,Actor, Movie
from app import create_app
from auth.auth import AuthError, requires_auth, verify_decode_jwt


database_name = 'capstonedb'
database_path = 'postgres://{}/{}'.format('localhost:5432', database_name)

casting_assistant_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ2MDhjMjkxYTQwMDZhNzMzZjdkIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYyMDQ4MDQ5MiwiZXhwIjoxNjIwNDg3NjkyLCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiXX0.Qd-A5CfU6w7CfkxYIAjIUvhJso21XQRyeha4m31E7OEsggZcuEWCvFzhSKhSdZGFPnAT8v5SYpdZxqdnQLPvhgo3jE6ORzUIpnmij9nv_58DNbgRRElY02_F3RCBTFKPcj6jUxmsNJ7QTU938CD-loHp0i-fhCXBUrirEwWLTlrcWiKfDu51csx5GRXI2XO79vuBKwx3rludI9Vsr_W4370ZcyICcZXqiThSPM9c8kUc2ZCSIH3FcX-kpLG5Sy-pMa_AnZt2EZqqBmhauOQ1JfnHkdKfF__9wswdcq9FPz177qmrLMAuUUR7_K37GIW5CIMXIHtI4T12b4D58q81xg'
casting_director_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ3N2UyZGQ5NTgwMDY5ODk5MDBhIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYyMDQ4MDYzMSwiZXhwIjoxNjIwNDg3ODMxLCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIiwicGF0Y2g6YWN0b3JzIiwicGF0Y2g6bW92aWVzIiwicG9zdDphY3RvcnMiXX0.YCkBwIdqTU2pFEqvC5se_vI3StU2xq-50fTH2LKM-3gyTG6QxNIbUzsy49A9NUBg-pDBMHuuPOjo98KNxfVCUhZHVLMlfot-oWuYH14Q-8yEQ_tNMCR76A7Wzp4SV6VjlQZ5Abvku3YAt5Cz5X8U0wxvLPci6soGBGEUfYl2P4tS3wQGeCHxEePkKeuEaMdgsdbmb3CDbbX6OZayuZ0hsXe1L9c4uhUivn3-EX1JfCy2TgMxnIG7PfI73N6p48XYmIYLFf05MXOXgKOKEf-3KqVmyCSbA7uXCMluCtakKJw2hNz4I0bXnGnJbFca71kqAx307RemRKaLHlsSjKbUPA'
executive_producer_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ3ZjU2MzUwNGMwMDcxZGU5OTVmIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYyMDQ4MDcxNCwiZXhwIjoxNjIwNDg3OTE0LCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImRlbGV0ZTptb3ZpZXMiLCJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyIsInBhdGNoOmFjdG9ycyIsInBhdGNoOm1vdmllcyIsInBvc3Q6YWN0b3JzIiwicG9zdDptb3ZpZXMiXX0.bYYZXkXcCi9rUWRD_X2Th2G8_x-TgMY8ycaVh62hRjNnKZmgC1gJXhris4FNz_kDhK8oYNBJEDJJSd6B0QR_SwxmwS7lGb4jsDNXqY1bDHQQpe6UcSLRVAAe8tmc43ualbAvNGJ54vWEF2Z6S5AL1HUzKRRG2lKMhxCndSEkxpRgxe9-AACnhNQSu1iuGxmTnFgHQlKWyji3AJBcJBaHOCQTiaAwXlVrxfPjgdL0-IQ3je4wmrukCdQ90MFRCyvDZbVxtJ9yJGonuY7PjgFzXctenn02o_rri7ZfHH-5VvqYR34Tz3ysaUxlHYElFxtsMigWN8_Ak7yiaMGC576PGA'

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
        self.casting_assistant_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ2MDhjMjkxYTQwMDZhNzMzZjdkIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYyMDQ4MDQ5MiwiZXhwIjoxNjIwNDg3NjkyLCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiXX0.Qd-A5CfU6w7CfkxYIAjIUvhJso21XQRyeha4m31E7OEsggZcuEWCvFzhSKhSdZGFPnAT8v5SYpdZxqdnQLPvhgo3jE6ORzUIpnmij9nv_58DNbgRRElY02_F3RCBTFKPcj6jUxmsNJ7QTU938CD-loHp0i-fhCXBUrirEwWLTlrcWiKfDu51csx5GRXI2XO79vuBKwx3rludI9Vsr_W4370ZcyICcZXqiThSPM9c8kUc2ZCSIH3FcX-kpLG5Sy-pMa_AnZt2EZqqBmhauOQ1JfnHkdKfF__9wswdcq9FPz177qmrLMAuUUR7_K37GIW5CIMXIHtI4T12b4D58q81xg'
        self.casting_director_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ3N2UyZGQ5NTgwMDY5ODk5MDBhIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYyMDQ4MDYzMSwiZXhwIjoxNjIwNDg3ODMxLCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIiwicGF0Y2g6YWN0b3JzIiwicGF0Y2g6bW92aWVzIiwicG9zdDphY3RvcnMiXX0.YCkBwIdqTU2pFEqvC5se_vI3StU2xq-50fTH2LKM-3gyTG6QxNIbUzsy49A9NUBg-pDBMHuuPOjo98KNxfVCUhZHVLMlfot-oWuYH14Q-8yEQ_tNMCR76A7Wzp4SV6VjlQZ5Abvku3YAt5Cz5X8U0wxvLPci6soGBGEUfYl2P4tS3wQGeCHxEePkKeuEaMdgsdbmb3CDbbX6OZayuZ0hsXe1L9c4uhUivn3-EX1JfCy2TgMxnIG7PfI73N6p48XYmIYLFf05MXOXgKOKEf-3KqVmyCSbA7uXCMluCtakKJw2hNz4I0bXnGnJbFca71kqAx307RemRKaLHlsSjKbUPA'
        self.executive_producer_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ3ZjU2MzUwNGMwMDcxZGU5OTVmIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYyMDQ4MDcxNCwiZXhwIjoxNjIwNDg3OTE0LCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImRlbGV0ZTptb3ZpZXMiLCJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyIsInBhdGNoOmFjdG9ycyIsInBhdGNoOm1vdmllcyIsInBvc3Q6YWN0b3JzIiwicG9zdDptb3ZpZXMiXX0.bYYZXkXcCi9rUWRD_X2Th2G8_x-TgMY8ycaVh62hRjNnKZmgC1gJXhris4FNz_kDhK8oYNBJEDJJSd6B0QR_SwxmwS7lGb4jsDNXqY1bDHQQpe6UcSLRVAAe8tmc43ualbAvNGJ54vWEF2Z6S5AL1HUzKRRG2lKMhxCndSEkxpRgxe9-AACnhNQSu1iuGxmTnFgHQlKWyji3AJBcJBaHOCQTiaAwXlVrxfPjgdL0-IQ3je4wmrukCdQ90MFRCyvDZbVxtJ9yJGonuY7PjgFzXctenn02o_rri7ZfHH-5VvqYR34Tz3ysaUxlHYElFxtsMigWN8_Ak7yiaMGC576PGA'
        setup_db(self.app, self.database_path)

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
        #movie = Movie(title='Test', release_date='11-11-1111')
        #movie.insert()
        #res = self.client().get('/movies', headers={"ROLE": "casting_assistant"})
        res = self.client().get('/movies', headers={'Authorization': 'Bearer ' + self.casting_assistant_token})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['movies'], [movie.format()])
        print()

    def test_get_actors_success(self):
        #res = self.client().get('/actors', headers=self.casting_assistant_header)
        res = self.client().get('/actors', headers={'Authorization': 'Bearer ' + self.casting_assistant_token})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        print()

    def test_get_actors_failure(self):
        res = self.client().get('/actors1-100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        print()

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
        print()

##---------------------------------------------------------------
## DELETE actor and movie Endpoint Tests
##---------------------------------------------------------------

    def test_delete_actors_success(self):
        #res = self.client().delete('/actors/1', headers=self.casting_director_header)
        res = self.client().delete('/actors/1', headers={'Authorization': 'Bearer ' + self.casting_director_token})
        data = json.loads(res.data)

        actor = Actor.query.filter(Actor.id==1).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], actor)
        print()

    def test_delete_actors_failure(self):
        res = self.client().delete('/actors/1000a')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        print()

    def test_delete_movies_success(self):
        #res = self.client().delete('/actors/1', headers=self.executive_producer_header)
        res = self.client().delete('/movies/1', headers={'Authorization': 'Bearer ' + self.executive_producer_token})
        data = json.loads(res.data)

        movie = Movie.query.filter(Movie.id==1).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], movie)
        print()

    def test_delete_movies_failure(self):
        res = self.client().delete('/movies/1000a')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        print()

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
        #res = self.client().post('/actors', headers=self.casting_director_header)
        res = self.client().post('/actors', headers={'Authorization': 'Bearer ' + self.casting_director_token}, json={'name': 'Brad'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        print()

    def test_post_actors_failure(self):
        ###res = self.client().post('/actors', headers={'ROLE':'casting_assistant'})
        ##res = self.client().post('/actors', headers={'Authorization': "Bearer {}".format(self.casting_assistant_header)}, json={"name": "ME", "age": "44", "gender":"male"})
        res = self.client().post('/actors', headers={'Authorization': 'Bearer ' + self.casting_assistant_token}, json={'name': 'ME', 'age': '44', 'gender':'male'})
        #res = self.client().post('/actors', headers=self.casting_director_header, json={'age': 31})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        print()

    def test_post_movies_success(self):
        #res = self.client().post('/movies', headers=self.executive_producer_header)
        res = self.client().post('/movies', headers={'Authorization': 'Bearer ' + self.executive_producer_token}, json={'title': 'fight night'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        print()

    def test_post_movies_failure(self):
        res = self.client().post('/movies', headers={'Authorization': 'Bearer ' + self.casting_assistant_token}, json={'title': 'fight night'})
        ##res = self.client().post('/movies', headers={'ROLE':'casting_assistant'})
        #res = self.client().post('/movies', headers=self.executive_producer_header, json={'release_date': 8-10-2000})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        print()

##---------------------------------------------------------------
## PATCH actor and movie Endpoint Tests
##---------------------------------------------------------------
    def test_patch_actors_success(self):
        res = self.client().patch('/actors/1', headers={'Authorization': 'Bearer ' + self.executive_producer_token}, json={'name': 'chris'})
        #res = self.client().patch('/actors/1', headers=self.casting_director_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        print()

    def test_patch_actors_failure(self):
        ###res = self.client().post('/actors', headers={'Authorization': "Bearer {}".format(self.casting_assistant_header)}, json={"name": "ME", "age": "44", "gender":"male"})
        res = self.client().patch('/actors/1', headers={'Authorization': 'Bearer ' + self.casting_assistant_token}, json={'name': 'chris'})
        #res = self.client().patch('/actors/1', headers=self.casting_assistant_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        print()

    def test_patch_movies_success(self):
        res = self.client().patch('/movies/1', headers={'Authorization': 'Bearer ' + self.executive_producer_token}, json={'title': 'coco'})
        #res = self.client().patch('/movies/1', headers=self.executive_producer_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        print()

    def test_patch_movies_failure(self):
        res = self.client().patch('/movies/1', headers={'Authorization': 'Bearer ' + self.casting_assistant_token}, json={'title': 'coco'})
        ##res = self.client().patch('/movies/1', headers={'ROLE':'casting_assistant'})
        #res = self.client().patch('/movies/1', headers=self.casting_assistant_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        print()

if __name__ == '__main__':
    unittest.main()
