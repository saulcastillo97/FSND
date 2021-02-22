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

casting_assistant_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ2MDhjMjkxYTQwMDZhNzMzZjdkIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxNDAyNTA5MSwiZXhwIjoxNjE0MDMyMjkxLCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiXX0.MDlJMT8pEepG8IVMcL6Y3EkOF7UN_6CxnfMQJdRm2MJtZDHfFsvheCPF7wz7ekj0UhQKyYs990CkKVRzaD2AYERTclUANHTNNtTLNQysYa-7eArWZh5ysIFq5ABtkMYZ5C3imoCx7C3vZBYZP9w5_XiOVr8BrrEo3mLiTa9Sn0aswUbriaOZdiwTih3EF2q8P5ZQkajUKS-nib46ZLD8oRIjFrttdWMTWqvftms6VkB6XW4hgye3jdKSQL6p8gKtUxqYvUOkFxWwkBfJeYs4NO9RMU62zN_NFSHAZkhK_8nxJ207F2nzC4UshKxax78C4j2bSveDljeeH1waKd2bww')
casting_director_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ3N2UyZGQ5NTgwMDY5ODk5MDBhIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxNDAyNTMwMywiZXhwIjoxNjE0MDMyNTAzLCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIiwicGF0Y2g6YWN0b3JzIiwicGF0Y2g6bW92aWVzIiwicG9zdDphY3RvcnMiXX0.Z69cyJ6QuZDI_f33CBhqnWtvq3XpnIBT4odoRCLpJh-luUUZ0nThfmrzvW1_1DmXh5CPg08V0u_E1qG1IxqxaXVe5I7o0uSR_sqKCSAKC9fr5nXaEgk__wMQACIQQXzmqr7mgzvkRg0x8DtyBAlmPfKdt-pQjz52ik02DtbKGyQP8h4kVinQjpYNb-qfRum5XfExz2JbAMipbxV-ExZd7p1Hv51VzY67P0q4qSMJQex_CGOl9udiQAV3B2h3e__2Vf3AoG8vgpzaf3rbyImX80MYIXddUhPGTW8g1y_nI-AzAiQN2eJmqO8xU1hahlKSRs5vfz0GCVLNUZUowv-kuQ')
executive_producer_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ3ZjU2MzUwNGMwMDcxZGU5OTVmIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxNDAyNTIzMSwiZXhwIjoxNjE0MDMyNDMxLCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImRlbGV0ZTptb3ZpZXMiLCJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyIsInBhdGNoOmFjdG9ycyIsInBhdGNoOm1vdmllcyIsInBvc3Q6YWN0b3JzIiwicG9zdDptb3ZpZXMiXX0.Tkkeh0rmXrSx08oAOAX57JSLuwoqG6hGy7WpycLXBSW8FOiTZuQfNjuqtNbDhAPG0h2EAQJ-2tuTgzIK3CjDTrXlr5TIVemFjbwk66-81BFRSZYtYCYGfuejLUdtAA4NAvY7AWU1YM7rVI3PP9wvPwnd0rsJwFBQ1a6sFefXrBCw8D2UK99mybxSw-0uQmrJyOs6IQF1fyovp6zJAxrHWTWzp0CP-hMyPyOJFXRuti2NiIneJ_aKFpF1Yhb5RNUEUN7eGNw-owNlr-ompx5ZV4Q5MLOmTyCBjisR4RGQfygi1kOzxeCZWGh8EwceZ3U9V-TKAGEjR0YQWu9Yu7LM8w')


class CapstoneTestCase(unittest.TestCase):
    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = 'capstonedb'
        self.database_path = 'postgres://{}/{}'.format('localhost:5432', self.database_name)
        self.casting_assistant_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ2MDhjMjkxYTQwMDZhNzMzZjdkIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxNDAyNTA5MSwiZXhwIjoxNjE0MDMyMjkxLCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiXX0.MDlJMT8pEepG8IVMcL6Y3EkOF7UN_6CxnfMQJdRm2MJtZDHfFsvheCPF7wz7ekj0UhQKyYs990CkKVRzaD2AYERTclUANHTNNtTLNQysYa-7eArWZh5ysIFq5ABtkMYZ5C3imoCx7C3vZBYZP9w5_XiOVr8BrrEo3mLiTa9Sn0aswUbriaOZdiwTih3EF2q8P5ZQkajUKS-nib46ZLD8oRIjFrttdWMTWqvftms6VkB6XW4hgye3jdKSQL6p8gKtUxqYvUOkFxWwkBfJeYs4NO9RMU62zN_NFSHAZkhK_8nxJ207F2nzC4UshKxax78C4j2bSveDljeeH1waKd2bww')
        self.casting_director_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ3N2UyZGQ5NTgwMDY5ODk5MDBhIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxNDAyNTMwMywiZXhwIjoxNjE0MDMyNTAzLCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIiwicGF0Y2g6YWN0b3JzIiwicGF0Y2g6bW92aWVzIiwicG9zdDphY3RvcnMiXX0.Z69cyJ6QuZDI_f33CBhqnWtvq3XpnIBT4odoRCLpJh-luUUZ0nThfmrzvW1_1DmXh5CPg08V0u_E1qG1IxqxaXVe5I7o0uSR_sqKCSAKC9fr5nXaEgk__wMQACIQQXzmqr7mgzvkRg0x8DtyBAlmPfKdt-pQjz52ik02DtbKGyQP8h4kVinQjpYNb-qfRum5XfExz2JbAMipbxV-ExZd7p1Hv51VzY67P0q4qSMJQex_CGOl9udiQAV3B2h3e__2Vf3AoG8vgpzaf3rbyImX80MYIXddUhPGTW8g1y_nI-AzAiQN2eJmqO8xU1hahlKSRs5vfz0GCVLNUZUowv-kuQ')
        self.executive_producer_token = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9YcDlybEhPTlhJUDJkeXV6VWRaZCJ9.eyJpc3MiOiJodHRwczovL3NjZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAyNWQ3ZjU2MzUwNGMwMDcxZGU5OTVmIiwiYXVkIjoiY2FzdGluZyIsImlhdCI6MTYxNDAyNTIzMSwiZXhwIjoxNjE0MDMyNDMxLCJhenAiOiJzU2tOQnB4RHZwWElrOEs5SDgzSXlZMzdCcXpHOGJ5ZSIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImRlbGV0ZTptb3ZpZXMiLCJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyIsInBhdGNoOmFjdG9ycyIsInBhdGNoOm1vdmllcyIsInBvc3Q6YWN0b3JzIiwicG9zdDptb3ZpZXMiXX0.Tkkeh0rmXrSx08oAOAX57JSLuwoqG6hGy7WpycLXBSW8FOiTZuQfNjuqtNbDhAPG0h2EAQJ-2tuTgzIK3CjDTrXlr5TIVemFjbwk66-81BFRSZYtYCYGfuejLUdtAA4NAvY7AWU1YM7rVI3PP9wvPwnd0rsJwFBQ1a6sFefXrBCw8D2UK99mybxSw-0uQmrJyOs6IQF1fyovp6zJAxrHWTWzp0CP-hMyPyOJFXRuti2NiIneJ_aKFpF1Yhb5RNUEUN7eGNw-owNlr-ompx5ZV4Q5MLOmTyCBjisR4RGQfygi1kOzxeCZWGh8EwceZ3U9V-TKAGEjR0YQWu9Yu7LM8w')
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

    def test_get_movies_success(self):
        res = self.client().get('/movies', headers=self.casting_assistant_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

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
