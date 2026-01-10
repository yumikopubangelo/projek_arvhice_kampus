import alembic.config
import alembic.command
import os

def run_migrations():
    """Applies all pending Alembic migrations."""
    
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the full path to alembic.ini
    alembic_ini_path = os.path.join(script_dir, "alembic.ini")
    
    # Create an Alembic configuration object
    alembic_cfg = alembic.config.Config(alembic_ini_path)
    
    # Set the script location (assuming it's relative to the ini file)
    alembic_cfg.set_main_option("script_location", "alembic")
    
    print("🚀 Applying database migrations...")
    
    # Run the 'upgrade' command
    alembic.command.upgrade(alembic_cfg, "head")
    
    print("✅ Migrations applied successfully!")

if __name__ == "__main__":
    # Ensure the working directory is the backend directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    run_migrations()
