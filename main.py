from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker

from flask import session as login_session
import random
import string
import sqlite3
# IMPORTS FOR THIS STEP
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
APPLICATION_NAME = "Restaurant Menu Application"



# Create anti-forgery state token
@app.route('/login')
def showLogin():
    global state
    login_session['state']=state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    print("in gconnect")
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
        print("obtaining credentials")
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()


    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    conn = sqlite3.connect('catalog')
    c = conn.cursor()
    c.execute("SELECT  * FROM users WHERE email=?", (login_session['email'],))
    res=c.fetchall()
    if len(res)==0:
        c.execute("INSERT INTO users VALUES(?,?);", (login_session['username'], login_session['email'],))
        conn.commit()

    flash("you are now logged in as %s" % login_session['username'])

    return "done bro"

@app.route('/catalog/<category>/items')
def catalog(category):
    if 'username' in login_session:
        user = login_session['email']
    else:
        user = "NON"
    conn = sqlite3.connect('catalog')
    c = conn.cursor()
    c.execute("SELECT * FROM categories")
    sqlresults = c.fetchall()
    c.execute("SELECT * FROM item WHERE category=?;", (category,))
    items=c.fetchall()
    global state
    login_session['state'] = state
    return render_template('index.html', results=sqlresults, items=items, user=user,category=category, STATE=state)

@app.route('/catalog/<category>/<item>')
def description(category,item):

    if 'username' in login_session:
        user = login_session['email']
    else:
        user = "NON"
    print(user)
    conn = sqlite3.connect('catalog')
    c = conn.cursor()
    c.execute("SELECT * FROM item where name=? and category=?;", (item, category,))
    sqlresults = c.fetchall()
    global state
    login_session['state'] = state
    return render_template('description.html' ,results=sqlresults,user=user ,STATE=state)


@app.route("/catalog/<item>/edit")
def edit(item):
    if 'username' not in login_session:
        return redirect('/')
    conn = sqlite3.connect('catalog')
    c = conn.cursor()
    user = login_session['email']
    c.execute("SELECT * FROM item where name=? and user=?;", (item, user,))
    sqlresults = c.fetchall()
    if len(sqlresults) == 0:
        return redirect('/')
    c.execute("SELECT * from categories")
    category=c.fetchall()
    global state
    login_session['state'] = state
    return render_template("edit.html",results=sqlresults,user=user,categories=category,STATE=state)


@app.route('/editform',methods=['POST'])
def editform():
    if 'username' not in login_session:
        return redirect('/')
    name=request.form['item_name']
    description=request.form['description']
    category=request.form['category']
    user=request.form['user']
    id=request.form['id']
    if login_session['email'] != user:
        return redirect('/')
    conn = sqlite3.connect('catalog')
    c = conn.cursor()
    c.execute("UPDATE item SET name=?,description=?,category=? where id=? and user=?;",(name,description,category,id,user,))
    conn.commit()
    return redirect('/')

@app.route('/catalog/<item>/delete')
def delete(item):
    if 'username' not in login_session:
        return redirect('/')

    conn = sqlite3.connect('catalog')
    c = conn.cursor()
    user=login_session['email']
    c.execute("SELECT * FROM item where name=? and user=?;", (item,user,))
    sqlresults=c.fetchall()
    if len(sqlresults)==0:
        return redirect('/')
    c.execute("DELETE FROM item where name=?;", (item,))
    conn.commit()
    return redirect('/')
@app.route('/')
def index():
    if 'username' in login_session:
        user = login_session['email']
    else:
        user = "NON"
    conn = sqlite3.connect('catalog')
    c = conn.cursor()
    global state
    login_session['state']=state
    c.execute("SELECT * FROM categories")
    sqlresults = c.fetchall()
    c.execute("SELECT * FROM item")
    items = c.fetchall()
    return render_template('index.html', results=sqlresults, user=user, STATE=state, items=items, category="Latest ")

# Show all restaurants
#@app.route('/')
#@app.route('/restaurant/')
#def showRestaurants():
#    restaurants = session.query(Restaurant).order_by(asc(Restaurant.name))
#    return render_template('restaurants.html', restaurants=restaurants)
@app.route('/gdisconnect')
def gdisconnect():
    credentials=login_session.get('credentials')
    if credentials is None:
        print 'Access Token is None'
        return redirect('/')
        #return response
    access_token = credentials.access_token
   # print 'In gdisconnect access token is %s', access_token
    #print("User name is")
    #print(login_session['username'])
    #if access_token is None:
    access_token=str(access_token)
    url = 'https://accounts.google.com/o/oauth2/revoke?token='+access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    #print 'result is '
    #print result
    print(access_token)

    if login_session['credentials'] is not None or login_session['email'] is not None:
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        print("all data deleted")
    print(result['status'])
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        print("Successfully disconnected.")

    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        print("Failed to revoke token for given user.")

    return redirect('/')


@app.route('/additem')
def additem():
    if 'username' not in login_session:
        return redirect('/')
    conn = sqlite3.connect('catalog')
    c = conn.cursor()
    c.execute("SELECT * FROM categories")
    sqlresults = c.fetchall()
    global state
    login_session['state']=state
    return render_template("additem.html", results=sqlresults,STATE=state)


@app.route('/itemform', methods=['POST'])
def itemform():
    if 'username' not in login_session:
        return redirect('/')
    conn = sqlite3.connect('catalog')
    c = conn.cursor()
    name=request.form['item_name']
    description=request.form['description']
    category=request.form['category']
    user=login_session['email']
    c.execute("INSERT INTO item(name,description,category,user) VALUES(?,?,?,?);", (name, description, category, user,))
    conn.commit()
    return redirect("/")

@app.route('/catelog.json')
def catelog_json():
    conn = sqlite3.connect('catalog')
    c = conn.cursor()
    c.execute("SELECT * FROM categories")
    sqlresults = c.fetchall()
    jso = {"category": []}
    i=0
    for row in sqlresults:
        jso['category'].append({
                "id": row[0],
                "Item": [],
                "name": row[1]

                })
        c.execute("SELECT * from item where category=?;", (row[1],))
        res = c.fetchall()

        for data in res:
            jso['category'][i]['Item'].append({
                "cat_id": row[0],
                "title": data[1],
                "description": data[2],
                "item_id": data[0]
            })
        i=i+1


    print(jso)
    return jsonify(jso)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True


    app.run(host='0.0.0.0', port=5000)