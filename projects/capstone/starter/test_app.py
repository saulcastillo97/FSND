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

casting_assistant_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ2MDhjMjkxYTQwMDZhNzMzZjdkIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxNjc3NjUxOCwiZXhwIjoxNjE2NzgzNzE4LCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiXX0.gkX1-3rGV48pMjUnks7Ssl1uS8NRzs7PlR3DvgnIoToH389YYlH29XEL58NKtP40DpVMzyZbdQF9_nfIwFjdqv0tcZVTXDHHIDP8PAfXfqszUoEfgjnDhbZ7TvwESQ9wBqUowJEFSWOJ289QONisKJR6TD0aCkca6e5jf_JwvSTXX9l4ypqfxNtFRaInzBl9sy3D3sli-XM1hPK_Kv_t3rVifcPezQKSzGLAk1kfmH7w_JkTbRVOPDMCkTCf9khjgkWFDzqQ_CNCboMNyhPC_LLbtd6DOvYdYPV4POp8yNuGXhWxNAM29gPylr85aSm5kubdpX6UPXSGZfAheq5Oig')
casting_director_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ3N2UyZGQ5NTgwMDY5ODk5MDBhIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxNjc3NjU5NCwiZXhwIjoxNjE2NzgzNzk0LCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIiwicGF0Y2g6YWN0b3JzIiwicGF0Y2g6bW92aWVzIiwicG9zdDphY3RvcnMiXX0.bFAAyJvB4ecH9WXyjw26q9sCMdTWbxrz-VgHmG-P8ja8ILxqWZsM3wOzuu3BPIZgRivJfiyU7yV4XLSfV7iF9VjO4ox9YL3FK8mvLCvLZlOD0x-pKJZ1cpqhBL00FRBqoieXQvQP4w6E8RoLpCYboXCXapafrBiDC5pL8aRa_vMCY7e1QjiogliFws-iBL_MUYCiFFlUE_3oXuLSKchLsiCn41XX_q8phP-Rkbxo5rxpsXIXi02UMZzN_jvFbDeVF9HmmIP3ZC59pEZ1xnB_S0C146lbN9RCAUIg8-5kvGULQuG5moTro8iDcC9f7SY_NisLSIYKkKswCXKnGW_YdA')
executive_producer_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ3ZjU2MzUwNGMwMDcxZGU5OTVmIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxNjc3NjY4MSwiZXhwIjoxNjE2NzgzODgxLCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImRlbGV0ZTptb3ZpZXMiLCJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyIsInBhdGNoOmFjdG9ycyIsInBhdGNoOm1vdmllcyIsInBvc3Q6YWN0b3JzIiwicG9zdDptb3ZpZXMiXX0.JPxwR0mdMkALs43buFQgaIBGaeSWR18WoAaVHCtOKk5APAN7KDV9QUHZ6LvPTIZU5O5PSdkbJ3nE2IIzkyiL9P7SlWFByLgORuXqBwXSWOfVaZnamb438tpuZL5pVVMX3Y3tfPgqVx1nJJz4DaZaYakp7g9QljmpNLn1nMTlDgRVmmSdhKh0M7RUmTGnWoyw5TIu0V3ZTEuOLlQS1bCPya3We-kt73sgIweHHjdZsODR_DJj6q5N3yrKfoP0gwkTm3zS1Zm9-AupUTmVJ8eoyZ1HNtjMQZzdR6wyndqHHpb0dfCC-o8i5goh1hS2R2_HuMK5MBVVUAzBPS2SJALagg')

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
        self.casting_assistant_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ2MDhjMjkxYTQwMDZhNzMzZjdkIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxNjc3NjUxOCwiZXhwIjoxNjE2NzgzNzE4LCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiXX0.gkX1-3rGV48pMjUnks7Ssl1uS8NRzs7PlR3DvgnIoToH389YYlH29XEL58NKtP40DpVMzyZbdQF9_nfIwFjdqv0tcZVTXDHHIDP8PAfXfqszUoEfgjnDhbZ7TvwESQ9wBqUowJEFSWOJ289QONisKJR6TD0aCkca6e5jf_JwvSTXX9l4ypqfxNtFRaInzBl9sy3D3sli-XM1hPK_Kv_t3rVifcPezQKSzGLAk1kfmH7w_JkTbRVOPDMCkTCf9khjgkWFDzqQ_CNCboMNyhPC_LLbtd6DOvYdYPV4POp8yNuGXhWxNAM29gPylr85aSm5kubdpX6UPXSGZfAheq5Oig')
        self.casting_director_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ3N2UyZGQ5NTgwMDY5ODk5MDBhIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxNjc3NjU5NCwiZXhwIjoxNjE2NzgzNzk0LCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIiwicGF0Y2g6YWN0b3JzIiwicGF0Y2g6bW92aWVzIiwicG9zdDphY3RvcnMiXX0.bFAAyJvB4ecH9WXyjw26q9sCMdTWbxrz-VgHmG-P8ja8ILxqWZsM3wOzuu3BPIZgRivJfiyU7yV4XLSfV7iF9VjO4ox9YL3FK8mvLCvLZlOD0x-pKJZ1cpqhBL00FRBqoieXQvQP4w6E8RoLpCYboXCXapafrBiDC5pL8aRa_vMCY7e1QjiogliFws-iBL_MUYCiFFlUE_3oXuLSKchLsiCn41XX_q8phP-Rkbxo5rxpsXIXi02UMZzN_jvFbDeVF9HmmIP3ZC59pEZ1xnB_S0C146lbN9RCAUIg8-5kvGULQuG5moTro8iDcC9f7SY_NisLSIYKkKswCXKnGW_YdA')
        self.executive_producer_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ3ZjU2MzUwNGMwMDcxZGU5OTVmIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxNjc3NjY4MSwiZXhwIjoxNjE2NzgzODgxLCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImRlbGV0ZTptb3ZpZXMiLCJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyIsInBhdGNoOmFjdG9ycyIsInBhdGNoOm1vdmllcyIsInBvc3Q6YWN0b3JzIiwicG9zdDptb3ZpZXMiXX0.JPxwR0mdMkALs43buFQgaIBGaeSWR18WoAaVHCtOKk5APAN7KDV9QUHZ6LvPTIZU5O5PSdkbJ3nE2IIzkyiL9P7SlWFByLgORuXqBwXSWOfVaZnamb438tpuZL5pVVMX3Y3tfPgqVx1nJJz4DaZaYakp7g9QljmpNLn1nMTlDgRVmmSdhKh0M7RUmTGnWoyw5TIu0V3ZTEuOLlQS1bCPya3We-kt73sgIweHHjdZsODR_DJj6q5N3yrKfoP0gwkTm3zS1Zm9-AupUTmVJ8eoyZ1HNtjMQZzdR6wyndqHHpb0dfCC-o8i5goh1hS2R2_HuMK5MBVVUAzBPS2SJALagg')
        setup_db(self.app, self.database_path)



        #self.casting_assistant_header = [('Content-Type', 'application/json'), ('Authorization', f'Bearer {self.casting_assistant_token}')]
        #self.casting_director_header = [('Content-Type', 'application/json'), ('Authorization', f'Bearer {self.casting_director_token}')]
        #self.executive_producer_header = [('Content-Type', 'application/json'), ('Authorization', f'Bearer {self.executive_producer_token}')]

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
        #movie = Movie(title='Test', release_date='11-11-1111')
        #movie.insert()
        #res = self.client().get('/movies', headers={"ROLE": "casting_assistant"})
        res = self.client().get('/movies', headers={'Authorization': 'Bearer ' + self.casting_assistant_token})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['movies'], [movie.format()])

    def test_get_actors_success(self):
        #res = self.client().get('/actors', headers=self.casting_assistant_header)
        res = self.client().get('/actors', headers={'Authorization': 'Bearer ' + self.casting_assistant_token})
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
        #res = self.client().delete('/actors/1', headers=self.casting_director_header)
        res = self.client().delete('/actors/1', headers={'Authorization': 'Bearer ' + self.casting_director_token})
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
        #res = self.client().delete('/actors/1', headers=self.executive_producer_header)
        res = self.client().delete('/movies/1', headers={'Authorization': 'Bearer ' + self.executive_producer_token})
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
        res = self.client().post('/movies', headers={'Authorization': 'Bearer ' + self.executive_producer_token}, json={'title': 'fight night'})
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
        res = self.client().patch('/actors/1', headers={'Authorization': 'Bearer ' + self.executive_producer_token}, json={'name': 'chris'})
        #res = self.client().patch('/actors/1', headers=self.casting_director_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_patch_actors_failure(self):
        ###res = self.client().post('/actors', headers={'Authorization': "Bearer {}".format(self.casting_assistant_header)}, json={"name": "ME", "age": "44", "gender":"male"})
        res = self.client().patch('/actors/1', headers={'Authorization': 'Bearer ' + self.casting_assistant_token}, json={'name': 'chris'})
        #res = self.client().patch('/actors/1', headers=self.casting_assistant_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)

    def test_patch_movies_success(self):
        res = self.client().patch('/movies/1', headers={'Authorization': 'Bearer ' + self.executive_producer_token}, json={'title': 'coco'})
        #res = self.client().patch('/movies/1', headers=self.executive_producer_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_patch_movies_failure(self):
        res = self.client().patch('/movies/1', headers={'Authorization': 'Bearer ' + self.casting_assistant_token}, json={'title': 'coco'})
        ##res = self.client().patch('/movies/1', headers={'ROLE':'casting_assistant'})
        #res = self.client().patch('/movies/1', headers=self.casting_assistant_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)

if __name__ == '__main__':
    unittest.main()
