import sqlite3

# Connect to the database
conn = sqlite3.connect('backend/campus_archive.db')
cursor = conn.cursor()

# Check users table
cursor.execute("SELECT id, email, hashed_password FROM users")
users = cursor.fetchall()

print("Users in database:")
for user in users:
    print(f"ID: {user[0]}, Email: {user[1]}, Hash: {user[2][:50]}...")

# Check projects table
cursor.execute("SELECT id, title, uploaded_by FROM projects")
projects = cursor.fetchall()

print("\nProjects in database:")
for project in projects:
    print(f"ID: {project[0]}, Title: {project[1]}, Uploaded by: {project[2]}")

conn.close()
