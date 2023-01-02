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

def page_not_found(error):
    return "<h1>Page not found!, sorry d:-D </h1>", 404


if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(404, page_not_found)
    app.run()
