import db_connections
import pyrebase
from db_connections import find_flights
from trains_scrape import find_trains
from hotels_scrape import find_hotels
from conversions import find_flt_duration
from flask import Flask, render_template, request, redirect
from pprint import pprint
from datetime import date
from random import randint

config = {
    "apiKey": "AIzaSyAiPuEH6tsR4h36GJKDzKtv87-2E9u0_oA",
    "authDomain": "bon-voyage-d2ff1.firebaseapp.com",
    "databaseURL": "https://bon-voyage-d2ff1.firebaseio.com",
    "storageBucket": "bon-voyage-d2ff1.appspot.com"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()
app = Flask(__name__)

#global variables
loggedIn = False
flights = []
trains = []
hotels = []
roomConf = []
priceConf = []
booked_fl = []
booked_tr = []
booked_ht = []

@app.route('/')
def hello_world():
    return render_template('index.html', login = loggedIn)

@app.route('/flights-display', methods = ["GET", "POST"])
def show_flights():
    global flights
    clas = 'Economy'
    if request.method == 'POST':
        typ = request.form['type']
        print(typ)
        src = request.form['src']
        print(src)
        des = request.form['des']
        print(des)
        dep_date = request.form['dep_date']
        print(dep_date)
        ret_date = request.form['ret_date']
        print(ret_date)
        adults = request.form['adults']
        print(adults)
        # kids = request.form['kids']
        # print(kids)
        clas = request.form['class']
        print(clas)
        flights = find_flights(src, des, dep_date)
    pprint(flights)
    return render_template('flights.html', flights = flights, clas = clas)

@app.route('/add-flight/<fltno>')
def add_flight(fltno):
    global booked_fl
    print(fltno)
    print(flights)
    for fl in flights:
        if fl['fltno'] == fltno:
            print('adding', fltno, 'to booked_fl')
            booked_fl.append(fl)
            print(fl)
            break
    print(booked_fl)
    return redirect('/checkout')

@app.route('/trains-display', methods = ["GET", "POST"])
def show_trains():
    global trains
    if request.method == 'POST':
        typ = request.form['type']
        print(typ)
        src = request.form['src']
        print(src)
        des = request.form['des']
        print(des)
        dep_date = request.form['dep_date']
        print(dep_date)
        ret_date = request.form['ret_date']
        print(ret_date)
        adults = request.form['adults']
        print(adults)
        kids = request.form['kids']
        print(kids)
        clas = request.form['class']
        print(clas)
        year, month, date = dep_date.split('-')
        trains = find_trains(src, des, date, month, year, clas)
    print(trains)
    return render_template('trains.html', trains = trains, clas = clas)

@app.route('/add-train/<trno>')
def add_train(trno):
    global booked_tr
    print(trno)
    print(trains)
    for tr in trains:
        if tr['trn_no'] == trno:
            print('adding', trno, 'to booked_tr')
            booked_tr.append(tr)
            print(tr)
            break
    print(booked_tr)
    return redirect('/checkout')

@app.route('/hotels-display', methods = ['GET', 'POST'])
def show_hotels():
    global hotels
    global roomConf
    if request.method == 'POST':
        city = request.form['city']
        print(city)
        checkin = request.form['checkin']
        print(checkin)
        checkout = request.form['checkout']
        print(checkout)
        room1 = request.form['room1']
        print(room1)
        room2 = request.form['room2']
        print(room2)
        roomConf = [room1, room2]
        hotels = find_hotels(city, checkin, checkout, '2', [room1, room2])
    print(len(hotels))
    pprint(hotels[0])
    pprint(hotels[1])
    # for hotel in hotels:
    #     print(hotel['name'],hotel['priceRange'],sep=':')
    return render_template('hotels.html', hotels=hotels, checkin = checkin, checkout = checkout)

@app.route('/add-hotel/<hid>/<checkin>/<checkout>')
def add_hotel(hid, checkin, checkout):
    global booked_ht
    global roomConf
    global priceConf
    print(hid)
    yr, month, day = checkin.split('-')
    checkin = date(int(yr), int(month), int(day))
    yr, month, day = checkout.split('-')
    checkout = date(int(yr), int(month), int(day))
    days = (checkout - checkin).days
    print(days)
    print(roomConf)
    print(len(hotels))
    for ht in hotels:
        if str(ht['id']) == hid:
            print('adding', ht, 'to booked_ht')
            base = int(ht['price'][1:])
            adder = randint(300,500)
            priceConf = [0]*len(roomConf)
            for i in range(len(roomConf)):
                if roomConf[i] == '3' or roomConf[i] == 3:
                    priceConf[i] = base + adder
                else:
                    priceConf[i] = base
            ht['roomConf'] = roomConf
            ht['priceConf'] = priceConf
            ht['days'] = days
            ht['roomCount'] = [i for i in range(len(roomConf))]
            ht['finalPriceConf'] = [x*days for x in priceConf]
            ht['totalBaseCost'] = sum(ht['finalPriceConf'])
            ht['tax'] = int(ht['totalBaseCost'] * 0.12)
            ht['bookingCharge'] = int(ht['totalBaseCost'] * 0.04)
            ht['totalPrice'] = ht['totalBaseCost'] + ht['tax'] + ht['bookingCharge']
            booked_ht.append(ht)
            print(ht)
            break
    print(booked_ht)
    return redirect('/checkout')
    # return 'done'

@app.route('/signup',methods=['GET','POST'])
def signup():
    global loggedIn
    successful = "Successfully Signed In!!"
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        pwd = request.form['password']
        city = request.form['city']
        contact = request.form['contact']
        data = {
            "email" : email,
            "name" : name,
            "city" : city,
            "contact" : contact       
        }
        db.child("users").child(contact).set(data)
        auth.create_user_with_email_and_password(email, pwd)
        loggedIn = True
    return render_template('index.html', login = True,s=successful)

@app.route('/checkout')
def checkout():
    global booked_fl
    global booked_tr
    global booked_ht
    pprint(booked_ht)
    pprint(booked_fl)
    pprint(booked_tr)
    return render_template('booking.html', hotels = booked_ht, flights = booked_fl, trains = booked_tr)

@app.route('/login',methods=['GET','POST'])
def login():
    global loggedIn
    unsucessful = 'Please enter correct credentials!'
    if(request.method == 'POST'):
        email = request.form['email']
        password = request.form['password']
        print(email, password)
        loggedIn = False
        successful = 'Login Successful'+'\nWelcome! '+str(email)
        try:
            auth.sign_in_with_email_and_password(email,password)
            loggedIn = True
            return render_template('index.html',s=successful, login = True) 
        except:
            return render_template('login.html', us=unsucessful)
    return render_template('login.html')

@app.route('/logout')
def logout():
    global loggedIn
    loggedIn = False
    return render_template('index.html', login = False)

@app.route('/pay',methods=['GET','POST'])
def pay():
    if request.method == 'POST':
        number = request.form['number']
        name = request.form['name']
        cvv = request.form['cvv']
        expiry = request.form['expiry']
        print(number,name,cvv,expiry)
    return render_template('booking.html')

@app.errorhandler(404)
def error_handle(error):
    return 'Page not found'

if __name__ == '__main__':
    app.run(debug = True)
