from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin
import ast
import requests
from datetime import datetime
from fastavro import writer, parse_schema
from csv import reader
import os
import copy
import json
import pandas as pd
import pandavro as pdx
from avro.datafile import DataFileReader
from avro.io import DatumReader
from AccessData import sql_querys 

from config import config
from validations import *

now = datetime.now()
app = Flask(__name__)

# CORS(app)
CORS(app, resources={r"/hired_employee/*": {"origins": "http://localhost:5000"}})
CORS(app, resources={r"/hired_employees/*": {"origins": "http://localhost:5000"}})
CORS(app, resources={r"/departments/*": {"origins": "http://localhost:5000"}})
CORS(app, resources={r"/jobs/*": {"origins": "http://localhost:5000"}})
CORS(app, resources={r"/avro_backup/*": {"origins": "http://localhost:5000"}})
CORS(app, resources={r"/avro_backup_list/*": {"origins": "http://localhost:5000"}})
CORS(app, resources={r"/avro_backup_restore/*": {"origins": "http://localhost:5000"}})
CORS(app, resources={r"/import_historic_CSV/*": {"origins": "http://localhost:5000"}})
CORS(app, resources={r"/hires_by_Q_for_year/*": {"origins": "http://localhost:5000"}})
CORS(app, resources={r"/hires_by_department_having_more_than_mean/*": {"origins": "http://localhost:5000"}})

conexion = MySQL(app)

# Function that returns all employees
@app.route('/hired_employees', methods=['GET'])
def list_hired_employees():
    try:
        cursor = conexion.connection.cursor()
        sql = sql_querys['sql_list_hired_employees']
        print(sql)
        cursor.execute(sql)
        data = cursor.fetchall()
        hired_employees = []
        for fila in data:
            hired_employee = {'id': fila[0], 'name': fila[1], 'datetime': fila[2], 'department_id': fila[3], 'job_id': fila[4]}
            hired_employees.append(hired_employee)
        LogFile("hired_employees list. success: True ->" + str(hired_employees))    
        return jsonify({'hired_employees': hired_employees, 'message': "hired_employees list.", 'success': True})
    except Exception as ex:
        LogFile("hired_employees list.Error success: False") 
        return jsonify({'message': "Error", 'success': False})

# Function that returns all departments
@app.route('/departments', methods=['GET'])
def list_departments():
    try:
        cursor = conexion.connection.cursor()
        sql = sql_querys['sql_departments']
        cursor.execute(sql)
        data = cursor.fetchall()
        departments = []
        for fila in data:
            department = {'id': fila[0], 'department': fila[1]}
            departments.append(department)
        LogFile("departments list. success: True ->" + str(departments))  
        return jsonify({'departments': departments, 'message': "departments list.", 'success': True})
    except Exception as ex:
        LogFile("departments list. Error success: False") 
        return jsonify({'message': "Error", 'success': False})

# Function that returns all jobs
@app.route('/jobs', methods=['GET'])
def list_jobs():
    try:
        cursor = conexion.connection.cursor()
        sql = sql_querys['sql_jobs']
        cursor.execute(sql)
        data = cursor.fetchall()
        jobs = []
        for fila in data:
            job = {'id': fila[0], 'department': fila[1]}
            jobs.append(job)
        LogFile("jobs list. success: True ->" + str(jobs))
        return jsonify({'jobs': jobs, 'message': "jobs list.", 'success': True})
    except Exception as ex:
        LogFile("jobs list. Error success: False")
        return jsonify({'message': "Error", 'success': False})

#Function to register employees one by one
@app.route('/hired_employee', methods=['POST'])
def add_hired_employee():
    if (validate_id(request.json['id']) and validate_name(request.json['name']) and validate_datetime(request.json['datetime']) and validate_department(request.json['department']) and validate_job(request.json['job'])):
        try:
            hired_employee = read_hired_employees_db(request.json['id'])
            if hired_employee != None:
                LogFile("hired employee added . Error ID already exists, cannot be duplicated. success: False ->" + str(request.json))
                return jsonify({'message': "ID already exists, cannot be duplicated.", 'success': False})
            else:
                #search for the department by name and if it doesn't exist I insert it
                department = read_department_db(request.json['department'])
                if department == None:
                    print("deparment not exist, insert that")
                    cursor = conexion.connection.cursor()
                    sql = str(sql_querys['sql_insert_departments']).format(request.json['department'])
                    cursor.execute(sql)
                    conexion.connection.commit() 
                    department = read_department_db(request.json['department'])
                #search for the job by name and if it doesn't exist I insert it
                job = read_jobs_db(request.json['job'])
                if job == None:
                    cursor = conexion.connection.cursor()
                    sql = str(sql_querys['sql_insert_jobs']).format(request.json['job'])
                    cursor.execute(sql)
                    conexion.connection.commit() 
                    job = read_jobs_db(request.json['job'])
                cursor = conexion.connection.cursor()
                sql = str(sql_querys['sql_insert_hired_employees']).format(request.json['id'],
                                                        request.json['name'], request.json['datetime'], department['id'], job['id'])
                cursor.execute(sql)
                conexion.connection.commit() 
                LogFile("hired employee added successfully. success: True ->" + str(request.json))
                return jsonify({'message': "hired employee added successfully.", 'success': True})
        except Exception as ex:
            LogFile("hired employee added . Error success: False ->" + str(request.json))
            return jsonify({'message': "Error", 'success': False})
    else:
        LogFile("hired employee added . Error Invalid parameters. success: False ->" + str(request.json))
        return jsonify({'message': "Invalid parameters...", 'success': False})

#Function to register employees up to 1000
@app.route('/hired_employees', methods=['POST'])
def add_hired_employees():
    response_agrupated_errors =""
    response_agrupated_errors_count =0
    if (len(request.json) <= 1000):
        for field_dict in request.json:
            if (validate_id(field_dict['id']) and validate_name(field_dict['name']) and validate_datetime(field_dict['datetime']) and validate_department(field_dict['department']) and validate_job(field_dict['job'])):
                try:
                    hired_employee = read_hired_employees_db(field_dict['id'])
                    if hired_employee != None:
                        #I save the error to return it in the response
                        field_dict['Error'] = "ID: " + str(field_dict['id']) + " already exists, cannot be duplicated."
                        if (response_agrupated_errors == ""):
                            response_agrupated_errors=str(field_dict)
                        else:
                            response_agrupated_errors=str(response_agrupated_errors) +","+ str(field_dict)
                        response_agrupated_errors_count = response_agrupated_errors_count + 1 
                    else:
                        #search for the department by name and if it doesn't exist I insert it
                        department = read_department_db(field_dict['department'])
                        if department == None:
                            cursor = conexion.connection.cursor()
                            sql = str(sql_querys['sql_insert_departments']).format(field_dict['department'])
                            cursor.execute(sql)
                            conexion.connection.commit() 
                            department = read_department_db(field_dict['department'])
                        #search for the job by name and if it doesn't exist I insert it
                        job = read_jobs_db(field_dict['job'])
                        if job == None:
                            cursor = conexion.connection.cursor()
                            sql = str(sql_querys['sql_insert_jobs']).format(field_dict['job'])
                            cursor.execute(sql)
                            conexion.connection.commit() 
                            job = read_jobs_db(field_dict['job'])
                        cursor = conexion.connection.cursor()
                        sql = str(sql_querys['sql_insert_hired_employees']).format(field_dict['id'],
                                                                field_dict['name'], field_dict['datetime'], department['id'], job['id'])
                        cursor.execute(sql)
                        conexion.connection.commit() 
                except Exception as ex:
                    return jsonify({'message': "Error", 'success': False})
            else:
                #I save the error to return it in the response
                field_dict['Error'] = "Invalid parameters."
                if (response_agrupated_errors == ""):
                    response_agrupated_errors=str(field_dict)
                else:
                    response_agrupated_errors=str(response_agrupated_errors) +","+ str(field_dict)
                response_agrupated_errors_count = response_agrupated_errors_count + 1 
    else:
        LogFile("hired employees added. Error you cannot send more than a thousand for each request.  success: False --> " + str(request.json))
        return jsonify({'message': "you cannot send more than a thousand for each request", 'success': False})
    if (response_agrupated_errors_count > 0):
        response_agrupated_errors = ast.literal_eval(response_agrupated_errors)
        if (response_agrupated_errors_count == len(request.json)):
            LogFile("hired employees added. invalid parameters were detected in all "+ str(response_agrupated_errors_count) + " cases.  success: False. Error cases: " + str(response_agrupated_errors))
            return jsonify({'message':  "invalid parameters were detected in all "+ str(response_agrupated_errors_count) + " cases.",'error cases: ': str(response_agrupated_errors), 'success': False})
        else:
            LogFile("hired employees added. "+  str(len(request.json) - response_agrupated_errors_count) + " new employees added and "+ str(response_agrupated_errors_count) + " invalid parameters cases were detected. Error cases: : " + str(response_agrupated_errors) + ". success: True")
            return jsonify({'message': str(len(request.json) - response_agrupated_errors_count) + " new employees added and "+ str(response_agrupated_errors_count) + " invalid parameters cases were detected.", 'error cases: ': str(response_agrupated_errors), 'success': True})
    else:
        LogFile("hired employees added. "+  str(len(request.json)) + " new employees added. success: True ->" + str(request.json))
        return jsonify({'message': str(len(request.json)) + " new employees added.", 'success': True})


# Function that updates an employee by id
@app.route('/hired_employees', methods=['PUT'])
def udpate_hired_employees():
    if (validate_id(request.json['id']) and validate_name(request.json['name']) and validate_datetime(request.json['datetime']) and validate_department(request.json['department']) and validate_job(request.json['job'])):
        try:
            hired_employee = read_hired_employees_db(request.json['id'])
            if hired_employee != None:
                #search for the department by name and if it doesn't exist I insert it
                department = read_department_db(request.json['department'])
                if department == None:
                    cursor = conexion.connection.cursor()
                    sql = str(sql_querys['sql_insert_departments']).format(request.json['department'])
                    cursor.execute(sql)
                    conexion.connection.commit() 
                    department = read_department_db(request.json['department'])
                #search for the job by name and if it doesn't exist I insert it
                job = read_jobs_db(request.json['job'])
                if job == None:
                    cursor = conexion.connection.cursor()
                    sql = str(sql_querys['sql_insert_jobs']).format(request.json['job'])
                    cursor.execute(sql)
                    conexion.connection.commit() 
                    job = read_jobs_db(request.json['job'])
                cursor = conexion.connection.cursor()
                sql = str(sql_querys['sql_update_hired_employees']).format(request.json['name'], request.json['datetime'], department['id'], job['id'], request.json['id'])
                cursor.execute(sql)
                conexion.connection.commit() 
                LogFile("hired employee updated successfully. success: True ->" + str(request.json))
                return jsonify({'message': "hired employee updated.", 'success': True})
            else:
                LogFile("hired employee not found. success: False ->" + str(request.json))
                return jsonify({'message': "hired employee not found.", 'success': False})
        except Exception as ex:
            LogFile("hired employee updated . Error success: False ->" + str(request.json))
            return jsonify({'message': "Error", 'success': False})
    else:
        LogFile("hired employee updated . Error Invalid parameters. success: False ->" + str(request.json))
        return jsonify({'message': "Invalid parameters...", 'success': False}) 



# Function that delete an employee by id
@app.route('/hired_employees', methods=['DELETE'])
def delete_hired_employees():
    if (validate_id(request.json['id'])):
        try:
            hired_employee = read_hired_employees_db(request.json['id'])
            if hired_employee != None:
                cursor = conexion.connection.cursor()
                sql = str(sql_querys['sql_delete_hired_employees']).format(request.json['id'])
                cursor.execute(sql)
                conexion.connection.commit()  # confirm the deletion.
                LogFile("deletehired employee. success: True, hired employee deleted ->" + str(request.json))
                return jsonify({'message': "hired employee deleted.", 'success': True})
            else:
                LogFile("delete hired employee. success: False, hired employee not found ->" + str(request.json))
                return jsonify({'message': "hired employee not found.", 'success': False})
        except Exception as ex:
            LogFile("delete hired employee. Error success: False")
            return jsonify({'message': "Error", 'success': False})
    else:
        LogFile("delete hired employee . Error Invalid parameters. success: False ->" + str(request.json))
        return jsonify({'message': "Invalid parameters...", 'success': False}) 

# Function that returns an employee by id from DB
def read_hired_employees_db(id):
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT id, name, datetime, department_id, job_id FROM hired_employees WHERE id = '{0}'".format(id)
        
        cursor.execute(sql)
        data = cursor.fetchone()
        if data != None:
            hired_employee = {'id': data[0], 'name': data[1], 'datetime': data[2], 'department_id': data[3], 'job_id': data[4]}
            return hired_employee
        else:
            return None
    except Exception as ex:
        raise ex

# Function that returns an employee from id
@app.route('/hired_employees/<id>', methods=['GET'])
def read_hired_employees(id):
    try:
        hired_employee = read_hired_employees_db(id)
        if hired_employee != None:
            return jsonify({'id': hired_employee, 'message': "hired employee found.", 'success': True})
        else:
            return jsonify({'message': "hired employee not found.", 'success': False})
    except Exception as ex:
        return jsonify({'message': "Error", 'success': False})

# Function that returns an department by department name from DB
def read_department_db(department):
    try:
        cursor = conexion.connection.cursor()
        sql = str(sql_querys['sql_one_departments']).format(department)
        cursor.execute(sql)
        data = cursor.fetchone()
        if data != None:
            department = {'id': data[0], 'department': data[1]}
            return department
        else:
            return None
    except Exception as ex:
        raise ex    

# Function that returns an job by job name from DB
def read_jobs_db(job):
    try:
        cursor = conexion.connection.cursor()
        sql = str(sql_querys['sql_one_jobs']).format(job)
        cursor.execute(sql)
        data = cursor.fetchone()
        if data != None:
            job = {'id': data[0], 'job': data[1]}
            return job
        else:
            return None
    except Exception as ex:
        raise ex   

# Function that generated backup from all DB data in avro file with time stamp in the name
@app.route('/avro_backup', methods=['POST'])
def avro_backup():
    try:
        cursor = conexion.connection.cursor()
        sql = str(sql_querys['sql_backup_list'])
        cursor.execute(sql)
        data = cursor.fetchall()
        hired_employees = []
        for fila in data:
            hired_employee = {u'id': fila[0], u'name': fila[1], u'datetime': fila[2], u'department_id': fila[3],u'job_id': fila[4], u'department': fila[5], u'job': fila[6]}
            hired_employees.append(hired_employee)
        schema = {
            'doc': 'hired_employees.',
            'name': 'hired employees Backup',
            'namespace': 'case study',
            'type': 'record',
            'fields': [
                {'name': 'id', 'type': 'int'},
                {'name': 'name', 'type': 'string'},
                {'name': 'datetime', 'type': 'string'},
                {'name': 'department_id', 'type': 'int'},
                {'name': 'department', 'type': 'string'},
                {'name': 'job_id', 'type': 'int'},
                {'name': 'job', 'type': 'string'},
            ],
        }
        parsed_schema = parse_schema(schema)
        now = datetime.now()
        filebackupname = str('backups/hired_employees_backup-'+ now.strftime("%m-%d-%Y-%H-%M-%S")+'.avro')
        with open(str(filebackupname), 'wb') as out:
            writer(out, parsed_schema, hired_employees)
        LogFile("Avro backup.  success: True. file save --> " + str(filebackupname))
        return jsonify({'Avro backup': "save", 'file name': filebackupname, 'success': True})
    except Exception as ex:
        LogFile("Avro backup.  success: False")
        return jsonify({'message': "Error", 'success': False})

# folder backups path
dir_path = "./backups"
# Function that return a list of backups save in /backups folder (the file name is needeed for restore backup call)
@app.route('/avro_backup_list', methods=['POST'])
def avro_backup_list():
    try:
        # list to store backups avro files
        listbackupfiles = []
        # Iterate directory
        for path in os.listdir(dir_path):
            # check if current path is a file
            if os.path.isfile(os.path.join(dir_path, path)):
                listbackupfiles.append(path)
        LogFile("Avro backup files list.  success: True --> " + str(listbackupfiles))
        return jsonify({'Avro backup files list': listbackupfiles, 'success': True})
    except Exception as ex:
        LogFile("Avro backup files list.  success: False")
        return jsonify({'message': "Error", 'success': False})

# Function that restore backup in to data base from avro backup file (WARNING, this action clean all data in DB and leave only data in backup avro file.)
# This call need GET parameter like that "http://localhost:5000/avro_backup_restore/NAMEFILE" 
@app.route('/avro_backup_restore', methods=['POST'])
def avro_backup_restore():
    print(request.json['file'])
    if (validate_file(request.json['file'])):
        try:
            # put backup avro file into a pandas dataframe
            backupdata = pdx.from_avro('./backups/'+request.json['file'])
            response_agrupated_errors =""
            response_agrupated_errors_count = 0
            numrows = 0
            # call Stores Procedures "truncate_all" to truncate all tables (this action is very sensitive and in production this action would require much more security)
            cursor2 = conexion.connection.cursor()
            cursor2.callproc('truncate_all', [])
            conexion.connection.commit() 
            # iterate through each row in the dataframe
            for index, row in backupdata.iterrows():
                numrows = numrows + 1
                if (validate_id(row['id']) and validate_name(row['name']) and validate_datetime(row['datetime']) and validate_department(row['department']) and validate_job(row['job'])):
                    hired_employee = read_hired_employees_db(str(row['id']))
                    if hired_employee != None:
                        #I save the error to return it in the response
                        hired_employee['Error'] = "ID: " + str(row['id']) + " already exists, cannot be duplicated."
                        if (response_agrupated_errors == ""):
                            response_agrupated_errors=str(hired_employee)
                        else:
                            response_agrupated_errors=str(response_agrupated_errors) +","+ str(hired_employee)
                        response_agrupated_errors_count = response_agrupated_errors_count + 1 
                    else:
                        #search for the department by name and if it doesn't exist I insert it
                        department = read_department_db(row['department'])
                        if department == None:
                            cursor = conexion.connection.cursor()
                            sql = str(sql_querys['sql_insert_departments']).format(row['department'])
                            cursor.execute(sql)
                            conexion.connection.commit() 
                            department = read_department_db(row['department'])
                        #search for the job by name and if it doesn't exist I insert it
                        job = read_jobs_db(row['job'])
                        if job == None:
                            cursor = conexion.connection.cursor()
                            sql = str(sql_querys['sql_insert_jobs']).format(row['job'])
                            cursor.execute(sql)
                            conexion.connection.commit() 
                            job = read_jobs_db(row['job'])
                        cursor = conexion.connection.cursor()
                        sql = str(sql_querys['sql_insert_hired_employees']).format(row['id'],
                                                                row['name'], row['datetime'], department['id'], job['id'])
                        cursor.execute(sql)
                        conexion.connection.commit() 
                else:
                    #I save the error to return it in the response
                    hired_employee = "{'id': "+str(row['id'])+", 'name': '"+str(row['name'])+"', 'datetime': '"+str(row['datetime'])+"', 'department': "+str(row['department'])+", 'job': "+str(row['job'])+", 'Error': 'Invalid parameters.'}"
                    if (response_agrupated_errors == ""):
                        response_agrupated_errors=str(hired_employee)
                    else:
                        response_agrupated_errors=str(response_agrupated_errors) +","+ str(hired_employee)
                    response_agrupated_errors_count = response_agrupated_errors_count + 1 
            if (response_agrupated_errors_count > 0):
                response_agrupated_errors = ast.literal_eval(response_agrupated_errors)
                if (response_agrupated_errors_count == numrows):
                    LogFile("Avro backup restored. invalid parameters were detected in all "+ str(response_agrupated_errors_count) + " cases.  success: False. Error cases: " + str(response_agrupated_errors))
                    return jsonify({'Avro backup restored message':  "invalid parameters were detected in all "+ str(response_agrupated_errors_count) + " cases.",'error cases: ': response_agrupated_errors, 'success': False})
                else:
                    LogFile("Avro backup restored. "+  str(numrows - response_agrupated_errors_count) + " new employees added and "+ str(response_agrupated_errors_count) + " invalid parameters cases were detected. Error cases: : " + str(response_agrupated_errors) + ". success: True File name--> " + str(request.json['file']))
                    return jsonify({'Avro backup restored message': str(numrows - response_agrupated_errors_count) + " new employees added and "+ str(response_agrupated_errors_count) + " invalid parameters cases were detected.", 'error cases: ': response_agrupated_errors, 'success': True})
            else:
                LogFile("Avro backup restored. "+  str(numrows) + " new employees added. success: True. File name--> " + str(request.json['file']))
                return jsonify({'Avro backup restored message': str(numrows) + " new employees added.", 'success': True})
        except Exception as ex:
            LogFile("Avro backup restored. Error success: False. File name--> " + str(request.json['file']))
            return jsonify({'Avro backup restored message': "Error", 'success': False})
    else:
        LogFile("Avro backup restored . Error Invalid parameters. success: False ->" + str(request.json))
        return jsonify({'message': "Invalid parameters...", 'success': False}) 

# This call need GET parameter like that "http://localhost:5000/avro_backup_restore/NAMEFILE" 
@app.route('/import_historic_CSV/<file>', methods=['GET'])
def import_historic_CSV(file):
    try:
        # open file in read mode
        with open(file, 'r') as read_obj:
            # pass the file object to reader() to get the reader object
            csv_reader = reader(read_obj)
            # Iterate over each row in the csv using reader object
            numrows = 0
            response_agrupated_errors  = ""
            response_agrupated_errors_count = 0
            for row in csv_reader:
                # row variable is a list that represents a row in csv
                numrows = numrows +1
                if (validate_id(row[0]) and validate_name(row[1]) and validate_datetime(row[2]) and validate_department(row[3]) and validate_job(row[4])):
                    hired_employee = read_hired_employees_db(str(row[0]))
                    if hired_employee != None:
                        #I save the error to return it in the response
                        hired_employee['Error'] = "ID: " + str(row[0]) + " already exists, cannot be duplicated."
                        if (response_agrupated_errors == ""):
                            response_agrupated_errors=str(hired_employee)
                        else:
                            response_agrupated_errors=str(response_agrupated_errors) +","+ str(hired_employee)
                        response_agrupated_errors_count = response_agrupated_errors_count + 1 
                    else:
                        #search for the department by name and if it doesn't exist I insert it
                        department = read_department_db(row[3])
                        if department == None:
                            cursor = conexion.connection.cursor()
                            sql = str(sql_querys['sql_insert_departments']).format(row[3])
                            cursor.execute(sql)
                            conexion.connection.commit() 
                            department = read_department_db(row[3])
                        #search for the job by name and if it doesn't exist I insert it
                        job = read_jobs_db(row[4])
                        if job == None:
                            cursor = conexion.connection.cursor()
                            sql = str(sql_querys['sql_insert_jobs']).format(row[4])
                            cursor.execute(sql)
                            conexion.connection.commit() 
                            job = read_jobs_db(row[4])
                        cursor = conexion.connection.cursor()
                        sql = str(sql_querys['sql_insert_hired_employees']).format(row[0],
                                                                row[1], row[2], department['id'], job['id'])
                        cursor.execute(sql)
                        conexion.connection.commit() 
                else:
                    #I save the error to return it in the response
                    hired_employee = "{'id': "+str(row[0])+", 'name': '"+str(row[1])+"', 'datetime': '"+str(row[2])+"', 'department': "+str(row[3])+", 'job': "+str(row[4])+", 'Error': 'Invalid parameters.'}"
                    if (response_agrupated_errors == ""):
                        response_agrupated_errors=str(hired_employee)
                    else:
                        response_agrupated_errors=str(response_agrupated_errors) +","+ str(hired_employee)
                    response_agrupated_errors_count = response_agrupated_errors_count + 1 
        if (response_agrupated_errors_count > 0):
            response_agrupated_errors = ast.literal_eval(response_agrupated_errors)
            if (response_agrupated_errors_count == numrows):
                LogFile("import historic CSV . invalid parameters were detected in all "+ str(response_agrupated_errors_count) + " cases.  success: False. Error cases: " + str(response_agrupated_errors))
                return jsonify({'import historic CSV message':  "invalid parameters were detected in all "+ str(response_agrupated_errors_count) + " cases.",'error cases: ': response_agrupated_errors, 'success': False})
            else:
                LogFile("import historic CSV. "+  str(numrows - response_agrupated_errors_count) + " new employees added and "+ str(response_agrupated_errors_count) + " invalid parameters cases were detected. Error cases: : " + str(response_agrupated_errors) + ". success: True")
                return jsonify({'import historic CSV message': str(numrows - response_agrupated_errors_count) + " historical employees added and "+ str(response_agrupated_errors_count) + " invalid parameters cases were detected.", 'error cases: ': response_agrupated_errors, 'success': True})
        else:
            LogFile("import historic CSV. "+  str(numrows) + " new employees added. success: True")
            return jsonify({'import historic CSV message': str(numrows) + " historical employees added.", 'success': True})
    except Exception as ex:
        LogFile("import historic CSV. Error success: False. File name--> " + str(file))
        return jsonify({'import historic CSV message': "Error", 'success': False})

# Function count of hires employees by Q for year
@app.route('/hires_by_Q_for_year/<year>', methods=['GET'])
def hires_by_Q_for_year(year):
    try:
        # call Stores Procedures "hires_by_Q_for_year" 
        cursor2 = conexion.connection.cursor()
        cursor2.callproc('hires_by_Q_for_year', [str(year)])
        data = cursor2.fetchall()
        hired_employees_by_Q_for_year = []
        for fila in data:
            hired_employee_by_Q_for_year = {'department': fila[0], 'job': fila[1], 'Q1': fila[2], 'Q2': fila[3], 'Q3': fila[4], 'Q4': fila[5]}
            hired_employees_by_Q_for_year.append(hired_employee_by_Q_for_year)
        LogFile("Count hired_employees by Q for year: " + str(hired_employees_by_Q_for_year) + ". success: True  File year--> " + str(year))
        return jsonify({'Count hired_employees by Q for year': hired_employees_by_Q_for_year, 'message': "Count hired_employees by Q for year, report OK.", 'success': True})
    except Exception as ex:
        LogFile("hires_by_Q_for_year. Error success: False. File year--> " + str(year))
        return jsonify({'message': "Error", 'success': False})

# Function count of hires employees by department having more than the mean for year
@app.route('/hires_by_department_having_more_than_mean/<year>', methods=['GET'])
def hires_by_department_having_more_than_mean(year):
    try:
        # call Stores Procedures "hires_by_Q_for_year" 
        cursor2 = conexion.connection.cursor()
        cursor2.callproc('hires_by_department_having_more_than_mean', [str(year)])
        data = cursor2.fetchall()
        hired_employees_department_having_more_than_mean = []
        for fila in data:
            hired_employee_department_having_more_than_mean = {'id': fila[0], 'department': fila[1], 'hired': fila[2]}
            hired_employees_department_having_more_than_mean.append(hired_employee_department_having_more_than_mean)
        LogFile("Count hired_employees count of hires employees by department having more than the mean for year: " + str(hired_employees_department_having_more_than_mean) + ". success: True  File year--> " + str(year))
        return jsonify({'Count hired_employees count of hires employees by department having more than the mean for year': hired_employees_department_having_more_than_mean, 'message': "Count hired_employees count of hires employees by department having more than the mean for year, report OK.", 'success': True})
    except Exception as ex:
        LogFile("Count hired_employees count of hires employees by department having more than the mean for year. Error success: False. File year--> " + str(year))
        return jsonify({'message': "Error", 'success': False})

# Function that log one txt file by day
def LogFile(text):
    now = datetime.now()
    try:
        f = open("logs/log_" + now.strftime("%m-%d-%Y")+".txt", "a")
        f.write("\n")
        f.write(now.strftime("%m-%d-%Y-%H-%M-%S")+ " : " + str(text))
        f.close()
        return "log OK"
    except Exception as ex:
        raise ex

def page_not_found(error):
    LogFile("Page not found!, sorry. Error success: False")
    return "<h1>Page not found!, sorry d:-D </h1>", 404


if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(404, page_not_found)
    app.run()
