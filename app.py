from cleansing import textCleansing
from flasgger import swag_from
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flask import request, g
import sqlite3
import pandas as pd

from flask import Flask, jsonify

app = Flask(__name__)

DATABASE = 'database.db'


def create_db():
    conn = sqlite3.connect('database.db')

    conn.execute('''
    drop table answer;
    ''')
    conn.commit()

    conn.execute(
        '''CREATE TABLE answer (id INTEGER PRIMARY KEY AUTOINCREMENT, answer varchar(255) not null);''')
    conn.commit()


create_db()


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


app.json_encoder = LazyJSONEncoder
swagger_template = dict(
    info={
        'title': LazyString(lambda: 'API Documentation for Challange Binar'),
        'version': LazyString(lambda: '1.0.0'),
    },
    host=LazyString(lambda: request.host)
)
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}
swagger = Swagger(app, template=swagger_template,
                  config=swagger_config)

abusive = pd.read_csv('dataset/abusive.csv', encoding='ISO-8859-1')
filterAbusive = abusive["ABUSIVE"].tolist()

alay = pd.read_csv('dataset/new_kamusalay.csv',
                   encoding='ISO-8859-1', header=None)
header = ['alay_word', 'replacement_word']
alay.columns = header
alay = alay


@swag_from("docs/hello_world.yml", methods=['GET'])
@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM answer')
    data = cursor.fetchall()
    response = {
        'status_code': 200,
        'description': "Semua data dari tabel answer",
        'data': data,
    }
    return jsonify(response)


@swag_from("docs/text_processing.yml", methods=['POST'])
@app.route('/text-processing', methods=['POST'])
def text_processing():
    data = request.form.get('text')

    clean = textCleansing(filterAbusive, alay)
    data = clean.cleaning(data)
    data = clean.cleansingAbusive(data)
    data = clean.replace_words(data)

    json_response = {
        'status_code': 200,
        'description': "Teks yang sudah diproses",
        'data': data,
    }

    conn = sqlite3.connect('database.db')
    sql_string = f"""
        INSERT INTO answer 
        (answer) 
        VALUES 
        ('{data}');
    """
    conn.execute(sql_string)
    conn.commit()

    response_data = jsonify(json_response)
    return response_data


@swag_from("docs/text_processing_file.yml", methods=['POST'])
@app.route('/text-processing-file', methods=['POST'])
def text_processing_file():

    # Upladed file
    file = request.files.getlist('file')[0]

    # Import file csv ke Pandas
    df = pd.read_csv(file, encoding='ISO-8859-1')

    # Ambil teks yang akan diproses dalam format list
    df = df.iloc[:, 0]

    # Lakukan cleansing pada teks
    clean = textCleansing(filterAbusive, alay)
    df = df.apply(lambda x: clean.cleaning(x))
    df = df.apply(lambda x: clean.cleansingAbusive(x))
    df = df.apply(lambda x: clean.replace_words(x))

    df = df.to_list()
    json_response = {
        'status_code': 200,
        'description': "Teks yang sudah diproses",
        'data': df,
    }

    conn = sqlite3.connect('database.db')
    sql_string = f"""
        INSERT INTO answer 
        (answer) 
        VALUES 
        ('{df}');
    """
    conn.execute(sql_string)
    conn.commit()

    response_data = jsonify(json_response)
    return response_data


if __name__ == '__main__':
    app.run()
