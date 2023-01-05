## FLASK MYSQL RESTAPI

FLASK MYSQL RESTAPI is a dockerized application to store, backup, publish and perform ABM functions on hiring people for different departments and jobs. It also publishes some statistics on this data.
Use HTTP protocol and the GET, POST, PUT and DELETE methods.
Publish various services through a Python Flask API, using a MySql database.

## Run in local

# without using docker
    You will need python installed and a running MySql database on port 3306, with the credentials from the ./config.py file
        from the root directory of the project run the following scripts
        ```bash
        $ pip install -r requirements.txt
        ```
        ```bash
        $ python src/app.py
        ```
# using docker
    You will need to have docker and docker compose installed.
        From the root directory of the project run the following scripts
        ```bash
        docker-compose up
        ```
in both cases you can now point to http://localhost:5000/ to use the different services of the application

# Clarification on how to build the different calls to services 
The calls to the different services are made through the URL "http;//localhost:5000/" adding the service and the variables to send if necessary.

## Service: import_historic_CSV Method: GET
This service is used to import data from a .CSV file (an example of the name <b>historical_data.csv</b> is included in the code) This file should have the values separated by commas "," following the example below:
```bash
4535,Marcelo Gonzalez,2021-01-28T16:02:08Z, Fisheries Department, Sailor,
4572,Lidia Mendez,2021-03-28T16:01:28Z, National Bank, Accountant,
4545,Angel buttler,2021-05-28T16:02:08Z, Supply chain, Stock Handler Sr,
...
```
the name of the file to use is passed in the end of URL, call following the example:
```bash
http://localhost:5000/avro_backup_restore/historical_data.csv
```
## GET Service: hired_employees Method: GET
Service that by GET method returns a list of hired employees in JSON format as the following example:
Call: <b>http://localhost:5000/hired_employees</b>
example response return:
```bash
{
    "hired_employees": [
    {
      "datetime": "2022-12-28T16:02:08Z",
      "department_id": 1,
      "id": 2,
      "job_id": 1,
      "name": "john Hand"
    }
    ],
  "message": "hired_employees list.",
  "success": true
}
```

## GET Service: departments Method: GET
Service that by GET method returns a list of departments in JSON format as the following example:
Call: <b>http://localhost:5000/departments</b>
example response return:
```bash
{
    "departments": [
    {
      "department": "Fire Station",
      "id": 1
    }
    ],
  "message": "departments list.",
  "success": true
}
```
## GET Service: jobs Method: GET
Service that by GET method returns a list of jobs in JSON format as the following example:
Call: <b>http://localhost:5000/jobs</b>
example response return:
```bash
{
    "jobs": [
    {
      "department": " Sailor",
      "id": 1
    }
    ],
  "message": "jobs list.",
  "success": true
}
```
## ADD Service: hired_employee Method: POST
Service that registers an employee by posting a JSON with the format of the example.
```bash
A clarification that applies to all registrations for new employees, both the department and the job are always passed in 
text and the application search for the department or job, if it does not find it in the table it adds it and if it finds 
it it puts the id that it already had.
```
Call: <b>http://localhost:5000/hired_employee</b>
POST call json example:
```bash
{
    "id": 2,
    "name": "john Hand",
    "datetime": "2022-12-28T16:02:08Z",
    "department": "fire station",
    "job": "adminitrator"
}
```
example response return:
```bash
{
  "message": "ID already exists, cannot be duplicated.",
  "success": false
}
```
## ADD MANY Service: hired_employees Method: POST
Service that registers up to 1000 employees at once, posting a JSON with the format of the following example. This service returns a Jason with the error cases and a detail of why each one was rejected.
```bash
A clarification that applies to all registrations for new employees, both the department and the job are always passed in 
text and the application search for the department or job, if it does not find it in the table it adds it and if it finds 
it it puts the id that it already had.
```
Call: <b>http://localhost:5000/hired_employees</b>
POST call json example:
```bash
[    
  {
      "name": "Belinda Machintons",
      "datetime": "2020-11-28T16:02:08Z",
      "department": "hospital",
      "id": 4,
      "job": "Nurse"
  },
    {
      "name": "Cecil keenan",
      "datetime": "2020-11-28T16:02:08Z",
      "department": "Sap Company",
      "id": 5,
      "job": "Deal Execution Bussiness Manager"
  },
      {
      "name": "Jhonatan Tole",
      "datetime": "2020-14-28T16:02:08Z",
      "department": "Hsbc Bank",
      "id": 6,
      "job": "Mainframe Developer Sr."
  }
]
```
example response return:
```bash
{
  "error cases: ": "(
    {
      'name': 'johny Ball', 
      'datetime': '2018-12-28T16:02:08Z', 
      'department': 'fire station', 
      'id': 6, 'job': 'Sr fireman', 
      'Error': 'ID: 6 already exists, cannot be duplicated.'}, 
    {
      'name': 'Belinda Machintons', 
      'datetime': '2020-11-28T16:02:08Z', 
      'department': 'hospital', 
      'id': 4, 
      'job': 'Nurse', 
      'Error': 'ID: 4 already exists, cannot be duplicated.'
    }, 
    {
      'name': 'Jhonatan Tole', 
      'datetime': '2020-14-28T16:02:08Z', 
      'department': 'Hsbc Bank', 
      'id': 6, 'job': 
      'Mainframe Developer Sr.', 
      'Error': 'ID: 6 already exists, cannot be duplicated.'
    })",
  "message": "1 new employees added and 3 invalid parameters cases were detected.",
  "success": true
}
```
## UPDATE Service: hired_employee Method: PUT
Service that update an employee information by posting a JSON with the format of the example.
```bash
A clarification, both the department and the job are always passed in text and the application search for the department 
or job, if it does not find it in the table it adds it and if it finds it it puts the id that it already had.
```
Call: <b>http://localhost:5000/hired_employees</b>
PUT call json example:
```bash
{
      "name": "Jhonatan Tole",
      "datetime": "2021-13-28T16:02:08Z",
      "department": "Hsbc Bank",
      "id": 6,
      "job": "Mainframe Developer Sr."
  }
```
example response return:
```bash
{
  "message": "hired employee updated.",
  "success": true
}
```
## DELETE Service: hired_employee Method: DELETE
Service to delete an employee, by posting a JSON with the format of the example.

Call: <b>http://localhost:5000/hired_employees</b>
DELETE call json example:
```bash
{
      "id": 6
  }
```
example response return:
```bash
{
  "message": "hired employee deleted.",
  "success": true
}
```