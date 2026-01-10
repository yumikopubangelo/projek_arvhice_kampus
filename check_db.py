#!/usr/bin/env python3

import sys
import os
sys.path.append('backend')

from app.database import engine
from sqlalchemy import text

def check_projects():
    with engine.connect() as conn:
        result = conn.execute(text('SELECT id, title, pdf_file_path, supplementary_files FROM projects LIMIT 10'))
        print("Projects in database:")
        for row in result:
            print(f"ID: {row[0]}, Title: {row[1]}, PDF: {row[2]}, Supp: {row[3]}")

if __name__ == "__main__":
    check_projects()
