import sqlite3
from faker import Faker
import json
import random

fake = Faker()

conn = sqlite3.connect('change_requests.db')

c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS change_requests
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_name TEXT,
              change_number TEXT,
              requested_by TEXT,
              date_of_request DATE,
              presented_to TEXT,
              change_name TEXT,
              description TEXT,
              reason TEXT,
              cost_items TEXT,
              category TEXT,
              timestamp DATETIME)''')

categories = ["hardware", "software", "personnel", "other"]

for _ in range(50):
    project_name = fake.company() 
    change_number = "CR-" + str(fake.random_number(digits=3))
    requested_by = fake.name()  
    date_of_request = fake.date_this_year().strftime("%Y-%m-%d")
    presented_to = fake.name() 
    change_name = fake.catch_phrase()  
    description = fake.paragraph()  
    reason = fake.sentence() 
    cost_items = json.dumps([
        {"item": fake.word(), "cost": fake.random_number(digits=3)}
        for _ in range(random.randint(1, 5))
    ])
    category = random.choice(categories)  
    timestamp = fake.date_time_this_year().strftime("%Y-%m-%d %H:%M:%S")

    c.execute("""
        INSERT INTO change_requests (
            project_name, change_number, requested_by, date_of_request, presented_to,
            change_name, description, reason, cost_items, category, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (project_name, change_number, requested_by, date_of_request, presented_to,
          change_name, description, reason, cost_items, category, timestamp))

conn.commit()
conn.close()