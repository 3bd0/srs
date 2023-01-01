import mariadb
import datetime
from time import sleep

conn = mariadb.connect(
    user="admin",
    password="Password",
    host="localhost",
    database="students_redistration_system")
cur = conn.cursor()

while True:
    slct = int(input("1. Register New Student\n"
                 "2. Enroll Course\n"
                 "3. Create New Course\n"
                 "4. Create New Schedule\n"
                 "5. Display Student Courses Schedule\n"))
    if slct == 1:
        # Register New Student
        std_name = input("Please Insert Student Name\n")
        bod = input("Please Insert Student Birth of Date in Format YYYY-MM-DD\n")
        query = f""" select * from levels """
        cur.execute(query)
        data = tuple(cur)
        while True:
            print("ID \t Level")
            for level_id, level_name in data:
                print(level_id, "\t", level_name)
            lvl = input("Please Choose Student Level Name\n")
            for level_id, level_name in data:
                if lvl in level_name:
                    founded = 1
                    break
                else:
                    founded = 0
            if founded == 1:
                break
            else:
                print("Wrong Selection, Please Insert Correct Level")
        mob_num = input("Please Insert Student Mobile Number\n")
        email = input("Please Insert Student Email\n")
        addrs = input("Please Insert Student Address\n")

        query = f""" INSERT INTO contacts (mobile_number, email)
        VALUES ('{mob_num}','{email}'); """
        cur.execute(query)
        conn.commit()
        query = f""" INSERT INTO students (student_name, bod)
        VALUES ('{std_name}','{bod}')  """
        cur.execute(query)
        conn.commit()
        query = f""" INSERT INTO addresses (address_description)
        VALUES ('{addrs}')  """
        cur.execute(query)
        conn.commit()
        query = f""" INSERT INTO students (student_name, contact_id, address_id, level_id, bod)
        VALUES ('{std_name}', (select contact_id from contacts where mobile_number = '{mob_num}'),
        (select address_id from addresses where address_description = '{addrs}'),
        (select level_id from levels where level_name = '{lvl}'), '{bod}') """
        cur.execute(query)
        conn.commit()
        print("Student Registered Successfully")
    if slct == 2:
        # Enroll Course
        std_id = input("Insert Student ID\n")
        while True:
            crs_id = input("Insert Course ID\n")
            query = f""" select level_id from students where student_id = {std_id} """
            cur.execute(query)
            std_lvl = tuple(cur)
            query = f""" select level_id from courses where course_id = {crs_id} """
            cur.execute(query)
            crs_lvl = tuple(cur)
            if std_lvl >= crs_lvl:
                query = f""" select * from enrollment_histories where course_id = {crs_id} and student_id = {std_id}; """
                cur.execute(query)
                is_registered = tuple(cur)
                if is_registered == ():
                    query = f""" select max_capacity from courses where course_id = {crs_id} """
                    cur.execute(query)
                    cap = tuple(cur)
                    query = f""" select count(student_id) from enrollment_histories where course_id = {crs_id} """
                    cur.execute(query)
                    std_num = tuple(cur)
                    if std_num < cap:
                        total_hr = input("Please Insert Total Hours\n")
                        query = f""" INSERT INTO enrollment_histories (student_id, course_id, total_hours)
                                VALUES ('{std_id}', '{crs_id}', '{total_hr}')  """
                        cur.execute(query)
                        conn.commit()
                        print("Course Enrolled Successfully")
                        break
                    else:
                        print("Course Has a Full Capacity, Please Choose Another One")
                else:
                    print("You Have Registered This Course Before, Please Choose Another One")
                    continue
            else:
                print("Please Insert A Course Within Your Level or Below")
                continue
    if slct == 3:
        # Create New Course
        crs_id = input("Please Insert Course ID\n")
        query = f""" select * from levels """
        cur.execute(query)
        data = tuple(cur)
        while True:
            print("ID \t Level")
            for level_id, level_name in data:
                print(level_id, "\t", level_name)
            lvl = int(input("Please Choose Level ID Of The Course\n"))
            for level_id, level_name in data:
                if lvl == level_id:
                    founded = 1
                    break
                else:
                    founded = 0
            if founded == 1:
                break
            else:
                print("Wrong Selection, Please Insert Correct Level ID")
        crs_name = input("Please Insert Course Name\n")
        cap = input("Please Insert Max Capacity\n")
        rph = input("Please Insert Hour Rate (Price)\n")
        query = f""" insert into courses (course_id, level_id, course_name, max_capacity, rate_per_hour) 
        values ('{crs_id}', '{lvl}', '{crs_name}', '{cap}', '{rph}'); """
        cur.execute(query)
        conn.commit()
        print("Course Created Successfully")
    if slct == 4:
        while True:
            while True:
                query = f""" select course_id, course_name from courses """
                cur.execute(query)
                data = list(cur)
                print("ID\t\t Course Name")
                for d, cn in data:
                    print(d, "\t", cn)
                crs_id = int(input("Please Insert Course ID\n"))
                for d, cn in data:
                    if crs_id == d:
                        founded = 1
                        break
                    else:
                        founded = 0
                if founded == 1:
                    break
                else:
                    print("Wrong Selection, Please Insert Correct Course ID")
            while True:
                crs_dy = input("Please Select Day Of The Weekdays\n")
                days_list = ['saturday', 'sunday', 'monday', 'tuesday', 'wednesday', 'thursday']
                if crs_dy in days_list:
                    break
                else:
                    print("Please Insert Correct Day")
            crs_st = int(input("Please Insert Course Start Time\n"))
            crs_du = int(input("Please Insert Course Duration\n"))
            query = f""" select start_time, DATE_ADD(start_time, INTERVAL duration HOUR)
            from course_schedules
            where day = '{crs_dy}'; """
            cur.execute(query)
            data = list(cur)
            crt = 1
            st_error_msg = ""
            end_error_msg = ""
            for time in data:
                # is Start Time Between Interval
                if datetime.timedelta(hours=crs_st) > time[0] and datetime.timedelta(hours=crs_st) < time[1]:
                    start_busy = 1
                    query = f""" select course_id from course_schedules
                    where day = '{crs_dy}' and start_time = '{time[0]}' ; """
                    cur.execute(query)
                    result_course = list(cur)[0][0]
                    st_error_msg = f"Your Course is Starting While Course ID {result_course} Running"
                else:
                    start_busy = 0
                # is End Time Between Interval
                alt_time = crs_st + crs_du
                if datetime.timedelta(hours=alt_time) > time[0] and datetime.timedelta(hours=alt_time) < time[1]:
                    end_busy = 1
                    query = f""" select course_id from course_schedules
                    where day = '{crs_dy}' and start_time = '{time[0]}' ; """
                    cur.execute(query)
                    result_course = list(cur)[0][0]
                    end_error_msg = f"Your Course is Finishing While Course ID {result_course} Running"
                else:
                    end_busy = 0

                if start_busy == 1 or end_busy == 1:
                    crt = 0
                    # If Time is Busy
                    # Comparing Level ID Between Courses

                    # 1- From Course Input
                    query = f""" select level_id from courses where course_id = '{crs_id}' """
                    cur.execute(query)
                    # Level ID of Input Course
                    lvl_inp = list(cur)

                    # 2- From Course Loop
                    query = f""" select course_id from course_schedules
                    where day = '{crs_dy}' and start_time = '{time[0]}' ; """
                    cur.execute(query)
                    crsid_lop = list(cur)
                    lop = crsid_lop[0][0]
                    query = f""" select level_id from courses where course_id = '{lop}' """
                    cur.execute(query)
                    # Level ID of Loop Course
                    lvl_lop = list(cur)

                    # Compare lvl_lop & lvl_inp
                    if lvl_lop != lvl_inp:
                        crt = 1
                        break

            if crt == 1:
                query = f""" insert into course_schedules (course_id, day, duration, start_time)
                values ('{crs_id}', '{crs_dy}', '{crs_du}', SEC_TO_TIME('{crs_st * 60 * 60}'));  """
                cur.execute(query)
                conn.commit()
                print("Course Scheduled Successfully")
                break
            else:
                if st_error_msg != "":
                    print(st_error_msg)
                if end_error_msg != "":
                    print(end_error_msg)
                sleep(2)
    if slct == 5:
        # Display Student Schedule
        while True:
            query = f""" select student_id, student_name from students """
            cur.execute(query)
            data = list(cur)
            print("ID\t Student Name")
            for d, cn in data:
                print(d, "\t", cn)
            std_id = int(input("Please Insert Student ID\n"))
            for d, cn in data:
                if std_id == d:
                    founded = 1
                    break
                else:
                    founded = 0
            if founded == 1:
                break
            else:
                print("Wrong Selection, Please Insert Correct Student ID\n\n")
                sleep(2)
        query = f""" select course_id from enrollment_histories where student_id = '{std_id}' """
        cur.execute(query)
        data = list(cur)
        print("ID\tCourseID Day\tDuration Start Time")
        for k in data:
            query = f""" select * from course_schedules where course_id = '{k[0]}' """
            cur.execute(query)
            data = list(cur)
            # print(data)
            for t_id, c_id, dy, du, st in data:
                print(t_id, "\t", c_id, "\t", dy, "\t", du, "\t", st)
