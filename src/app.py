from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin
import os
import copy
import json
from datetime import datetime

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


def page_not_found(error):
    return "<h1>Page not found!, sorry d:-D </h1>", 404


if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(404, page_not_found)
    app.run()
