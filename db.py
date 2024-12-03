import pyodbc

# ตั้งค่าการเชื่อมต่อฐานข้อมูล
server = 'ACER\\SQLEXPRESS'
database = 'runsheet'
driver = '{ODBC Driver 17 for SQL Server}'

# ฟังก์ชันสำหรับเชื่อมต่อฐานข้อมูล
def db_connection():
    conn_str = (
        "DRIVER=" + driver + ";"
        "SERVER=" + server + ";"
        "DATABASE=" + database + ";"
        "Trusted_Connection=yes;"
    )
    return pyodbc.connect(conn_str)