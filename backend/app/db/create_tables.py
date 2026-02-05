from backend.app.db.schema import Base
from backend.app.db.session import engine

def main():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Done.")

if __name__ == "__main__":
    main()
