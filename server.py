import json, MySQLdb
from flask import Flask, jsonify, abort, request

app = Flask(__name__, static_url_path="/static")

### database ###
# establish db connection
def connect_db():
    global db
    global cur
    # the following is purely for example
    db = MySQLdb.connect(host="dursley.socs.uoguelph.ca", # db host, I DO NOT KNOW IF THIS IS WHAT WE USE, JUST AN EXAMPLE !!!
                       user="user", # db username
                       passwd="pass", # db password
                       db="db_name") # name of the db
    cur = db.cursor() # this is the cursor used to execute MySQL commands
    return

# EXAMPLE DB QUERY FUNCTION
def query_db(queryType, query):
    try:
        # example SQL call, command itself is not relevant
        cur.execute("SELECT column FROM table WHERE queryType LIKE %s AND WHERE queryText LIKE %s", (queryType, query)) # execute("MySQL command", list_of_data)
        return cur.fetchone() # retrieves the next row of a query result set
        #return cur.fetchall() # retrieves all (or all remaining) rows of a query result set
    except:
        print "Error: " + query + " of type " + queryType + " not found."
        return None

# EXAMPLE DB STORE FUNCTION
def store_db(queryType, query, result):
    try:
        # example SQL call, command itself is not relevant
        cur.execute("INSERT INTO table WHERE queryType LIKE %s (queryText, column) VALUES (%s, %s)", (queryType, query, result))
    except:
        pass
    return

### api routing ###
# sign up user request
@app.route("/api/v1.0/users/accounts/participants/signup/", methods=["POST"])
def signup_user():
    signup_dict = request.get_json(silent=True) # POST request body

    # 400 error check for required fields
    if(signup_dict["userName"] == ""):
        abort(400)
    if(signup_dict["password"] == ""):
        abort(400)
    if(signup_dict["email"] == ""):
        abort(400)
    if(signup_dict["givenName"] == ""):
        abort(400)
    if(signup_dict["familyName"] == ""):
        abort(400)
    if(signup_dict["country"] == ""):
        abort(400)
    if(signup_dict["province"] == ""):
        abort(400)
    if not isinstance(signup_dict["visualAccessibility"], bool):
        abort(400)
    if not isinstance(signup_dict["hearingAccessibility"], bool):
        abort(400)
    if not isinstance(signup_dict["motorAccessibility"], bool):
        abort(400)
    if not isinstance(signup_dict["cognitiveAccessibility"], bool):
        abort(400)
    if not isinstance(signup_dict["teamCaptain"], bool):
        abort(400)
    if(signup_dict["teamCaptain"] == True):
        if(signup_dict["teamName"] == ""):
            abort(400)
        if not isinstance(signup_dict["teamViewable"], bool):               #Required from requirements, but forgot to include
            abort(400)
        if not isinstance(signup_dict["teamAccessibility"], bool):          #Team Accessibility =/= Individual Accessibility
            abort(400)
        if(signup_dict["member1"] == ""):
            abort(400)
        if(signup_dict["member2"] == ""):
            abort(400)
        if(signup_dict["member3"] == ""):
            abort(400)

    # do MySQL work here #
    if(signup_dict["teamCaptain"] == True):
        try:
            cur.execute("""INSERT INTO Team (teamName, teamViewable, routeID, teamAccessibility)
                        VALUES (%s, %s, %s, %s)""",
                        [
                        (signup_dict["teamName"], signup_dict["teamViewable"], NULL, signup_dict["teamAccessibility"])
                        ])
        except:
            pass

        try:
            # example SQL call, command itself is not relevant
            team = cur.execute("SELECT teamID, teamName, teamViewable, routeID, teamAccessibility FROM Team WHERE teamName=%s", (signup_dict["teamName"])) 
            # execute("MySQL command", list_of_data)
            #return cur.fetchone() # retrieves the next row of a query result set
            #return cur.fetchall() # retrieves all (or all remaining) rows of a query result set
        except:
            print "Error: " + signup_dict["teamName"] + " not found."

    try:
        # example SQL call, command itself is not relevant
        cur.execute("""INSERT INTO User (userName, password, email, givenName, familyName, country, province, city, visualAccessibility, 
                    hearingAccessibility, motorAccessibility, cognitiveAccessibility, teamCaptain, teamID) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
                    [
                    (signup_dict["userName"], signup_dict["password"], signup_dict["email"], signup_dict["givenName"], signup_dict["familyName"],
                    signup_dict["country"], signup_dict["province"], signup_dict["city"], signup_dict["visualAccessibility"], signup_dict["hearingAccessibility"],
                    signup_dict["motorAccessibility"], signup_dict["cognitiveAccessibility"], signup_dict["teamCaptain"], team[0])
                    ])
    except:
        pass

    try:
        # example SQL call, command itself is not relevant
        user = cur.fetchall("""SELECT userID, userName, password, email, givenName, familyName, country, province, city, visualAccessibility, 
                                    hearingAccessibility, motorAccessibility, cognitiveAccessibility, teamCaptain, teamID FROM User WHERE userName=%s""", (signup_dict["userName"])) # execute("MySQL command", list_of_data)
        #return cur.fetchone() # retrieves the next row of a query result set
        #return cur.fetchall() # retrieves all (or all remaining) rows of a query result set (array of arrays of information)
    except:
        print "Error: " + signup_dict["userName"] + " not found."

    # POST response body pulled from database
    signup_response = {}
    if user[13] == True:
        signup_response["userType"] = "CAPTAIN"
    else:
        signup_response["userType"] = "PARTICIPANT"

    signup_response["userID"] = user[0]
    signup_response["userName"] = user[1]
    signup_response["password"] = user[2]
    signup_response["email"] = user[3]
    signup_response["givenName"] = user[4]
    signup_response["familyName"] = user[5]
    signup_response["country"] = user[6]
    signup_response["province"] = user[7]
    signup_response["city"] = user[8]
    signup_response["visualAccessibility"] = user[9]
    signup_response["hearingAccessibility"] = user[10]
    signup_response["motorAccessibility"] = user[11]
    signup_response["cognitiveAccessibility"] = user[12]
    signup_response["teamCaptain"] = user[13]
    signup_response["teamID"] = team[0]

    signup_response["teamName"] = team[1]
    signup_response["teamViewable"] = team[2]
    signup_response["teamAccessibility"] = team[3]

    try:
        # example SQL call, command itself is not relevant
        teamMembers = cur.fetchall("SELECT userID, userName, email, givenName, familyName, teamCaptain FROM User WHERE teamID=%s", (team[0])) # execute("MySQL command", list_of_data)
        #return cur.fetchone() # retrieves the next row of a query result set
        #return cur.fetchall() # retrieves all (or all remaining) rows of a query result set (array of arrays of information)
    except:
        print "Error: " + signup_dict["teamName"] + " not found."

    for i in range(0,9):
        if teamMembers[i][5] == True:
            signup_response["teamCaptainName"] = teamMembers[i]
            del teamMembers[i]

    signup_response["member1"] = teamMembers[0]
    signup_response["member2"] = teamMembers[1]
    signup_response["member3"] = teamMembers[2]
    signup_response["member4"] = teamMembers[3]

    return jsonify(signup_response), 200, {"ContentType":"application/json"}

# log in user request
@app.route("/api/v1.0/users/accounts/login/", methods=["POST"])
def login_user():
    login_dict = request.get_json(silent=True) # POST request body

    # 400 error check for required fields
    if(login_dict["userName"] == ""):
        abort(400)
    if(login_dict["password"] == ""):
        abort(400)

    # 403 error check if user and pass in database match
    # do MySQL work here #
    # ------------------ #
    #                    #

    # POST response body pulled from database
    login_response = {}
    login_response["userType"] = ""
    login_response["userID"] = ""
    login_response["userName"] = ""
    login_response["password"] = ""
    login_response["email"] = ""
    login_response["givenName"] = ""
    login_response["familyName"] = ""
    login_response["country"] = ""
    login_response["province"] = ""
    login_response["city"] = ""
    login_response["visualAccessibility"] = ""
    login_response["hearingAccessibility"] = ""
    login_response["motorAccessibility"] = ""
    login_response["cognitiveAccessibility"] = ""
    login_response["teamCaptain"] = ""
    login_response["teamName"] = ""
    login_response["teamID"] = ""                              #Added this since Team Name can be changed.
    login_response["teamViewable"] = ""
    login_response["teamAccessibility"] = ""
    login_response["teamCaptainName"] = ""                     #The signup may be participant
    login_response["member1"] = ""
    login_response["member2"] = ""
    login_response["member3"] = ""
    login_response["member4"] = ""

    return jsonify(login_response), 200, {"ContentType":"application/json"} 

# delete user request
@app.route("/api/v1.0/users/manage/delete/", methods=["DELETE"])
def delete_user():
    deleteUser_dict = request.get_json(silent=True) # POST request body

    # 400 error check for required fields
    if not isinstance(deleteUser_dict["userID"], int):
        abort(400)
    if(deleteUser_dict["userName"] == ""):
        abort(400)
    if(deleteUser_dict["password"] == ""):
        abort(400)

    # 403 error check if user id in database match
    # do MySQL work here #
    # ------------------ #
    #                    #

    return jsonify({"success":True}), 200, {"ContentType":"application/json"}

# modify user request
@app.route("/api/v1.0/users/manage/edit/", methods=["PUT"])
def modify_user():
    modifyUser_dict = request.get_json(silent=True) # POST request body

    # 400 error check for required fields
    if not isinstance(modifyUser_dict["userID"], int):
        abort(400)

    # 403 error check if user id in database match
    # do MySQL work here #
    # ------------------ #
    #                    #

    return jsonify({"success":True}), 200, {"ContentType":"application/json"}


# search Routes
#### !!! this is not proper parameter passing; looking into this - Matt
@app.route("/api/v1.0/routes/manage/search[?parameters]", methods=["GET"])
def search_routes():
    search_dict = request.get_json(silent=True) # POST request body

    # 400 error check for required fields
    #I'm not sure how to deal with this

    # 403 error check if creating user id in database match
    # do MySQL work here #
    # ------------------ #
    #                    #

    # GET response body pulled from database
    search_response = {}
    search_response["routeName"] = ""
    search_response["routeID"] = ""
    search_response["creatingUserID"] = ""
    search_response["teamNames"] = ""
    search_response["routeType"] = ""
    search_response["busID"] = ""
    search_response["busTime1"] = ""
    search_response["busTime2"] = ""
    search_response["startLat"] = ""
    search_response["startLong"] = ""
    search_response["midLat"] = ""
    search_response["midLong"] = ""
    search_response["endLat"] = ""
    search_response["endLong"] = ""
    search_response["visualAccessibility"] = ""
    search_response["hearingAccessibility"] = ""
    search_response["motorAccessibility"] = ""
    search_response["cognitiveAccessibility"] = ""

    return jsonify(search_response), 200, {"ContentType":"application/json"}

# join route
@app.route("/api/v1.0/routes/manage/join/", methods=["PUT"])
def join_route():
    joinRoute_dict = request.get_json(silent=True) # POST request body

    # 400 error check for required fields
    if(joinRoute_dict["routeName"] == ""):
        abort(400)
    if(joinRoute_dict["routeID"] == ""):
        abort(400)
    if(joinRoute_dict["creatingUserID"] == ""):
        abort(400)
    if(joinRoute_dict["userID"] == ""):
        abort(400)
    if(joinRoute_dict["teamID"] == ""):
        abort(400)

    # do MySQL work here #
    # ------------------ #
    #                    #

    return jsonify({"success":True}), 200, {"ContentType":"application/json"}

# modify team
@app.route("/api/v1.0/teams/teamaccounts/edit/", methods=["PUT"])
def modify_team():
    modifyTeam_dict = request.get_json(silent=True) # POST request body
    
    # 400 error check for required fields
    if not isinstance(modifyTeam_dict["userID"], int):
        abort(400)
    if not isinstance(modifyTeam_dict["teamID"], int):
        abort(400)
    if(modifyTeam_dict["teamName"] == ""):
        abort(400)

    # do MySQL work here #
    # ------------------ #
    #                    #

    return jsonify({"success":True}), 200, {"ContentType":"application/json"}

# join team
@app.route("/api/v1.0/teams/teamaccounts/join/", methods=["PUT"])
def join_team():
    joinTeam_dict = request.get_json(silent=True) # POST request body

    # 400 error check for required fields
    if not isinstance(joinTeam_dict["userID"], int):
        abort(400)
    if(joinTeam_dict["userName"] == ""):
        abort(400)
    if not isinstance(joinTeam_dict["teamID"], int):
        abort(400)
    if(joinTeam_dict["teamName"] == ""):
        abort(400)

    # do MySQL work here #
    # ------------------ #
    #                    #

    # POST response body pulled from database
    joinTeam_response = {}
    joinTeam_response["teamCaptain"] = ""
    joinTeam_response["teamName"] = ""
    joinTeam_response["teamID"] = ""
    joinTeam_response["teamViewable"] = ""
    joinTeam_response["teamAccessibility"] = ""
    joinTeam_response["teamCaptainName"] = ""
    joinTeam_response["member1"] = ""
    joinTeam_response["member2"] = ""
    joinTeam_response["member3"] = ""
    joinTeam_response["member4"] = ""

    return jsonify(joinTeam_response), 200, {"ContentType":"application/json"}

# delete team
@app.route("/api/v1.0/teams/teamaccounts/delete/", methods=["DELETE"])
def delete_team():
    deleteTeam_dict = request.get_json(silent=True) # POST request body

    # 400 error check for required fields
    if not isinstance(deleteTeam_dict["userID"], int):
        abort(400)
    if(deleteTeam_dict["userName"] == ""):
        abort(400)
    if(deleteTeam_dict["password"] == ""):
        abort(400)
    if not isinstance(deleteTeam_dict["teamID"], int):
        abort(400)
    if(deleteTeam_dict["teamName"] == ""):
        abort(400)

    # do MySQL work here #
    # ------------------ #
    #                    #

    return jsonify({"success":True}), 200, {"ContentType":"application/json"}

# leave team
@app.route("/api/v1.0/teams/teamaccounts/leave/", methods=["PUT"])
def leave_team():
    leaveTeam_dict = request.get_json(silent=True) # POST request body

    # 400 error check for required fields
    if(leaveTeam_dict["userID"] == ""):
        abort(400)
    if(leaveTeam_dict["userName"] == ""):
        abort(400)
    if(leaveTeam_dict["password"] == ""):
        abort(400)
    if(leaveTeam_dict["teamID"] == ""):
        abort(400)
    if(leaveTeam_dict["teamName"] == ""):
        abort(400)

    # do MySQL work here #
    # ------------------ #
    #                    #

    return jsonify({"success":True}), 200, {"ContentType":"application/json"}

# THE FOLLOWING ARE PURELY FOR EXAMPLES OF USING FLASK FOR INTERACTING WITH A DICTIONARY #
users = [
    {
        "id": 1,
        "username": u"user1",
        "password": u"password1",
        "email": u"user1@email.com"
    },
    {
        "id": 2,
        "username": u"user2",
        "password": u"password2",
        "email": u"user2@email.com"
    }
]

# retrieve user from database
@app.route("/trickoreat/api/v1.0/users/<string:username>", methods=["GET"])
def get(username):
    # MySQL calls to retrieve data normally goes here
    user = [user for user in users if user["username"] == username]
    if len(user) == 0:
        abort(404)
    return jsonify({"user": user[0]}) # returns json of single user

# create new user in database
@app.route("/trickoreat/api/v1.0/users/", methods=["POST"])
def create():
    # MySQL calls to create data normally goes here
    # example user create, this only requires a username so it"s extremely primitive and needs to be incorporated based on the MySQL database 
    if not request.json or not "username" in request.json:
        abort(400)
    user = {
        "id": users[-1]["id"] + 1,
        "username": request.json["username"],
        "password": "",
        "email": ""
    }
    user.append(user)
    return jsonify({"user": user}), 201

# update user in database
@app.route("/trickoreat/api/v1.0/users/<string:username>", methods=["PUT"])
def update(username):
    # MySQL calls to update data normally goes here
    user = [user for user in users if user["username"] == username]
    if len(user) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if "title" in request.json and type(request.json["title"]) != unicode:
        abort(400)
    if "password" in request.json and type(request.json["password"]) != unicode:
        abort(400)
    if "email" in request.json and type(request.json["email"]) != unicode:
        abort(400)
    user[0]["title"] = request.json.get("title", user[0]["title"])
    user[0]["password"] = request.json.get("password", user[0]["password"])
    user[0]["email"] = request.json.get("email", user[0]["email"])
    return jsonify({"user": user[0]})

# delete user in database
@app.route("/trickoreat/api/v1.0/users/<string:username>", methods=["DELETE"])
def delete(username):
    # MySQL calls to delete data normally goes here
    user = [user for user in users if user["username"] == username]
    if len(user) == 0:
        abort(404)
    users.remove(user[0])
    return jsonify({"result": True})

# END EXAMPLES #



if __name__ == "__main__":
    #connect_db()
    app.run(debug=True)