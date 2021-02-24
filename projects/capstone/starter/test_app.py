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

casting_assistant_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ2MDhjMjkxYTQwMDZhNzMzZjdkIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxNDE5OTU5OCwiZXhwIjoxNjE0MjA2Nzk4LCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiXX0.eNvJ9w0VLiPyOEfdrdUpOdHwMhDdM0DEgAiwevZ34r_g6yVSwt4gcdkh67LYHzitALNFvzZmHejl_dMr8wsOVSTgbxxa84TugnvQ7kZkARkxI3U_Y9AzmNjy_xowpXZ5lQ9K2EA9NkIpxvPS_p16zsXdcbx-JNgavAchQYRtb09GVJRC7XzcH9_Qu07oMlAb2Px0jeNXTAb1y3piSQ3Epz275q3obhTLLTOHObWWSthw5-hjkCX5cWJfYLd41R4t8GLRoLk_mP0hdknvmIVSpiAjPriCFwtei3p_hsK4EAi6KyFak4oVXTTS1CEed8RfX71s0ITimxS1tXAY9RFdtg')
casting_director_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ3N2UyZGQ5NTgwMDY5ODk5MDBhIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxNDE5OTY2OCwiZXhwIjoxNjE0MjA2ODY4LCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIiwicGF0Y2g6YWN0b3JzIiwicGF0Y2g6bW92aWVzIiwicG9zdDphY3RvcnMiXX0.N1c8QNk9c_W2MeeW_kt3EQM7_Nh-l-I5-rPu-iJcR8URPPF7qplBUYqRlaPxkN7EdEc40J8NOa9JfvOGTzo-Eig65MgdA1AfeVmq4wSVJUTGGwAtII2rS_NHFgHvMHCtVn5lvaHdIH8bvtdDCHM5rzuPfpU5rWs9GOD1QQXMy0xiiQRsf3zzC-hVxlfsa2U--jsp9YyI_e98YYgXJCpdLwk9oxLBKFRq7xcGssBK_82apwW7jH6brInx36QQeJ-wl1UTnrzhaA_wrhSlHKflc7eD7fqb-5Jsdz3fVpXedA6gRcQtaOS90PqJrYgBBwRFc8j8OZreszBSzoSJKgRQAA')
executive_producer_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ3ZjU2MzUwNGMwMDcxZGU5OTVmIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxNDE5OTc0MSwiZXhwIjoxNjE0MjA2OTQxLCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImRlbGV0ZTptb3ZpZXMiLCJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyIsInBhdGNoOmFjdG9ycyIsInBhdGNoOm1vdmllcyIsInBvc3Q6YWN0b3JzIiwicG9zdDptb3ZpZXMiXX0.LmGaI7sCRUdxyB8e8_V1cRL9Fs5Xjz74yK6ORVMW65TJ5m2DfaEAf-LDdtmdtjgZezT-nLDVtWe8heZi7Ztg4tgc25LRdJM3byeGVHtDfl9iodSJRYnbPF7CWAwO8nGpOfyuHh14ex52Pn9OjkObIXlGpccqAQRIe3_rZTCAs-wqP22scLomcESS4y5evJiXMdyU8P6biXY65CAMH04LWJKyQQxAYjBqlBjdc_P74C3y6j_qL7yees6iwgHy94AJrKKwzGrU7s7iegu3X4FHQg7mOFZtj9SQ7iDhPuLMOpKftbLip2svN31hIK8kCY9744XnGxbBxbB8K0-YSdQj8w')

ROLES = {
    "CASTING_ASSISTANT": {
        "permissions": [
            "get:movies",
            "get:actors"
        ]
    },
    "CASTING_DIRECTOR": {
        "permissions": [
            "get:movies",
            "get:actors",
            "post:actors",
            "delete:actors",
            "patch:movies",
            "patch:actors"
        ]
    },
    "EXECUTIVE_PRODUCER": {
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
        self.casting_assistant_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ2MDhjMjkxYTQwMDZhNzMzZjdkIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxNDE5OTU5OCwiZXhwIjoxNjE0MjA2Nzk4LCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiXX0.eNvJ9w0VLiPyOEfdrdUpOdHwMhDdM0DEgAiwevZ34r_g6yVSwt4gcdkh67LYHzitALNFvzZmHejl_dMr8wsOVSTgbxxa84TugnvQ7kZkARkxI3U_Y9AzmNjy_xowpXZ5lQ9K2EA9NkIpxvPS_p16zsXdcbx-JNgavAchQYRtb09GVJRC7XzcH9_Qu07oMlAb2Px0jeNXTAb1y3piSQ3Epz275q3obhTLLTOHObWWSthw5-hjkCX5cWJfYLd41R4t8GLRoLk_mP0hdknvmIVSpiAjPriCFwtei3p_hsK4EAi6KyFak4oVXTTS1CEed8RfX71s0ITimxS1tXAY9RFdtg')
        self.casting_director_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ3N2UyZGQ5NTgwMDY5ODk5MDBhIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxNDE5OTY2OCwiZXhwIjoxNjE0MjA2ODY4LCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIiwicGF0Y2g6YWN0b3JzIiwicGF0Y2g6bW92aWVzIiwicG9zdDphY3RvcnMiXX0.N1c8QNk9c_W2MeeW_kt3EQM7_Nh-l-I5-rPu-iJcR8URPPF7qplBUYqRlaPxkN7EdEc40J8NOa9JfvOGTzo-Eig65MgdA1AfeVmq4wSVJUTGGwAtII2rS_NHFgHvMHCtVn5lvaHdIH8bvtdDCHM5rzuPfpU5rWs9GOD1QQXMy0xiiQRsf3zzC-hVxlfsa2U--jsp9YyI_e98YYgXJCpdLwk9oxLBKFRq7xcGssBK_82apwW7jH6brInx36QQeJ-wl1UTnrzhaA_wrhSlHKflc7eD7fqb-5Jsdz3fVpXedA6gRcQtaOS90PqJrYgBBwRFc8j8OZreszBSzoSJKgRQAA')
        self.executive_producer_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ3ZjU2MzUwNGMwMDcxZGU5OTVmIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxNDE5OTc0MSwiZXhwIjoxNjE0MjA2OTQxLCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImRlbGV0ZTptb3ZpZXMiLCJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyIsInBhdGNoOmFjdG9ycyIsInBhdGNoOm1vdmllcyIsInBvc3Q6YWN0b3JzIiwicG9zdDptb3ZpZXMiXX0.LmGaI7sCRUdxyB8e8_V1cRL9Fs5Xjz74yK6ORVMW65TJ5m2DfaEAf-LDdtmdtjgZezT-nLDVtWe8heZi7Ztg4tgc25LRdJM3byeGVHtDfl9iodSJRYnbPF7CWAwO8nGpOfyuHh14ex52Pn9OjkObIXlGpccqAQRIe3_rZTCAs-wqP22scLomcESS4y5evJiXMdyU8P6biXY65CAMH04LWJKyQQxAYjBqlBjdc_P74C3y6j_qL7yees6iwgHy94AJrKKwzGrU7s7iegu3X4FHQg7mOFZtj9SQ7iDhPuLMOpKftbLip2svN31hIK8kCY9744XnGxbBxbB8K0-YSdQj8w')
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
        res = self.client().get('/movies', headers={"ROLE": "CASTING_ASSISTANT"})
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
        res = self.client().post('/actors', headers=self.casting_director_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_post_actors_failure(self):
        res = self.client().delete('/actors', headers=self.casting_director_header, json={'release_date': 8-10-2000})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

    def test_post_movies_success(self):
        res = self.client().post('/movies', headers=self.executive_producer_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_post_movies_failure(self):
        res = self.client().delete('/movies', headers=self.executive_producer_header, json={'age': 31})

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
        res = self.client().patch('/movies/1', headers=self.casting_assistant_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)

if __name__ == '__main__':
    unittest.main()
