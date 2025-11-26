from config.database import get_db_connection

def init_database():
    """Инициализация базы данных и создание таблиц"""
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        
        # Создание таблицы clients
        cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id SERIAL PRIMARY KEY,
            full_name VARCHAR(255) NOT NULL,
            phone VARCHAR(50) NOT NULL,
            email VARCHAR(255) NOT NULL,
            registration_date DATE NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Создание индексов для ускорения поиска
        cur.execute("CREATE INDEX IF NOT EXISTS idx_clients_full_name ON clients(full_name)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_clients_phone ON clients(phone)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_clients_email ON clients(email)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_clients_registration_date ON clients(registration_date)")
        
        # Создание триггера для обновления updated_at
        cur.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        """)
        
        cur.execute("""
        DROP TRIGGER IF EXISTS update_clients_updated_at ON clients;
        CREATE TRIGGER update_clients_updated_at
        BEFORE UPDATE ON clients
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """)
        
        conn.commit()
        print("База данных успешно инициализирована")
        
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при инициализации базы данных: {e}")
        raise
        
    finally:
        cur.close()
        conn.close()
