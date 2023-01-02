# Validates the code (if it is numeric and of length < 8).
def validate_id(id: str) -> bool:
    return (str(id).isnumeric() and len(str(id)) <= 8)

# Validates the name (if it is a text without whitespace between 1 and 100 characters).
def validate_name(name: str) -> bool:
    name = name.strip()
    return (len(name) > 0 and len(name) <= 100)

# Validates the datetime (if it is equal to 20 characters).
def validate_datetime(datetime: str) -> bool:
    datetime = datetime.strip()
    return (len(datetime) > 0 and len(datetime) == 20)

# Validate that the job_id is numeric and are between 1 and 4.
def validate_job_id(job_id: str) -> bool:
    return (str(job_id).isnumeric() and len(str(job_id)) <= 4)

# Validates the job (if it is a text without whitespace between 1 and 100 characters).
def validate_job(job: str) -> bool:
    job = job.strip()
    return (len(job) > 0 and len(job) <= 100)

# Validate that the department_id is numeric and are between 1 and 4.
def validate_department_id(department_id: str) -> bool:
    return (str(department_id).isnumeric() and len(str(department_id)) <= 4)

# Validates the department (if it is a text without whitespace between 1 and 100 characters).
def validate_department(department: str) -> bool:
    department = department.strip()
    return (len(department) > 0 and len(department) <= 100)

   
