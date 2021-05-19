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

casting_assistant_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ2MDhjMjkxYTQwMDZhNzMzZjdkIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYyMTQzNTYyNSwiZXhwIjoxNjIxNDQyODI1LCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiXX0.L7hVNd-P_AB1tALD5tnJape6ycYanWtInfh09YW9MzmyaV3SVGfIJH0qdmiGyWn4Ni9BP5XMb8iUXkXMWy0fjm-7B8F_myesRg1vxubxudbgBuKD_rHJf_kDtUnf_6dtQNW3HjOReGMf4AhD-i1Fi5HmBa9AGU-R8hNOwlKVIki7GhORguhQgZb4WfeQWld5-7Gi2-pkHADg0R_zIDf_RkOiuCZzlvN8klKwaKcGdU7AZz2eq4aIQALTipELWmX5mZ0tDYcGD8NaO3itcSg4u1RvgIkZfwEw1d0xafyZ-CqNjSsLKHSTY_Bur9Eumfq8Vbg7m7Dg6eMGcEBwBE4JTw'
casting_director_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ3N2UyZGQ5NTgwMDY5ODk5MDBhIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYyMTQzNTY5NCwiZXhwIjoxNjIxNDQyODk0LCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIiwicGF0Y2g6YWN0b3JzIiwicGF0Y2g6bW92aWVzIiwicG9zdDphY3RvcnMiXX0.VRyr8DWyePJzIQCYzjtxsdPzde7fRER7nOfZldNuKtK4fQpsGLt0HamvBtQVy2fCJYDAzI392ax0QFHrpPEOjWuzhyBjVif9seHg8IUtAI8RZj6hV3KV-4NcBJS9NwN0b7_zohwb14CfY84vtWbi3J8X2UvXk7pcDi0t6dH9kTSj2t2zzDr2_s3TrKRmVAMhBl6YOAJLHyQOSue6c3zrsOttBR8lwhc5yZZ62d8JiZcoydSxodHeH8p31cgi2YTbj26ouEj7j_IdMExC3LDm5_gmKLe3GC1BSo_FooujDWqah3d9VMcwHgfvvjSRKejXbIaImej-TAkhog6oJ9w83g'
executive_producer_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ3ZjU2MzUwNGMwMDcxZGU5OTVmIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYyMTQzNTc1NSwiZXhwIjoxNjIxNDQyOTU1LCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImRlbGV0ZTptb3ZpZXMiLCJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyIsInBhdGNoOmFjdG9ycyIsInBhdGNoOm1vdmllcyIsInBvc3Q6YWN0b3JzIiwicG9zdDptb3ZpZXMiXX0.tZo-R9dvuqKV6onAxZXKhje4DkFiw-JL_rrcDZ_0jxFlRJe1ro2BAr_BgngQDa27N3c0Tr7qnD_nvgb5HovhrqIU4YcNIFHV1iwHzRMxNIk-kEUhCIkJKVowIxMsV5kt_F1QG3nIEtbDNX6uU9c2Jh8CZH0T5g7R02jVrQXBAsL76favJxpu60urOQWKSY0ubSnNwaVuP34EiX3-rxNuB8CgTgZQsTd8WFf3WGLf30uibl6Pym_e3_Rlfc-02pYI0tEbzJAM3Mjfsj8xUxgaOpj8Y0mKyD9CNVPH9iAlJQPYvAZSaJjCH5VzXfRZrZs7eoJO8egFqMl7BexLzViAKA'

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
        self.casting_assistant_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ2MDhjMjkxYTQwMDZhNzMzZjdkIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYyMTQzNTYyNSwiZXhwIjoxNjIxNDQyODI1LCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiXX0.L7hVNd-P_AB1tALD5tnJape6ycYanWtInfh09YW9MzmyaV3SVGfIJH0qdmiGyWn4Ni9BP5XMb8iUXkXMWy0fjm-7B8F_myesRg1vxubxudbgBuKD_rHJf_kDtUnf_6dtQNW3HjOReGMf4AhD-i1Fi5HmBa9AGU-R8hNOwlKVIki7GhORguhQgZb4WfeQWld5-7Gi2-pkHADg0R_zIDf_RkOiuCZzlvN8klKwaKcGdU7AZz2eq4aIQALTipELWmX5mZ0tDYcGD8NaO3itcSg4u1RvgIkZfwEw1d0xafyZ-CqNjSsLKHSTY_Bur9Eumfq8Vbg7m7Dg6eMGcEBwBE4JTw'
        self.casting_director_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ3N2UyZGQ5NTgwMDY5ODk5MDBhIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYyMTQzNTY5NCwiZXhwIjoxNjIxNDQyODk0LCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIiwicGF0Y2g6YWN0b3JzIiwicGF0Y2g6bW92aWVzIiwicG9zdDphY3RvcnMiXX0.VRyr8DWyePJzIQCYzjtxsdPzde7fRER7nOfZldNuKtK4fQpsGLt0HamvBtQVy2fCJYDAzI392ax0QFHrpPEOjWuzhyBjVif9seHg8IUtAI8RZj6hV3KV-4NcBJS9NwN0b7_zohwb14CfY84vtWbi3J8X2UvXk7pcDi0t6dH9kTSj2t2zzDr2_s3TrKRmVAMhBl6YOAJLHyQOSue6c3zrsOttBR8lwhc5yZZ62d8JiZcoydSxodHeH8p31cgi2YTbj26ouEj7j_IdMExC3LDm5_gmKLe3GC1BSo_FooujDWqah3d9VMcwHgfvvjSRKejXbIaImej-TAkhog6oJ9w83g'
        self.executive_producer_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ3ZjU2MzUwNGMwMDcxZGU5OTVmIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYyMTQzNTc1NSwiZXhwIjoxNjIxNDQyOTU1LCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImRlbGV0ZTptb3ZpZXMiLCJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyIsInBhdGNoOmFjdG9ycyIsInBhdGNoOm1vdmllcyIsInBvc3Q6YWN0b3JzIiwicG9zdDptb3ZpZXMiXX0.tZo-R9dvuqKV6onAxZXKhje4DkFiw-JL_rrcDZ_0jxFlRJe1ro2BAr_BgngQDa27N3c0Tr7qnD_nvgb5HovhrqIU4YcNIFHV1iwHzRMxNIk-kEUhCIkJKVowIxMsV5kt_F1QG3nIEtbDNX6uU9c2Jh8CZH0T5g7R02jVrQXBAsL76favJxpu60urOQWKSY0ubSnNwaVuP34EiX3-rxNuB8CgTgZQsTd8WFf3WGLf30uibl6Pym_e3_Rlfc-02pYI0tEbzJAM3Mjfsj8xUxgaOpj8Y0mKyD9CNVPH9iAlJQPYvAZSaJjCH5VzXfRZrZs7eoJO8egFqMl7BexLzViAKA'
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
        #self.assertEqual(data['deleted'], actor)
        print()

    def test_delete_actors_failure(self):
        res = self.client().delete('/actors/1000a')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        print()

    def test_delete_movies_success(self):
        #res = self.client().delete('/actors/1', headers=self.executive_producer_header)
        res = self.client().delete('/movies/2', headers={'Authorization': 'Bearer ' + self.executive_producer_token})
        data = json.loads(res.data)

        movie = Movie.query.filter(Movie.id==2).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        #self.assertEqual(data['deleted'], movie)
        print()

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
        #res = self.client().post('/actors', headers=self.casting_director_header)
        res = self.client().post('/actors', headers={'Authorization': 'Bearer ' + self.casting_director_token}, json={'name': 'Brad'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_post_actors_failure(self):
        ###res = self.client().post('/actors', headers={'ROLE':'casting_assistant'})
        ##res = self.client().post('/actors', headers={'Authorization': "Bearer {}".format(self.casting_assistant_header)}, json={"name": "ME", "age": "44", "gender":"male"})
        res = self.client().post('/actors', headers={'Authorization': 'Bearer ' + self.casting_assistant_token}, json={'name': 'ME', 'age': '44', 'gender':'male'})
        #res = self.client().post('/actors', headers=self.casting_director_header, json={'age': 31})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)

    def test_post_movies_success(self):
        #res = self.client().post('/movies', headers=self.executive_producer_header)
        res = self.client().post('/movies', headers={'Authorization': 'Bearer ' + self.executive_producer_token}, json={'title': 'fight night', 'release_date': '1111-11-11 00:00:00'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_post_movies_failure(self):
        res = self.client().post('/movies', headers={'Authorization': 'Bearer ' + self.casting_assistant_token}, json={'title': 'fight night'})
        ##res = self.client().post('/movies', headers={'ROLE':'casting_assistant'})
        #res = self.client().post('/movies', headers=self.executive_producer_header, json={'release_date': 8-10-2000})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)

##---------------------------------------------------------------
## PATCH actor and movie Endpoint Tests
##---------------------------------------------------------------
    def test_patch_actors_success(self):
        res = self.client().patch('/actors/1', headers={'Authorization': 'Bearer ' + self.executive_producer_token}, json={'name': 'Me', 'age': '44', 'gender':'male'})
        #res = self.client().patch('/actors/1', headers=self.casting_director_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_patch_actors_failure(self):
        ###res = self.client().post('/actors', headers={'Authorization': "Bearer {}".format(self.casting_assistant_header)}, json={"name": "ME", "age": "44", "gender":"male"})
        res = self.client().patch('/actors/2', headers={'Authorization': 'Bearer ' + self.casting_assistant_token}, json={'name': 'chris'})
        #res = self.client().patch('/actors/1', headers=self.casting_assistant_header)
        data = json.loads(res.data)
        print('DATA VARIABLE IS:', data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)

    def test_patch_movies_success(self):
        res = self.client().patch('/movies/3', headers={'Authorization': 'Bearer ' + self.executive_producer_token}, json={'title': 'coco'})
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
