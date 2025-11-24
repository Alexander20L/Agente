"""
Sistema de base de datos unificado
Soporta SQLite (desarrollo local) y PostgreSQL (producción)
"""

import os
import sqlite3
from datetime import datetime
import bcrypt

# Detectar si estamos en producción o desarrollo
USE_POSTGRES = os.getenv('DATABASE_URL') is not None

if USE_POSTGRES:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    DATABASE_URL = os.getenv('DATABASE_URL')
else:
    DATABASE_URL = 'users.db'


class Database:
    """Clase unificada para manejar SQLite y PostgreSQL"""
    
    def __init__(self):
        self.use_postgres = USE_POSTGRES
        self.connection = None
    
    def connect(self):
        """Establece conexión con la base de datos"""
        if self.use_postgres:
            self.connection = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        else:
            self.connection = sqlite3.connect(DATABASE_URL)
            self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def close(self):
        """Cierra la conexión"""
        if self.connection:
            self.connection.close()
    
    def execute(self, query, params=None):
        """Ejecuta una query y retorna el cursor"""
        conn = self.connect()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        return cursor, conn
    
    def init_database(self):
        """Inicializa las tablas necesarias"""
        if self.use_postgres:
            create_table_query = '''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(100) NOT NULL,
                    name VARCHAR(200) NOT NULL,
                    email VARCHAR(200) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            '''
        else:
            create_table_query = '''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            '''
        
        cursor, conn = self.execute(create_table_query)
        cursor.close()
        conn.commit()
        
        # Crear usuario admin si no existe
        self._create_default_admin(conn)
        
        conn.commit()
        self.close()
    
    def _create_default_admin(self, conn):
        """Crea el usuario admin por defecto si no existe"""
        cursor = conn.cursor()
        
        # Verificar si existe admin
        if self.use_postgres:
            cursor.execute('SELECT username FROM users WHERE username = %s', ('admin',))
        else:
            cursor.execute('SELECT username FROM users WHERE username = ?', ('admin',))
        
        if not cursor.fetchone():
            hashed_password = bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt()).decode()
            
            if self.use_postgres:
                cursor.execute('''
                    INSERT INTO users (username, password, name, email)
                    VALUES (%s, %s, %s, %s)
                ''', ('admin', hashed_password, 'Administrador', 'admin@example.com'))
            else:
                cursor.execute('''
                    INSERT INTO users (username, password, name, email)
                    VALUES (?, ?, ?, ?)
                ''', ('admin', hashed_password, 'Administrador', 'admin@example.com'))
            
            conn.commit()
        
        cursor.close()
    
    def get_user(self, username):
        """Obtiene un usuario por username"""
        if self.use_postgres:
            query = 'SELECT username, password, name, email FROM users WHERE username = %s'
        else:
            query = 'SELECT username, password, name, email FROM users WHERE username = ?'
        
        cursor, conn = self.execute(query, (username,))
        user = cursor.fetchone()
        
        cursor.close()
        self.close()
        
        if user:
            return dict(user)
        return None
    
    def create_user(self, username, password, name, email):
        """Crea un nuevo usuario"""
        try:
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            
            if self.use_postgres:
                query = '''
                    INSERT INTO users (username, password, name, email)
                    VALUES (%s, %s, %s, %s)
                '''
            else:
                query = '''
                    INSERT INTO users (username, password, name, email)
                    VALUES (?, ?, ?, ?)
                '''
            
            cursor, conn = self.execute(query, (username, hashed_password, name, email))
            conn.commit()
            
            cursor.close()
            self.close()
            
            return True
        except (sqlite3.IntegrityError if not self.use_postgres else psycopg2.IntegrityError):
            self.close()
            return False  # Usuario ya existe
    
    def get_all_users(self):
        """Obtiene todos los usuarios (para administración)"""
        query = 'SELECT id, username, name, email, created_at FROM users ORDER BY created_at DESC'
        
        cursor, conn = self.execute(query)
        users = cursor.fetchall()
        
        cursor.close()
        self.close()
        
        return [dict(user) for user in users]
    
    def verify_password(self, username, password):
        """Verifica si la contraseña es correcta"""
        user = self.get_user(username)
        
        if user:
            stored_password = user['password']
            return bcrypt.checkpw(password.encode(), stored_password.encode())
        
        return False


# Instancia global
db = Database()


# Funciones de compatibilidad con el código existente
def init_database():
    """Inicializa la base de datos"""
    db.init_database()


def get_user(username):
    """Obtiene un usuario"""
    return db.get_user(username)


def create_user(username, password, name, email):
    """Crea un nuevo usuario"""
    return db.create_user(username, password, name, email)


def verify_password(username, password):
    """Verifica la contraseña de un usuario"""
    return db.verify_password(username, password)
