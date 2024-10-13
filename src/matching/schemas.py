from pydantic import BaseModel


class MatchingSchema(BaseModel):
    candidate: dict
    job: dict