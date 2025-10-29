import pymysql
import serial
import serial.tools.list_ports
import datetime

DB_CONFIG = dict(
    host = 'localhost',
    user = 'root',
    password = 'js990129',
    db = 'env_monitoring',
    charset = 'utf8'
)

class DB:
    def __init__(self, **config):
        self.config = config
        print("DB 연결됨:", config)

        self.ser = None

        try:
            ports = serial.tools.list_ports.comports()
            for port in ports:
                if "Arduino" in port.description :
                    self.ser = serial.Serial(port.device, 9600, timeout=1) 
                    print(f"{port.device}에 연결되었습니다.")
                    break
        except Exception as e:
            self.ser = None
            print(f"포트 열기 실패: {e}")

    def connect(self):
        return pymysql.connect(**self.config)
    
    def verify_user(self, username, password):
        sql = "SELECT COUNT(*) FROM users WHERE username=%s AND password=%s"
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (username, password))
                count, = cur.fetchone()
                return count == 1
            
    def insert_user(self, username, password):
        sql1 = 'SELECT COUNT(*) FROM users WHERE username = %s OR password = %s'
        sql2 = 'INSERT INTO users (username, password) VALUES (%s, %s)'
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql1, (username, password))
                count, = cur.fetchone()
                if count == 1:
                    return count == 1
                else:
                    cur.execute(sql2, (username, password))
                    conn.commit()
                    return count == 1
    
    def save_sensor_data(self, temperature, humidity, water_level, soil_moisture):
        sql = 'INSERT INTO sensor_data (temperature, humidity, water_level, soil_moisture, created_time)VALUES (%s, %s, %s, %s, %s)'
        current_time = datetime.datetime.now()
        try:
            with self.connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (temperature, humidity, water_level, soil_moisture, current_time))
                conn.commit()
            print(f"데이터 저장 성공: {temperature}°C, {humidity}%, {soil_moisture}%, {water_level}mm")
            return True
        except Exception as e:
            print(f"데이터 저장 실패: {e}")
            return False
    
    

    def fetch_data(self):
        sql = 'SELECT temperature, humidity, water_level, soil_moisture, created_time FROM sensor_data ORDER BY id DESC'
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                return cur.fetchall()

    def fetch_date_data(self, sel_date):
        sql = 'SELECT temperature, humidity, water_level, soil_moisture, created_time FROM sensor_data WHERE DATE(created_time) = %s ORDER BY created_time'
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, sel_date)
                return cur.fetchall()