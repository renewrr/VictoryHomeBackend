from app.database import db_manager
from app.models import model_views, models_generated as models
from app import schemas
from typing import Tuple, Sequence
import datetime


from sqlalchemy import select, insert, delete, Integer, or_
from sqlalchemy.orm import with_loader_criteria, selectinload, noload


class WebhookRepository:
    pass

    @staticmethod
    def post_webhook_message(response_id, timestamp, answers):
        print(response_id, timestamp, answers)
        pass
