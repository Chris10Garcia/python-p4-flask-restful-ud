#!/usr/bin/env python3
import functools
from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from werkzeug.exceptions import NotFound
from models import db, Newsletter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newsletters.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class Home(Resource):
    def get(self):
        response_body = {
            "message" : "Welcome to the Newsletter RESTful API",
        }
        response = make_response(
            response_body,
            200
        )
        return response
    
api.add_resource(Home, "/")

class Newsletters(Resource):
    def response_func(self, responsebody, code):
        resposne = make_response(
            responsebody,
            code
        )
        return resposne

    def get(self):
        news_dict = [news.to_dict() for news in Newsletter.query.all()]

        return self.response_func(news_dict, 200)

    def post(self):           
        # figured out how to deal if data came in as raw json or if it was form data         
        try:
            request.get_json()
            form_data = {attr : request.json.get(attr) for attr in request.json if hasattr(Newsletter, attr)}
        except:
            request.get_data()
            form_data = {attr : request.form.get(attr) for attr in request.form if hasattr(Newsletter, attr)}

        new_record = Newsletter(**form_data)

        db.session.add(new_record)
        db.session.commit()

        news_dict = new_record.to_dict()

        return self.response_func(news_dict, 200)

api.add_resource(Newsletters, "/newsletters")


class NewsLettersByID(Resource):

    # def get(self, id):
    #     news = Newsletter.query.filter(Newsletter.id == id).first()
    #     if news == None:
    #         response_body = "<h1>404, record not found</h1>"
    #         response = make_response(
    #             response_body, 
    #             404
    #         )
    #         return response        

    #     news_dict = news.to_dict()

    #     response = make_response(
    #         news_dict,
    #         200
    #     )
    #     return response        


    #this should be a decorator
    def record_exits(func):
        @functools.wraps(func)  
        def wrapper(self, *arg, id):
            news = Newsletter.query.filter(Newsletter.id == id).first()
            if news == None:
                response_body = "<h1>404, record not found</h1>"
                response = make_response(
                    response_body, 
                    404
                )
                return response
            return func(self, news)
        return wrapper

    def response_func(self, responsebody, code):
        response = make_response(
            jsonify(responsebody),
            code
        )
        return response

    @record_exits
    def get(self, news):
        news_dict = news.to_dict()

        return self.response_func(news_dict, 200)

    # def get(self, id):
    #     news = Newsletter.query.filter(Newsletter.id == id).first()
    #     news_dict = news.to_dict()
    #     return self.response_func(news_dict, 200)

    @record_exits
    def patch(self, news):
        
        try:
            request.get_json()
            [setattr(news, attr, request.json.get(attr))for attr in request.json if hasattr(Newsletter, attr)]
        except:
            request.get_data()
            [setattr(news, attr, request.form.get(attr))for attr in request.form if hasattr(Newsletter, attr)]            
    
        db.session.add(news)
        db.session.commit()

        news_dict = news.to_dict()

        return self.response_func(news_dict, 200)   

    @record_exits
    def delete(self, news):
        db.session.delete(news)
        db.session.commit()

        response_body = {
            "message" : "Record successfully deleted"
        }

        self.response_func(response_body, 200)


api.add_resource(NewsLettersByID, "/newsletters/<int:id>")

@app.errorhandler(NotFound)
def handle_not_found(e):
    response = make_response(
        f"<h1>{e}</h1>",
        404
    )
    return response

app.register_error_handler(404, handle_not_found)

if __name__ == '__main__':
    app.run(port=5555, debug=True)

