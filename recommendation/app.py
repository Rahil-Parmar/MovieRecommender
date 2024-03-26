from flask import Flask, render_template,request
import pandas as pd
import requests
import json
import datetime
import fickling

app = Flask(__name__)
app.config['TEMPLATES_FOLDER'] = 'templates'
movie_data = fickling.load(open('movie_dict.pkl','rb'))
movie_data = pd.DataFrame(movie_data)
movie_title = movie_data['Title'].apply(lambda x:x.lower())
similarity = fickling.load(open('similarity.pkl','rb'))
similarity = pd.DataFrame(similarity)
TMDB_API_URL = "https://api.themoviedb.org/3/"
TMDB_API_KEY = "87c9b727d697cfb29a87266e5098a948"
language_code ={
  "en": "English",
  "es": "Spanish",
  "fr": "French",
  "de": "German",
  "it": "Italian",
  "pt": "Portuguese",
  "ru": "Russian",
  "zh": "Chinese",
  "ja": "Japanese",
  "ko": "Korean"
}
#Default page
@app.route('/',methods=['GET','POST'])
def index():
    return render_template('index.html')

#Search for entered keywords
@app.route('/searchKeyword',methods=['GET','POST'])
def searchKeyWord():
    print('insearch')
    if request.method == 'POST':
        try:
            
            movie = request.form.get('query')
            res = '<ul class="list-unstyled">'
            data = [i for i in movie_title if movie.lower() in i]
            # data = movie_data[movie_data['Title'].str.contains(movie.lower())]['Title']
            # print(data)
            if len(data) > 0:
                # data = data[:10]
                for movie in data:
                    res += '<li>'+movie.title()+'</li>'
            else:
                res += '<li> No Data Found <li>'
            res += '</ul>'
            data = []
            # print(res)
            return res
        except Exception as e:
            print(e)
    return render_template('index.html')

#Get poster for the movie
def getPoster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=87c9b727d697cfb29a87266e5098a948&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

#get info of the movie
def getData(movie_id):
    movie_details_url = TMDB_API_URL + "movie/" + movie_id +"?api_key=" + TMDB_API_KEY
  # Make a request to the TMDB API endpoint.
    response = requests.get(movie_details_url)
    movie_det = {}
    # Check if the request was successful.
    if response.status_code == 200:
        response_json = json.loads(response.content)
        date = response_json["release_date"]
        date_object = datetime.datetime.strptime(date, "%Y-%m-%d")
# Format the month and year as a string.
        movie_det["release"] = date_object.strftime("%b %Y")
        movie_det['title'] = response_json["original_title"]
        movie_det["tagline"] = response_json["tagline"]
        movie_det["overciew"] = response_json["overview"]
        movie_det["language"] = language_code[response_json["original_language"]]
        movie_det["runtime"] = response_json["runtime"]
        movie_det["poster"] = "https://image.tmdb.org/t/p/w500/" + response_json["poster_path"]
        movie_det["genres"] = []
        for i in response_json["genres"]:
            movie_det["genres"].append(i["name"])
        return movie_det
    

    else:
        # The request was not successful.
        print("Error getting movie details:", response.status_code)
        


#Get the five movies based on similarity
def getRecommendation(movie):
    index = movie_data[movie_title == movie.lower()].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    
    mv = getData(str(movie_data[movie_title == movie.lower()].iloc[0].TMDb_Id))
    mv["cast"] = movie_data[movie_title == movie.lower()].iloc[0].cast
    mv["rec_title"] = []
    mv["rec_posters"] = []
    for i in distances[1:6]:
        # fetch the movie poster
        movie_id = movie_data.iloc[i[0]].TMDb_Id
        mv["rec_posters"].append(getPoster(movie_id))
        mv["rec_title"].append(movie_data.iloc[i[0]].Title)
    print(mv)
    return mv

#give recommendation
@app.route('/recommend',methods = ['GET','POST'])
def recommend():
    print('In recommend')
    if request.method == 'POST':
        movie = request.form.get('movie')
        movie_data = getRecommendation(movie)
        return render_template('search.html',data = movie_data)
    else:
        movie = request.args.get('movie')
        movie_data = getRecommendation(movie)
        return render_template('search.html',data = movie_data)
    return render_template('index.html')

if __name__ == '__main__':
   app.run(debug=True)
