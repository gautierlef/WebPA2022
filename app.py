from flask import Flask, render_template, request, url_for, redirect, current_app, send_from_directory, Response
import mysql.connector
import boto3
import os
import requests
import os
import json
import pandas as pd
from pandas import json_normalize


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('viewHome.html')


@app.route('/viewTweets', methods=['GET'])
def viewTweets():
    tweets = []
    storage = Storage()
    data = storage.loadAllTweets()
    for row in data:
        tweets.append({'id': str(row[0]), 'authorId': str(row[1]), 'date': str(row[2]), 'lang': row[3], 'link': row[3], 'text': row[4]})
    return render_template('viewTweets.html', tweets=tweets)


@app.route('/inputComparisonTweet/<idTweet>', methods=['POST'])
def inputComparisonTweet(idTweet):
    articles = []
    storage = Storage()
    data = storage.loadAllArticles()
    for row in data:
        articles.append({'id': str(row[0]), 'Redactor': row[1], 'date': str(row[2]), 'lang': row[3], 'link': row[3], 'text': row[4]})
    return render_template('viewArticleSelection.html', articles=articles, idTweet=idTweet)


@app.route('/viewArticles', methods=['GET'])
def viewArticles():
    articles = []
    storage = Storage()
    data = storage.loadAllArticles()
    for row in data:
        articles.append({'id': str(row[0]), 'Redactor': row[1], 'date': str(row[2]), 'lang': row[3], 'link': row[3], 'text': row[4]})
    return render_template('viewArticles.html', articles=articles)


@app.route('/inputComparisonArticles/<idArticle>', methods=['POST'])
def inputComparisonArticles(idArticle):
    tweets = []
    storage = Storage()
    data = storage.loadAllTweets()
    for row in data:
        tweets.append({'id': str(row[0]), 'authorId': str(row[1]), 'date': str(row[2]), 'lang': row[3], 'link': row[3], 'text': row[4]})
    return render_template('viewTweetSelection.html', tweets=tweets, idArticle=idArticle)


@app.route('/comparisonById/<idTweet>/<idArticle>', methods=['POST'])
def comparisonById(idTweet, idArticle):
    storage = Storage()
    tweetData = storage.loadTweet(idTweet)
    articleData = storage.loadArticle(idArticle)
    tweet = {'id': str(articleData[0]), 'authorId': str(articleData[1]), 'date': str(articleData[2]), 'lang': articleData[3], 'link': articleData[3], 'text': articleData[4]}
    article = {'id': str(articleData[0]), 'Redactor': articleData[1], 'date': str(articleData[2]), 'lang': articleData[3], 'link': articleData[3], 'text': articleData[4]}
    return render_template('viewArticleSelection.html')


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


@app.route("/scrapTweets/<word>")
def scrapTweets(word):
    # To set your environment variables in your terminal run the following line:
    # export 'BEARER_TOKEN'='<your_bearer_token>'
    bearer_token = os.environ.get("AAAAAAAAAAAAAAAAAAAAAKjWbgEAAAAAd71Ej2t93WqhATnBrQcgYPsplS8%3DFoRfmQylzxgUS2mOUL6yt6HAsI1JsBmcxMocnVI1w3EBDn0koZ")
    # Code sale, token pas caché
    bearer_token = "AAAAAAAAAAAAAAAAAAAAAKjWbgEAAAAAd71Ej2t93WqhATnBrQcgYPsplS8%3DFoRfmQylzxgUS2mOUL6yt6HAsI1JsBmcxMocnVI1w3EBDn0koZ"
    search_url = "https://api.twitter.com/2/tweets/search/recent"

    def bearer_oauth(r):
        """
        Method required by bearer token authentication.
        """
        r.headers["Authorization"] = f"Bearer {bearer_token}"
        r.headers["User-Agent"] = "v2RecentSearchPython"
        return r

    def connect_to_endpoint(url, params):
        response = requests.get(url, auth=bearer_oauth, params=params)
        print(response.status_code)
        if response.status_code != 200:
            print(response.status_code)
            raise Exception(response.status_code, response.text)
        return response.json()

    df = pd.DataFrame()
    link = "https://www.businessinsider.com/elizabeth-holmes-pleads-with-judge-to-overturn-theranos-convictions-2022-5?r=US&IR=T"
    # Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
    # expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
    tweetfields = ['author_id,lang,created_at']
    query_params = {'query': word, 'tweet.fields': tweetfields, "max_results": 100}
    json_response = connect_to_endpoint(search_url, query_params)
    results = json.dumps(json_response, indent=4, sort_keys=True)
    results1 = json.loads(results)
    df1 = pd.DataFrame.from_dict(results1["data"])
    df1["link"] = link
    df1["keyword"] = word
    df = df.append(df1)
    df = df.reset_index(drop=True)
    df.to_excel("tweetbase.xlsx", index=False)
    return redirect('/')


@app.route("/readXlsx")
def readXlsx():
    df = pd.read_excel("tweetbase.xlsx")
    print(df)
    return redirect('/')


@app.route("/sendToS3")
def sendToS3():
    s3Client = boto3.client("s3")
    s3Client.upload_file(
        Filename="tweetbase.xlsx",
        Bucket="mainbucket",
        Key="tweetbase.xlsx",
    )
    # os.remove("matieres.csv")
    return redirect('/')


class Storage:
    def __init__(self):
        self.db = mysql.connector.connect(
            user='pagljm',
            passwd='20sur20fac1le!',
            db='maindatabase',
            host='maindatabase.cntkwisqa3zr.us-west-1.rds.amazonaws.com',
            port=3306
        )

    def loadAllTweets(self):
        cur = self.db.cursor()
        cur.execute(''' SELECT id, authorId, date, lang, link, text FROM Twitt ''')
        data = cur.fetchall()
        return data

    def loadAllArticles(self):
        cur = self.db.cursor()
        cur.execute(''' SELECT id, redactor, date, lang, link, text FROM Article ''')
        data = cur.fetchall()
        return data

    def loadTweet(self, idTweet):
        cur = self.db.cursor()
        cur.execute(''' SELECT id, authorId, date, lang, link, text FROM Twitt WHERE id = %s ''', (idTweet, ))
        tweet = cur.fetchall()
        return tweet

    def loadArticle(self, idArticle):
        cur = self.db.cursor()
        cur.execute(''' SELECT id, redactor, date, lang, link, text FROM Article WHERE id = %s ''', (idArticle, ))
        article = cur.fetchall()
        return article


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
