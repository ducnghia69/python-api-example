from flask import Flask, jsonify, request, send_from_directory, redirect, render_template
from flask_restful import Api, Resource
from flasgger import Swagger
import urllib

from app_redirect import AppRedirect
import book_review
import os

app = Flask(__name__)
api = Api(app)
swagger = Swagger(app)

class UppercaseText(Resource):
    def get(self):
        """
        This method responds to the GET request for this endpoint and returns the data in uppercase.
        ---
        tags:
        - Text Processing
        parameters:
            - name: text
              in: query
              type: string
              required: true
              description: The text to be converted to uppercase
        responses:
            200:
                description: A successful GET request
                content:
                    application/json:
                      schema:
                        type: object
                        properties:
                            text:
                                type: string
                                description: The text in uppercase
        """
        text = request.args.get('text')

        return jsonify({"text": text.upper()})
    
class Records(Resource):
    def get(self):
        """
        This method responds to the GET request for returning a number of books.
        ---
        tags:
        - Records
        parameters:
            - name: count
              in: query
              type: integer
              required: false
              description: The number of books to return
            - name: sort
              in: query
              type: string
              enum: ['ASC', 'DESC']
              required: false
              description: Sort order for the books
        responses:
            200:
                description: A successful GET request
                schema:
                    type: object
                    properties:
                        books:
                            type: array
                            items:
                                type: object
                                properties:
                                    title:
                                        type: string
                                        description: The title of the book
                                    author:
                                        type: string
                                        description: The author of the book
        """

        count = request.args.get('count')  # Default to returning 10 books if count is not provided
        sort = request.args.get('sort')

        # Get all the books
        books = book_review.get_all_records(count=count, sort=sort)

        return {"books": books}, 200
    
class AddRecord(Resource):
    def post(self):
        """
        This method responds to the POST request for adding a new record to the DB table.
        ---
        tags:
        - Records
        parameters:
            - in: body
              name: body
              required: true
              schema:
                id: BookReview
                required:
                  - Book
                  - Rating
                properties:
                  Book:
                    type: string
                    description: the name of the book
                  Rating:
                    type: integer
                    description: the rating of the book (1-10)
        responses:
            200:
                description: A successful POST request
            400: 
                description: Bad request, missing 'Book' or 'Rating' in the request body
        """

        data = request.json
        print(data)

        # Check if 'Book' and 'Rating' are present in the request body
        if 'Book' not in data or 'Rating' not in data:
            return {"message": "Bad request, missing 'Book' or 'Rating' in the request body"}, 400
        # Call the add_record function to add the record to the DB table
        success = book_review.add_record(data)

        if success:
            return {"message": "Record added successfully"}, 200
        else:
            return {"message": "Failed to add record"}, 500
        
# Định nghĩa thư mục chứa các tệp JSON
static_dir = os.path.join(app.root_path, 'static')

# Cấu hình route phục vụ tệp assetlinks.json (Android App Links)
@app.route('/.well-known/assetlinks.json')
def serve_assetlinks():
    return send_from_directory(static_dir, 'assetlinks.json', mimetype='application/json')

# Cấu hình route phục vụ tệp apple-app-site-association (iOS Universal Links)
@app.route('/.well-known/apple-app-site-association')
def serve_aasa():
    return send_from_directory(static_dir, 'apple-app-site-association', mimetype='application/json')


@app.route('/abc')
def redirectIOSApp():
    qs = request.args.to_dict()
    message = 'nghia dep zai?'

    options = {
        "iosApp": f'applinks:python-api-example-kl64.onrender.com',
        "iosAppStore": f'https://itunes.apple.com/il/app/twitter/id333903271?mt=8&message={message}',
        "android": {
            "host": f'python-api-example-kl64.onrender.com',
            "scheme": 'https',
            "package": 'com.example.deeplink_cookbook',
            "fallback": f'https://play.google.com/store/apps/details?id=com.twitter.android&hl=en&message={urllib.parse.quote(message)}'
        }
    }

    return AppRedirect.redirect(options)

@app.route('/abc1')
def redirectIOSAppStore():
    qs = request.args.to_dict()
    message = qs.get('nghia dep zai so 1?', '')

    options = {
        "iosApp": f'twitter://post?message=' + message,
        "iosAppStore": f'https://itunes.apple.com/il/app/twitter/id333903271?mt=8&message={message}',
        "android": {
            "host": f'python-api-example-kl64.onrender.com',
            "scheme": 'https',
            "package": 'com.example.deeplink_cookbook',
            "fallback": f'https://play.google.com/store/apps/details?id=com.twitter.android&hl=en&message={urllib.parse.quote(message)}'
        }
    }

    return render_template('redirect.html', options=options)



api.add_resource(AddRecord, "/add-record")
api.add_resource(Records, "/records")
api.add_resource(UppercaseText, "/uppercase")

if __name__ == "__main__":
    app.run(debug=True)