"""
Test script for database models

This script tests all database models to ensure they work correctly.
Run this AFTER applying migrations.

Usage:
    python test_models.py
"""

import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, Project, AccessRequest, PrivacyLevel, ProjectStatus, AccessRequestStatus


def test_user_model():
    """Test User model CRUD operations"""
    print("\n" + "="*60)
    print("🧪 TESTING USER MODEL")
    print("="*60)
    
    db: Session = SessionLocal()
    
    try:
        # CREATE - Student
        print("\n1️⃣ Creating student user...")
        student = User(
            email="student@test.com",
            hashed_password="hashed_password_here",
            full_name="Ahmad Rizki",
            role="student",
            student_id="12345678",
            is_active=True,
            is_verified=False
        )
        db.add(student)
        db.commit()
        db.refresh(student)
        print(f"   ✅ Student created: {student}")
        
        # CREATE - Dosen
        print("\n2️⃣ Creating dosen user...")
        dosen = User(
            email="dosen@test.com",
            hashed_password="hashed_password_here",
            full_name="Dr. Budi Santoso",
            role="dosen",
            department="Computer Science",
            title="Dr.",
            is_active=True,
            is_verified=True
        )
        db.add(dosen)
        db.commit()
        db.refresh(dosen)
        print(f"   ✅ Dosen created: {dosen}")
        
        # READ
        print("\n3️⃣ Reading users...")
        users = db.query(User).all()
        print(f"   ✅ Found {len(users)} users")
        for user in users:
            print(f"      - {user.full_name} ({user.email}) - {user.role}")
        
        # UPDATE
        print("\n4️⃣ Updating student...")
        student.phone = "+62812345678"
        student.updated_at = datetime.utcnow()
        db.commit()
        print(f"   ✅ Student updated: phone = {student.phone}")
        
        # TEST PROPERTIES
        print("\n5️⃣ Testing user properties...")
        print(f"   - student.is_student: {student.is_student}")
        print(f"   - student.is_dosen: {student.is_dosen}")
        print(f"   - dosen.is_student: {dosen.is_student}")
        print(f"   - dosen.is_dosen: {dosen.is_dosen}")
        
        return student.id, dosen.id
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def test_project_model(student_id: int, dosen_id: int):
    """Test Project model CRUD operations"""
    print("\n" + "="*60)
    print("🧪 TESTING PROJECT MODEL")
    print("="*60)
    
    db: Session = SessionLocal()
    
    try:
        # CREATE - Private Project
        print("\n1️⃣ Creating private project...")
        project1 = Project(
            title="Sentiment Analysis using BERT",
            abstract="This research implements BERT model for sentiment analysis on Indonesian social media data. We collected 10,000 tweets and achieved 87% accuracy.",
            abstract_preview="This research implements BERT model for sentiment analysis...",
            authors=["Ahmad Rizki", "Siti Nurhaliza"],
            tags=["ML", "NLP", "BERT", "sentiment-analysis"],
            year=2024,
            semester="Ganjil",
            class_name="Machine Learning A",
            course_code="CS601",
            status=ProjectStatus.COMPLETED,
            privacy_level=PrivacyLevel.PRIVATE,
            pdf_file_path="/uploads/projects/1/report.pdf",
            pdf_file_size=2048000,
            code_repo_url="https://github.com/ahmad/sentiment-bert",
            uploaded_by=student_id,
            advisor_id=dosen_id,
            view_count=0,
            download_count=0
        )
        db.add(project1)
        db.commit()
        db.refresh(project1)
        print(f"   ✅ Project created: {project1}")
        
        # CREATE - Public Project
        print("\n2️⃣ Creating public project...")
        project2 = Project(
            title="Object Detection for Autonomous Vehicles",
            abstract="Real-time object detection system using YOLOv8.",
            abstract_preview="Real-time object detection system...",
            authors=["Ahmad Rizki"],
            tags=["Computer Vision", "Deep Learning", "YOLO"],
            year=2024,
            semester="Genap",
            status=ProjectStatus.ONGOING,
            privacy_level=PrivacyLevel.PUBLIC,
            uploaded_by=student_id,
            advisor_id=dosen_id
        )
        db.add(project2)
        db.commit()
        db.refresh(project2)
        print(f"   ✅ Project created: {project2}")
        
        # READ
        print("\n3️⃣ Reading projects...")
        projects = db.query(Project).all()
        print(f"   ✅ Found {len(projects)} projects")
        for proj in projects:
            print(f"      - {proj.title[:50]} ({proj.year}) - {proj.privacy_level.value}")
        
        # UPDATE
        print("\n4️⃣ Updating project...")
        project1.view_count += 1
        project1.updated_at = datetime.utcnow()
        db.commit()
        print(f"   ✅ Project view count: {project1.view_count}")
        
        # TEST PROPERTIES
        print("\n5️⃣ Testing project properties...")
        print(f"   - project1.is_public: {project1.is_public}")
        print(f"   - project1.has_file: {project1.has_file}")
        print(f"   - project2.is_public: {project2.is_public}")
        print(f"   - project2.has_file: {project2.has_file}")
        
        # TEST ACCESS CONTROL
        print("\n6️⃣ Testing access control...")
        # Owner can access
        print(f"   - Student can access project1: {project1.can_access(student_id, 'student')}")
        # Public project is accessible to dosen
        print(f"   - Dosen can access project2: {project2.can_access(dosen_id, 'dosen')}")
        # Private project not accessible to dosen (without approval)
        print(f"   - Dosen can access project1 (private): {project1.can_access(dosen_id, 'dosen')}")
        
        # TEST RELATIONSHIPS
        print("\n7️⃣ Testing relationships...")
        print(f"   - project1.uploader.full_name: {project1.uploader.full_name}")
        print(f"   - project1.advisor.full_name: {project1.advisor.full_name}")
        
        return project1.id, project2.id
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def test_access_request_model(project_id: int, dosen_id: int):
    """Test AccessRequest model CRUD operations"""
    print("\n" + "="*60)
    print("🧪 TESTING ACCESS REQUEST MODEL")
    print("="*60)
    
    db: Session = SessionLocal()
    
    try:
        # CREATE
        print("\n1️⃣ Creating access request...")
        access_req = AccessRequest(
            project_id=project_id,
            requester_id=dosen_id,
            status=AccessRequestStatus.PENDING,
            message="I would like to review this project for research purposes.",
        )
        db.add(access_req)
        db.commit()
        db.refresh(access_req)
        print(f"   ✅ Access request created: {access_req}")
        
        # READ
        print("\n2️⃣ Reading access requests...")
        requests = db.query(AccessRequest).all()
        print(f"   ✅ Found {len(requests)} access requests")
        for req in requests:
            print(f"      - Request #{req.id}: {req.status.value}")
        
        # TEST PROPERTIES
        print("\n3️⃣ Testing access request properties...")
        print(f"   - is_pending: {access_req.is_pending}")
        print(f"   - is_approved: {access_req.is_approved}")
        print(f"   - is_active: {access_req.is_active}")
        
        # APPROVE REQUEST
        print("\n4️⃣ Approving access request...")
        access_req.approve(response_message="Access granted for review.")
        db.commit()
        print(f"   ✅ Request approved")
        print(f"   - Status: {access_req.status.value}")
        print(f"   - Responded at: {access_req.responded_at}")
        print(f"   - is_approved: {access_req.is_approved}")
        print(f"   - is_active: {access_req.is_active}")
        
        # TEST RELATIONSHIPS
        print("\n5️⃣ Testing relationships...")
        print(f"   - Project: {access_req.project.title[:50]}")
        print(f"   - Requester: {access_req.requester.full_name}")
        
        # TEST DENY (create new request)
        print("\n6️⃣ Testing deny functionality...")
        access_req2 = AccessRequest(
            project_id=project_id,
            requester_id=dosen_id + 100,  # Fake ID for testing
            status=AccessRequestStatus.PENDING
        )
        db.add(access_req2)
        db.commit()
        
        access_req2.deny(response_message="Request denied.")
        db.commit()
        print(f"   ✅ Request denied: {access_req2.status.value}")
        
        return access_req.id
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def cleanup_test_data():
    """Clean up test data"""
    print("\n" + "="*60)
    print("🧹 CLEANING UP TEST DATA")
    print("="*60)
    
    db: Session = SessionLocal()
    
    try:
        # Delete in order (foreign key constraints)
        print("\n1️⃣ Deleting access requests...")
        count = db.query(AccessRequest).delete()
        print(f"   ✅ Deleted {count} access requests")
        
        print("\n2️⃣ Deleting projects...")
        count = db.query(Project).delete()
        print(f"   ✅ Deleted {count} projects")
        
        print("\n3️⃣ Deleting users...")
        count = db.query(User).delete()
        print(f"   ✅ Deleted {count} users")
        
        db.commit()
        print("\n✅ Cleanup complete!")
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Main test runner"""
    print("\n" + "="*60)
    print("🚀 STARTING DATABASE MODEL TESTS")
    print("="*60)
    
    try:
        # Test User model
        student_id, dosen_id = test_user_model()
        
        # Test Project model
        project_id, _ = test_project_model(student_id, dosen_id)
        
        # Test AccessRequest model
        test_access_request_model(project_id, dosen_id)
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        
        # Ask if user wants to clean up
        response = input("\n🧹 Clean up test data? (y/N): ")
        if response.lower() == 'y':
            cleanup_test_data()
        else:
            print("\n💡 Test data kept. You can view it in the database.")
        
    except Exception as e:
        print("\n" + "="*60)
        print(f"❌ TEST FAILED: {e}")
        print("="*60)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()