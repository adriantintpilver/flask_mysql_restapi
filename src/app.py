from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin
import ast
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

from config import config
from validations import *

now = datetime.now()
app = Flask(__name__)

# CORS(app)
CORS(app, resources={r"/hired_employees/*": {"origins": "http://localhost:5000"}})
CORS(app, resources={r"/departments/*": {"origins": "http://localhost:5000"}})
CORS(app, resources={r"/jobs/*": {"origins": "http://localhost:5000"}})

conexion = MySQL(app)

# Function that returns all employees
@app.route('/hired_employees', methods=['GET'])
def list_hired_employees():
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT id, name, datetime, department_id, job_id FROM hired_employees ORDER BY id ASC"
        cursor.execute(sql)
        data = cursor.fetchall()
        hired_employees = []
        for fila in data:
            hired_employee = {'id': fila[0], 'name': fila[1], 'datetime': fila[2], 'department_id': fila[3], 'job_id': fila[4]}
            hired_employees.append(hired_employee)
        return jsonify({'hired_employees': hired_employees, 'message': "hired_employees list.", 'success': True})
    except Exception as ex:
        return jsonify({'message': "Error", 'success': False})

# Function that returns all departments
@app.route('/departments', methods=['GET'])
def list_departments():
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT id, department FROM departments ORDER BY id ASC"
        cursor.execute(sql)
        data = cursor.fetchall()
        departments = []
        for fila in data:
            department = {'id': fila[0], 'department': fila[1]}
            departments.append(department)
        return jsonify({'departments': departments, 'message': "departments list.", 'success': True})
    except Exception as ex:
        return jsonify({'message': "Error", 'success': False})

# Function that returns all jobs
@app.route('/jobs', methods=['GET'])
def list_jobs():
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT id, job FROM jobs ORDER BY id ASC"
        cursor.execute(sql)
        data = cursor.fetchall()
        jobs = []
        for fila in data:
            job = {'id': fila[0], 'department': fila[1]}
            jobs.append(job)
        return jsonify({'jobs': jobs, 'message': "jobs list.", 'success': True})
    except Exception as ex:
        return jsonify({'message': "Error", 'success': False})


#Function to register employees one by one
@app.route('/hired_employee', methods=['POST'])
def add_hired_employee():
    if (validate_id(request.json['id']) and validate_name(request.json['name']) and validate_datetime(request.json['datetime']) and validate_department_id(request.json['department_id']) and validate_job_id(request.json['job_id']) and validate_department(request.json['department']) and validate_job(request.json['job'])):
        try:
            hired_employee = read_hired_employees_db(request.json['id'])
            if hired_employee != None:
                return jsonify({'message': "ID already exists, cannot be duplicated.", 'success': False})
            else:
                #search for the department by name and if it doesn't exist I insert it
                department = read_department_db(request.json['department'])
                if department == None:
                    print("deparment not exist, insert that")
                    cursor = conexion.connection.cursor()
                    sql = """INSERT INTO departments (department) 
                    VALUES ('{0}')""".format(request.json['department'])
                    cursor.execute(sql)
                    conexion.connection.commit() 
                    department = read_department_db(request.json['department'])
                #search for the job by name and if it doesn't exist I insert it
                job = read_jobs_db(request.json['job'])
                if job == None:
                    print("job not exist, insert that")
                    cursor = conexion.connection.cursor()
                    sql = """INSERT INTO jobs (job) 
                    VALUES ('{0}')""".format(request.json['job'])
                    cursor.execute(sql)
                    conexion.connection.commit() 
                    job = read_jobs_db(request.json['job'])
                cursor = conexion.connection.cursor()
                sql = """INSERT INTO hired_employees (id, name, datetime, department_id, job_id) 
                VALUES ('{0}', '{1}', '{2}', {3}, {4})""".format(request.json['id'],
                                                        request.json['name'], request.json['datetime'], department['id'], job['id'])
                cursor.execute(sql)
                conexion.connection.commit() 
                return jsonify({'message': "hired employee added successfully.", 'success': True})
        except Exception as ex:
            return jsonify({'message': "Error", 'success': False})
    else:
        return jsonify({'message': "Invalid parameters...", 'success': False})

# Function that returns an employee by id by DB
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
        sql = "SELECT id, department FROM departments WHERE department = '{0}'".format(department)
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
        sql = "SELECT id, job FROM jobs WHERE job = '{0}'".format(job)
        cursor.execute(sql)
        data = cursor.fetchone()
        if data != None:
            job = {'id': data[0], 'job': data[1]}
            return job
        else:
            return None
    except Exception as ex:
        raise ex 

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
                            sql = """INSERT INTO departments (department) 
                            VALUES ('{0}')""".format(row[3])
                            cursor.execute(sql)
                            conexion.connection.commit() 
                            department = read_department_db(row[3])
                        #search for the job by name and if it doesn't exist I insert it
                        job = read_jobs_db(row[4])
                        if job == None:
                            cursor = conexion.connection.cursor()
                            sql = """INSERT INTO jobs (job) 
                            VALUES ('{0}')""".format(row[4])
                            cursor.execute(sql)
                            conexion.connection.commit() 
                            job = read_jobs_db(row[4])
                        cursor = conexion.connection.cursor()
                        sql = """INSERT INTO hired_employees (id, name, datetime, department_id, job_id) 
                        VALUES ('{0}', '{1}', '{2}', {3}, {4})""".format(row[0],
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
                return jsonify({'import historic CSV message':  "invalid parameters were detected in all "+ str(response_agrupated_errors_count) + " cases.",'error cases: ': response_agrupated_errors, 'success': False})
            else:
                return jsonify({'import historic CSV message': str(numrows - response_agrupated_errors_count) + " historical employees added and "+ str(response_agrupated_errors_count) + " invalid parameters cases were detected.", 'error cases: ': response_agrupated_errors, 'success': True})
        else:
            return jsonify({'import historic CSV message': str(numrows) + " historical employees added.", 'success': True})
    except Exception as ex:
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
        return jsonify({'Count hired_employees by Q for year': hired_employees_by_Q_for_year, 'message': "Count hired_employees by Q for year, report OK.", 'success': True})
    except Exception as ex:
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
        return jsonify({'Count hired_employees count of hires employees by department having more than the mean for year': hired_employees_department_having_more_than_mean, 'message': "Count hired_employees count of hires employees by department having more than the mean for year, report OK.", 'success': True})
    except Exception as ex:
        return jsonify({'message': "Error", 'success': False})

def page_not_found(error):
    return "<h1>Page not found!, sorry d:-D </h1>", 404


if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(404, page_not_found)
    app.run()
