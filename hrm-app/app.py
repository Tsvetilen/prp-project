from flask import Flask, render_template, request, redirect, url_for
import pyodbc
import os

app = Flask(__name__)

def get_db_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=" + os.getenv("DB_HOST", "fonteynholiday.database.windows.net") + ";"
        "DATABASE=" + os.getenv("DB_NAME", "hrm") + ";"
        "UID=" + os.getenv("DB_USER", "FonteynDB") + ";"
        "PWD=" + os.getenv("DB_PASSWORD", "Fonteyn123") + ";"
        "Encrypt=yes;TrustServerCertificate=no;"
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/employees', methods=['GET', 'POST'])
def add_employee():
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        position_ID = request.form['position_ID']
        department_ID = request.form['department_ID']
        cursor.execute(
            'INSERT INTO employees (first_name, last_name, email, position_ID, department_ID) VALUES (?, ?, ?, ?, ?)',
            (first_name, last_name, email, position_ID, department_ID)
        )
        conn.commit()
    cursor.execute('SELECT id, title FROM positions')
    positions = cursor.fetchall()
    cursor.execute('SELECT id, name FROM departments')
    departments = cursor.fetchall()
    cursor.execute('''
        SELECT e.id, e.first_name, e.last_name, e.email, p.title, d.name
        FROM employees e
        INNER JOIN positions p ON e.position_ID = p.id
        INNER JOIN departments d ON e.department_ID = d.id
    ''')
    employees = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('employees.html', positions=positions, departments=departments, employees=employees)

@app.route('/positions', methods=['GET', 'POST'])
def add_position():
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        title = request.form['title']
        cursor.execute('INSERT INTO positions (title) VALUES (?)', (title,))
        conn.commit()
    cursor.execute('SELECT id, title FROM positions')
    positions = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('positions.html', positions=positions)

@app.route('/departments', methods=['GET', 'POST'])
def add_department():
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        cursor.execute('INSERT INTO departments (name) VALUES (?)', (name,))
        conn.commit()
    cursor.execute('SELECT id, name FROM departments')
    departments = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('departments.html', departments=departments)

@app.route('/payroll', methods=['GET', 'POST'])
def add_payroll():
    conn = get_db_connection()
    cursor = conn.cursor()
    error_message = None
    if request.method == 'POST':
        employee_id = request.form['employee_id']
        try:
            salary = float(request.form['salary'])
            taxes = float(request.form['taxes'])
            if salary <= 0 or taxes <= 0:
                error_message = "Salary and Taxes must be positive values."
            else:
                cursor.execute('INSERT INTO payroll (employee_id, salary, taxes) VALUES (?, ?, ?)', (employee_id, salary, taxes))
                conn.commit()
        except ValueError:
            error_message = "Salary and Taxes must be valid value."
    cursor.execute('SELECT id, first_name, last_name FROM employees')
    employees = cursor.fetchall()
    cursor.execute('SELECT id, employee_id, salary, taxes FROM payroll')
    payrolls = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('payroll.html', employees=employees, payrolls=payrolls, error=error_message)

@app.route('/attendance', methods=['GET', 'POST'])
def add_attendance():
    conn = get_db_connection()
    cursor = conn.cursor()
    error_message = None
    if request.method == 'POST':
        employee_id = int(request.form['employee_id'])
        days_present = int(request.form['days_present'])
        days_absent = int(request.form['days_absent'])
        if sum([days_absent, days_present]) > 24:
            error_message = "Cannot exceed 24 working days"
        else:
            cursor.execute(
                'INSERT INTO attendance (employee_id, days_present, days_absent) VALUES (?, ?, ?)',
                (employee_id, days_present, days_absent)
            )
            conn.commit()
    cursor.execute('SELECT id, first_name, last_name FROM employees')
    employees = cursor.fetchall()
    cursor.execute('SELECT id, employee_id, days_present, days_absent FROM attendance')
    attendances = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('attendance.html', employees=employees, attendances=attendances, error=error_message)

@app.route('/departments/delete/<int:dept_id>', methods=['POST'])
def delete_department(dept_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM departments WHERE id = ?', (dept_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('add_department'))

@app.route('/positions/delete/<int:pos_id>', methods=['POST'])
def delete_position(pos_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM positions WHERE id = ?', (pos_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('add_position'))

@app.route('/employees/delete/<int:emp_id>', methods=['POST'])
def delete_employee(emp_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM employees WHERE id = ?', (emp_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('add_employee'))

@app.route('/payroll/delete/<int:payroll_id>', methods=['POST'])
def delete_payroll(payroll_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM payroll WHERE id = ?', (payroll_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('add_payroll'))

@app.route('/attendance/delete/<int:attendance_id>', methods=['POST'])
def delete_attendance(attendance_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM attendance WHERE id = ?', (attendance_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('add_attendance'))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)