from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask_jsonpify import jsonify

db_connect = create_engine('sqlite:///SAT_NewYork_DB.db')
app = Flask(__name__)
api = Api(app)

class DBN(Resource):
    def get(self):
        conn = db_connect.connect() # connect to database
        query = conn.execute("select * from AllData") # This line performs query and returns json result
        return {'DBN': [i[0] for i in query.cursor.fetchall()]} # Fetches first column that is DBN

class AllCorrelation(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute("select * from SAT_Correlation")
        result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
        return jsonify(result)

class Correlation(Resource):
    def get(self):
        conn = db_connect.connect()
        query = conn.execute("select name, SAT_score from SAT_Correlation")
        result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
        return jsonify(result)

api.add_resource(DBN, '/DBN') # Route_1
api.add_resource(AllCorrelation, '/Correlation') # Route_2
api.add_resource(Correlation, '/SATCorrelation') # Route_2

if __name__ == '__main__':
     app.run(port='5002')