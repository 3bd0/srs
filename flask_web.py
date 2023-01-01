from flask import Flask, render_template, request, jsonify, url_for
import requests
import mariadb
import jinja2


conn = mariadb.connect(
    user="admin",
    password="Password",
    host="localhost",
    database="students_redistration_system")
cur = conn.cursor()

app = Flask(__name__)

env = jinja2.Environment(autoescape=True)


@app.route('/')
def index():
    return render_template("index.html")


@app.route("/all_courses.html")
def all_courses():
    query = f""" select * from courses """
    cur.execute(query)
    data = list(cur)
    context = {'title': "SRS | All Courses",
               'data': data}
    return render_template("all_courses.html", **context)


@app.route("/courses_schedules.html")
def courses_schedules():
    query = f""" select * from course_schedules """
    cur.execute(query)
    data = list(cur)
    context = {'title': "SRS | Courses Schedule",
               'data': data}
    return render_template("courses_schedules.html", **context)


@app.route("/registered_students.html")
def registered_students():
    query = f""" select student_id, student_name,mobile_number,email,address_description,level_name,bod
    from students s
    join contacts c on c.contact_id = s.contact_id
    join addresses a on a.address_id = s.address_id
    join levels l on l.level_id = s.level_id; """
    cur.execute(query)
    data = list(cur)
    context = {'title': "SRS | Registered Students",
               'data': data}
    return render_template("registered_students.html", **context)


@app.route('/api/v1/student_details', methods=['GET'])
def student_details():
    query = f""" select student_id, student_name,mobile_number,email,address_description,level_name,bod
    from students s
    join contacts c on c.contact_id = s.contact_id
    join addresses a on a.address_id = s.address_id
    join levels l on l.level_id = s.level_id; """
    cur.execute(query)
    data = list(cur)
    my_api = []
    for sid, sn, mn, em, ad, lvl, bod in data:
        result = {"student_id": sid, "student_name": sn, "mobile_number": mn, "email": em,
                  "address_description": ad, "level_name": lvl, "bod": bod}
        my_api.append(result)
    # Checking API Authorization
    auth = request.headers.get('Authorization')
    query = f""" select password from users_auth where password = '{auth}'"""
    cur.execute(query)
    data = list(cur)
    if data != []:
        return jsonify({'code': 200, 'data': my_api}), 200
    else:
        return jsonify({"status_code": 400, "error": "Authentication Failed"}), 400


app.run(debug=True, port=8080)
