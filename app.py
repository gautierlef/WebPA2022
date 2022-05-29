from flask import Flask, render_template, request, url_for, redirect, current_app, send_from_directory, Response
import mysql.connector
import boto3
import os


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('viewHome.html')


@app.route('/viewTwitts', methods=['GET'])
def viewTwitts():
    twitts = []
    storage = Storage()
    data = storage.loadAll()
    for row in data:
        twitts.append({'id': str(row[0]), 'nom': row[1], 'description': row[2], 'heures': str(row[3])})
    return render_template('viewTwitts.html', twitts=twitts)


@app.route('/viewArticles', methods=['GET'])
def viewArticles():
    articles = []
    storage = Storage()
    data = storage.loadAll()
    for row in data:
        articles.append({'id': str(row[0]), 'nom': row[1], 'description': row[2], 'heures': str(row[3])})
    return render_template('viewArticles.html', articles=articles)


@app.route('/inputComparison', methods=['GET'])
def inputComparison():
    return render_template('viewInputComparison.html')


@app.route('/comparison', methods=['POST'])
def comparison():
    keyWord = request.form['keyWord']
    return render_template('viewComparison.html', keyWord=keyWord)


@app.route("/downloadCSV")
def downloadCSV():
    s3client = boto3.client("s3")
    s3 = boto3.resource(
        service_name="s3",
        region_name="us-east-1",
        aws_access_key_id="AKIAZMSAVZUGSJ7DUL5J",
        aws_secret_access_key="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"
    )
    mainbucket = s3.Bucket('mainbucket')
    for obj in mainbucket.objects.all():
        path, filename = os.path.split(obj.key)
        mainbucket.download_file(obj.key, filename)
    with open("matieres.csv") as f:
        csv = f.read()
    f.close()
    os.remove("matieres.csv")
    return Response(csv, mimetype="text/csv", headers={"Content-disposition": "attachment; filename=matieres.csv"})


class Storage:
    def __init__(self):
        self.db = mysql.connector.connect(
            user='pagljm',
            passwd='20sur20fac1le!',
            db='maindatabase',
            host='maindatabase.cntkwisqa3zr.us-west-1.rds.amazonaws.com',
            port=3306
        )

    def loadAll(self):
        cur = self.db.cursor()
        cur.execute(''' SELECT id, nom, description, heures FROM Matieres ''')
        data = cur.fetchall()
        return data

    def loadMatiere(self, idMatiere):
        cur = self.db.cursor()
        cur.execute(''' SELECT id, nom, description, heures FROM Matieres WHERE id = %s ''', (idMatiere, ))
        matiere = cur.fetchall()
        return matiere


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
