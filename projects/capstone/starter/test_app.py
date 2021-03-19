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

casting_assistant_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ2MDhjMjkxYTQwMDZhNzMzZjdkIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxNjE4NTE2OSwiZXhwIjoxNjE2MTkyMzY5LCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiXX0.U9UupjXpv_XLvXrlaCCwzWJim9mW9ddvXxYEq22skwtff3b3H7Dz9RXrrpNXLYSB197geEITt4d-oiGsJ6D9zHxtt6QGowyf8QR3r12LCOdZJI82DvVWCfdEcp_vb11Jm2JoTrn1OWHdSLKxQyzsVmdTdXoSNiqRFg1WYyuel3JKaRd5V83BFJuOeDzefhjc-O1Jnny_rX5DSQMAuAIVy_DjW2QM67vE2eL_Ilrfrx0imIMjpS6IoQsuB6bqtSdhbPBohUEDBZrNKdFADOKuINDDzMt3BGQoudlcqg9tFxcJDLoXwp-XbhXVhkhLZwB60aFvh8vosXOOx5nzowZKsw')
casting_director_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ3N2UyZGQ5NTgwMDY5ODk5MDBhIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxNjE4NTIzMCwiZXhwIjoxNjE2MTkyNDMwLCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIiwicGF0Y2g6YWN0b3JzIiwicGF0Y2g6bW92aWVzIiwicG9zdDphY3RvcnMiXX0.LWvnR_Z3zCAQ1Y24rMgY7uFzlsKIhnbEhYUydkhVL7OZlWX2MKYqQTSbGsSwr7NHqbft-EFfh36W0czKt0HZT2QOXbR_6ScSUpP6oRF0mi71csYwe7oxVLqG2hk4SK-FKg-9eS_wdNDiW8lZ19jdjwwyXn7m6iWNdGTd6HqregTsTkzv32n6z9hRpJZBQOy-QbkJceak0vCbc2x9PhHSJuWW86fV77vwgOu-oLphis93O3Q5rCpZK5qD_orMhVNpfrmDXbgwoC-Mb0ySLbfZK74bPUS_snZjdru-zfdGcDRA52rU8bK8mW55zuDFSCu4PdlMFEaKZz9RzW1FjgUXhA')
executive_producer_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ3ZjU2MzUwNGMwMDcxZGU5OTVmIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxNjE4NTI4NywiZXhwIjoxNjE2MTkyNDg3LCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImRlbGV0ZTptb3ZpZXMiLCJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyIsInBhdGNoOmFjdG9ycyIsInBhdGNoOm1vdmllcyIsInBvc3Q6YWN0b3JzIiwicG9zdDptb3ZpZXMiXX0.bgzQyPxj97RTH2vLPu4wIjU5SMd0kIy7dzgG8KbF2eBi5q1LRJwV6Jfv_B9Rpk8H3C0LfEES3RTcH76iE29X-wQnsIrFQsQ_YR5fkcOCJg4E0Yoc2p3TZbpgiPC-172YRO3sIUwWHwqlkYwpG0voLvqKA-FknyZr-0ayt06jhe6XhpM4oLOb8_56B7cZVZulw4OBKGRj_PB8mCIVo5OSFYrzK__HJQmf_Al7XAvN1iEXn_-yv2SOrBaCIhf5URQj8VZWf4MhUs53fF3wp5prIbY2lHzQzTASxydh21D5wgIiFbKKTP8KzbSCk7dKRpFOzO02kEECQ-D_H-27WUSgkw')

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
        self.casting_assistant_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ2MDhjMjkxYTQwMDZhNzMzZjdkIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxNjE4NTE2OSwiZXhwIjoxNjE2MTkyMzY5LCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiXX0.U9UupjXpv_XLvXrlaCCwzWJim9mW9ddvXxYEq22skwtff3b3H7Dz9RXrrpNXLYSB197geEITt4d-oiGsJ6D9zHxtt6QGowyf8QR3r12LCOdZJI82DvVWCfdEcp_vb11Jm2JoTrn1OWHdSLKxQyzsVmdTdXoSNiqRFg1WYyuel3JKaRd5V83BFJuOeDzefhjc-O1Jnny_rX5DSQMAuAIVy_DjW2QM67vE2eL_Ilrfrx0imIMjpS6IoQsuB6bqtSdhbPBohUEDBZrNKdFADOKuINDDzMt3BGQoudlcqg9tFxcJDLoXwp-XbhXVhkhLZwB60aFvh8vosXOOx5nzowZKsw')
        self.casting_director_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ3N2UyZGQ5NTgwMDY5ODk5MDBhIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxNjE4NTIzMCwiZXhwIjoxNjE2MTkyNDMwLCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIiwicGF0Y2g6YWN0b3JzIiwicGF0Y2g6bW92aWVzIiwicG9zdDphY3RvcnMiXX0.LWvnR_Z3zCAQ1Y24rMgY7uFzlsKIhnbEhYUydkhVL7OZlWX2MKYqQTSbGsSwr7NHqbft-EFfh36W0czKt0HZT2QOXbR_6ScSUpP6oRF0mi71csYwe7oxVLqG2hk4SK-FKg-9eS_wdNDiW8lZ19jdjwwyXn7m6iWNdGTd6HqregTsTkzv32n6z9hRpJZBQOy-QbkJceak0vCbc2x9PhHSJuWW86fV77vwgOu-oLphis93O3Q5rCpZK5qD_orMhVNpfrmDXbgwoC-Mb0ySLbfZK74bPUS_snZjdru-zfdGcDRA52rU8bK8mW55zuDFSCu4PdlMFEaKZz9RzW1FjgUXhA')
        self.executive_producer_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ3ZjU2MzUwNGMwMDcxZGU5OTVmIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxNjE4NTI4NywiZXhwIjoxNjE2MTkyNDg3LCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImRlbGV0ZTptb3ZpZXMiLCJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyIsInBhdGNoOmFjdG9ycyIsInBhdGNoOm1vdmllcyIsInBvc3Q6YWN0b3JzIiwicG9zdDptb3ZpZXMiXX0.bgzQyPxj97RTH2vLPu4wIjU5SMd0kIy7dzgG8KbF2eBi5q1LRJwV6Jfv_B9Rpk8H3C0LfEES3RTcH76iE29X-wQnsIrFQsQ_YR5fkcOCJg4E0Yoc2p3TZbpgiPC-172YRO3sIUwWHwqlkYwpG0voLvqKA-FknyZr-0ayt06jhe6XhpM4oLOb8_56B7cZVZulw4OBKGRj_PB8mCIVo5OSFYrzK__HJQmf_Al7XAvN1iEXn_-yv2SOrBaCIhf5URQj8VZWf4MhUs53fF3wp5prIbY2lHzQzTASxydh21D5wgIiFbKKTP8KzbSCk7dKRpFOzO02kEECQ-D_H-27WUSgkw')
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
        ###res = self.client().post('/actors', headers={'ROLE':'casting_assistant'})
        res = self.client().post('/actors', headers={'Authorization': "Bearer {}".format(self.casting_assistant_header)}, json={"name": "ME", "age": "44", "gender":"male"})
        #res = self.client().post('/actors', headers=self.casting_director_header, json={'age': 31})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)

    def test_post_movies_success(self):
        res = self.client().post('/movies', headers=self.executive_producer_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_post_movies_failure(self):
        res = self.client().post('/movies', headers={'ROLE':'casting_assistant'})
        #res = self.client().post('/movies', headers=self.executive_producer_header, json={'release_date': 8-10-2000})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
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
        ###res = self.client().post('/actors', headers={'Authorization': "Bearer {}".format(self.casting_assistant_header)}, json={"name": "ME", "age": "44", "gender":"male"})
        res = self.client().patch('/actors/1', headers=self.casting_assistant_header)
        data = json.loads(res.data)
        print(data)

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
