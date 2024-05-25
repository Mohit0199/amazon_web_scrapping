from flask import Flask, render_template, request,jsonify
from bs4 import BeautifulSoup as bs
import urllib
import pymongo

app = Flask(__name__) # initializing a flask app

@app.route('/',methods=['GET'])  # route to display the home page
def homePage():
    return render_template("index.html")


@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")

            amazon_url = "https://www.amazon.in/s?k=" + searchString

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            req = urllib.request.Request(amazon_url, headers=headers)
            urlclient = urllib.request.urlopen(req)
            amazon_page = urlclient.read()
            amazon_html = bs(amazon_page, "html.parser")

            bigboxes = amazon_html.find_all(class_="sg-col-20-of-24 s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16")

            product_link = "https://www.amazon.in/"+bigboxes[0].find("a")["href"]
   
            prodReq = urllib.request.Request(product_link, headers=headers)
            prodRes = urllib.request.urlopen(prodReq)
            prod_page = prodRes.read()
            prod_html = bs(prod_page, "html.parser")

            commentboxes = prod_html.find_all(class_="a-section review aok-relative")
         
            reviews = []
            for commentbox in commentboxes:
                try:
                    name = commentbox.find(class_="a-profile-content").text
                except:
                    name = 'No Name'

                try:
                    rating = commentbox.find(class_="a-icon-alt").text
                except:
                    rating = 'No Rating'

                try:
                    commentHead = commentbox.find(class_="a-size-base a-link-normal review-title a-color-base review-title-content a-text-bold").find_all('span')[2].text
                except:
                    commentHead = 'No Comment Heading'
                    
                try:
                    custComment = commentbox.find(class_="a-row a-spacing-small review-data").text.strip()[:-10]
                except Exception as e:
                    print("Exception while creating dictionary: ",e)

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)

            client = pymongo.MongoClient("mongodb+srv://mohitrathod723:mohit99@cluster0.9xj2jcf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
            db = client['review_scrap']
            review_col = db['review_scrap_data']
            review_col.insert_many(reviews)

            return render_template('results.html', reviews=reviews)
        
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
        
    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(host='127.0.0.1', debug=True)
