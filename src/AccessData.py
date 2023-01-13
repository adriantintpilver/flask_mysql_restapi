sql_querys = {
    # list_hired_employees query
    'sql_list_hired_employees' : "SELECT id, name, datetime, department_id, job_id FROM hired_employees ORDER BY id ASC",
    # list sql_departments query
    'sql_departments' : "SELECT id, department FROM departments ORDER BY id ASC",
    # list one sql_departments query
    'sql_one_departments' : """SELECT id, department FROM departments WHERE department = '{0}'""",
    # list sql_jobs query
    'sql_jobs' : "SELECT id, job FROM jobs ORDER BY id ASC",
    # list one sql_jobs query
    'sql_one_jobs' : """SELECT id, job FROM jobs WHERE job = '{0}'""",
    # list one sql_backup_list query
    'sql_backup_list' : """SELECT HE.id, HE.name, HE.datetime, HE.department_id, HE.job_id, D.department, J.job  FROM globantdatastudy.hired_employees as HE inner join globantdatastudy.departments as D on D.id = HE.department_id inner join globantdatastudy.jobs as J on J.id = HE.job_id ORDER BY id ASC""",
    # insert new department query
    'sql_insert_departments' : """INSERT INTO departments (department) VALUES ('{0}')""",
    # insert new job query
    'sql_insert_jobs' : """INSERT INTO jobs (job) VALUES ('{0}')""",
    # insert new hired employees query
    'sql_insert_hired_employees' : """INSERT INTO hired_employees (id, name, datetime, department_id, job_id) VALUES ('{0}', '{1}', '{2}', {3}, {4})""",
    # delete hired employees query
    'sql_delete_hired_employees' : """DELETE FROM hired_employees WHERE id = {0}""",
    # update hired employees query
    'sql_update_hired_employees' : """UPDATE hired_employees SET name = '{0}', datetime = '{1}' , department_id = {2} , job_id = {3} WHERE id = {4}"""
}