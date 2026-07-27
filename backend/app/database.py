# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base


class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.session_factory = None
        self._scoped_session = None

    def init_app(self, app):
        """Initializes raw SQLAlchemy and binds to Flask application lifecycle."""
        db_uri = app.config.get("DATABASE_URI")

        # 1. Create a raw SQLAlchemy engine with an optimized connection pool
        self.engine = create_engine(
            db_uri,
            pool_size=10,
            max_overflow=20,
            pool_recycle=3600,
            executemany_mode="values",
            executemany_batch_page_size=1000,
        )
        self.session_factory = sessionmaker(bind=self.engine)

        # 2. Force thread-safety utilizing a scoped session proxy
        self._scoped_session = scoped_session(self.session_factory)

        # 3. Clean up the connection at the end of every request (Crucial!)
        @app.teardown_appcontext
        def shutdown_session(exception=None):
            if self._scoped_session:
                # Returns connection back to the pool, preventing leaks
                self._scoped_session.remove()

    @property
    def session(self) -> scoped_session:
        if self._scoped_session is None:
            raise RuntimeError(
                "DatabaseManager not initialized. Call init_app() first."
            )
        return self._scoped_session


Base = declarative_base()
db_manager = DatabaseManager()
