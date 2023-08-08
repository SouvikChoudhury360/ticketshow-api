from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response, jsonify
from flask_login import login_required, current_user
from .models import venue, show, bookings, ratings, booking_time, User
from datetime import datetime
from . import db

main = Blueprint('main', __name__)

# LANDING ROUTE
@main.route('/')
def index():
    welcome = {"welcome": "IITM MAD 2 PROJECT"}  
    return make_response(jsonify(welcome), 200)


# LOGGED IN USER
@main.route('/user')
def logged_user():
    if not current_user:
        return make_response(jsonify({"user": ""}))
    return make_response(jsonify({"user": current_user.email}), 200)


# ALL VENUES AND SHOWS LIST
@main.route('/shows')
def get_shows():
    venues_db = venue.query.all()
    venues = []
    for thisvenue in venues_db:
        showList = show.query.filter_by(venue_id=thisvenue.id)
        current_venue = {"id": thisvenue.id,"name": thisvenue.name, "capacity": thisvenue.capacity, "address": thisvenue.address,"shows": []}
        for thisshow in showList:
            current_show = {"id": thisshow.id, "title": thisshow.title, "ticket_price": thisshow.ticket_price, "tags": thisshow.tags, "starting_time": thisshow.starting_time, "ending_time": thisshow.ending_time, "seats_left": thisshow.capacity}
            current_venue['shows'].append(current_show)
        venues.append(current_venue)
    return make_response(jsonify(venues), 200)


# GET SINGLE SHOW
@main.route('/show/<int:show_id>', methods=['GET'])
def get_show(show_id):
    thisshow = show.query.get_or_404(show_id)
    show_output = {"id": thisshow.id, "title": thisshow.title, "ticket_price": thisshow.ticket_price, "tags": thisshow.tags, "starting_time": thisshow.starting_time, "ending_time": thisshow.ending_time, "seats_left": thisshow.capacity}
    return make_response(jsonify(show_output))

# GET SINGLE VENUE 
@main.route('/venue/<int:venue_id>', methods=['GET'])
def get_venue(venue_id):
    thisvenue = venue.query.get_or_404(venue_id)
    venue_output = {"address": thisvenue.address, "name": thisvenue.name, "capacity": thisvenue.capacity, "id": thisvenue.id}
    return make_response(jsonify(venue_output))

# CREATE A VENUE
@main.route('/createVenue', methods=['POST'])
def createVenue_post():
    req = request.json
    address = req['address']
    name = req['name']
    capacity = req['capacity']
    new_venue = venue(name=name, address= address, capacity=capacity)
    db.session.add(new_venue)
    db.session.commit()
    return make_response(jsonify({"address": address, "name": name, "capacity": capacity, "id": new_venue.id}))


# UPDATE A VENUE 
@main.route("/venue/<int:venue_id>/edit", methods=['PATCH'])
def editVenue(venue_id):
    thisvenue = venue.query.get_or_404(venue_id)
    req = request.json
    if "name" in  req:
        thisvenue.name = req["name"]
    if "address" in req:
        thisvenue.address = req["address"]
    if "capacity" in req:
        thisvenue.capacity = req["capacity"]    
    db.session.commit()
    return make_response(jsonify({"name": thisvenue.name, "address": thisvenue.address, "capacity": thisvenue.capacity, "id": thisvenue.id}))


# DELETE A VENUE
@main.route("/venue/<int:venue_id>/delete", methods=['DELETE'])
def deleteVenue(venue_id):
    thisvenue = venue.query.get_or_404(venue_id)
    shows_list = show.query.all()
    bookings_list = bookings.query.all()
    for thisshow in shows_list:
        if thisshow.venue_id == thisvenue.id:
            for thisbooking in bookings_list:
                if thisbooking.show_id == thisshow.id:
                    db.session.delete(thisbooking)
            db.session.delete(thisshow)
    db.session.delete(thisvenue)
    db.session.commit()
    return make_response(jsonify({"delete": "successful"}))


# CREATE A SHOW
@main.route('/<int:venue_id>/createShow', methods=['POST'])
def createShow(venue_id):
    req = request.json
    thisvenue = venue.query.filter_by(id=venue_id).first()
    title = req['title']
    tags =  req['tags']
    ticket_price = req['ticket_price']
    start_time = datetime.strptime(req['starting_time'], '%Y-%m-%dT%H:%M:%S.%f%z')
    end_time = datetime.strptime(req['ending_time'], '%Y-%m-%dT%H:%M:%S.%f%z')
    thisshow = show(title=title, tags=tags, ticket_price=ticket_price, starting_time=start_time, ending_time=end_time, capacity=thisvenue.capacity, venue_id=thisvenue.id)
    db.session.add(thisshow)
    db.session.commit()
    return make_response(jsonify({"id": thisshow.id, "title": thisshow.title, "ticket_price": thisshow.ticket_price, "tags": thisshow.tags, "starting_time": thisshow.starting_time, "ending_time": thisshow.ending_time, "seats_left": thisshow.capacity}))


# DELETE A SHOW
@main.route("/show/<int:show_id>/delete", methods=['DELETE'])
def deleteShow(show_id):
    thisshow = show.query.get_or_404(show_id)
    bookings_list = bookings.query.all()
    for thisbooking in bookings_list:
        if thisbooking.show_id == thisshow.id:
            db.session.delete(thisbooking)
    db.session.delete(thisshow)
    db.session.commit()
    return make_response(jsonify({"delete": "successful"}))


# UPDATE A SHOW 
@main.route("/show/<int:show_id>/edit", methods=['PATCH'])
def editShow(show_id):
    thisshow = show.query.get_or_404(show_id)
    req = request.json
    if "title" in req:
        thisshow.title = req['title']
    if "tags" in req:
        thisshow.tags = req['tags']
    if "ticket_price" in req:
        thisshow.ticket_price = req['ticket_price']
    if "starting_time" in req:
        thisshow.starting_time = datetime.strptime(req['starting_time'], '%Y-%m-%dT%H:%M:%S.%f%z')
    if "ending_time" in req:
        thisshow.ending_time = datetime.strptime(req['ending_time'], '%Y-%m-%dT%H:%M:%S.%f%z')
    db.session.commit()
    return make_response(jsonify({"id": thisshow.id, "title": thisshow.title, "ticket_price": thisshow.ticket_price, "tags": thisshow.tags, "starting_time": thisshow.starting_time, "ending_time": thisshow.ending_time, "seats_left": thisshow.capacity}))


# CREATE A BOOKING 
@main.route('/booking/<int:show_id>', methods=['POST'])
def booking_post(show_id):
    req = request.json
    count = req['count']
    userid = req['userid']
    new_booking = bookings(show_id=show_id, count=int(count), user_id=int(userid))
    thisshow = show.query.get_or_404(show_id)
    if thisshow.capacity < int(count) :
        return make_response(404)
    thisshow.capacity = thisshow.capacity - int(count)
    db.session.add(new_booking)
    db.session.commit()
    current_date = datetime.today()
    new_booking_time = booking_time(booking_time= current_date, user_id = int(userid))
    db.session.add(new_booking_time)
    db.session.commit()
    return make_response(jsonify({"booking_id": new_booking.id, "tickets_confirmed": new_booking.count}))


# GET ALL BOOKING FOR USER
@main.route('/mybookings/<int:userid>', methods= ['GET'])
def mybookings(userid):
    bookingsList = bookings.query.filter_by(user_id=userid)
    showlist = {}
    for thisbooking in bookingsList:
        thisshow = show.query.filter_by(id=thisbooking.show_id).first()
        thisvenue = venue.query.filter_by(id=thisshow.venue_id).first()
        thisrating = ratings.query.filter((ratings.user_id==userid) & (ratings.show_id == thisshow.id)).count()
        rated = False
        if thisrating > 0:
            rated = True
        showlist[thisbooking.id] = {"show_id": thisshow.id,"show": thisshow.title, "starting_time": thisshow.starting_time, "ending_time": thisshow.ending_time, "ticket_count": thisbooking.count, "total_cost": thisbooking.count * thisshow.ticket_price, "venue": thisvenue.name, "address": thisvenue.address, "israted": rated}
    return make_response(jsonify(showlist))

@main.route('/reminder', methods = ['GET'])
def reminder():
    booked = booking_time.query.all()
    allusers = User.query.all()
    output = []
    for thisuser in allusers:
        flag = False
        for booker in booked:
            if booker.user_id == thisuser.id:
                flag = True
        if flag == False:
            temp = {
                "email": thisuser.email,
                "name": thisuser.name,
                "id": thisuser.id 
            }
            output.append(temp)
    return make_response(output)

# ADD A REVIEW
@main.route('/rating/<int:show_id>', methods=['POST'])
def rating_post(show_id):
    req = request.json
    rating = req['rating']
    userid = req['userid']
    new_rating = ratings(show_id=show_id, rating=int(rating), user_id=int(userid))
    db.session.add(new_rating)
    db.session.commit()
    return make_response(jsonify({"rating": rating}))


# ANALYTICS
@main.route('/analytics/<int:show_id>', methods=['GET'])
def analytics(show_id):
    thisshow = show.query.filter_by(id=show_id).first()
    ratings_list = ratings.query.all()
    rating_list = [0,0,0,0,0]
    for rating in ratings_list:
        if rating.show_id == show_id:
            rating_list[rating.rating-1] += 1
    return make_response(jsonify({"ratings": rating_list, "show": thisshow.title}))



# SEARCH ACTUAL
@main.route('/search/shows', methods=['GET', 'POST'])
def search_shows():
    req = request.json
    search_text = req['show_search']
    search = "%{}%".format(search_text)
    showlist = show.query.filter(show.title.like(search)).all()
    showtags = show.query.filter(show.tags.like(search)).all()
    finallist = showlist
    for newshow in showtags:
        exists = False
        for thisshow in finallist:
            if thisshow.id == newshow.id:
                exists = True
        if exists == False:
            finallist.append(newshow)
    output = []
    for thisshow in finallist:
        temp = {
            "id": thisshow.id,
            "title": thisshow.title,
            "starting_time": thisshow.starting_time,
            "ending_time": thisshow.ending_time,
            "capacity": thisshow.capacity,
            "ticket_price": thisshow.ticket_price,
            "tags": thisshow.tags, 
        }
        output.append(temp)
    return make_response(output)
