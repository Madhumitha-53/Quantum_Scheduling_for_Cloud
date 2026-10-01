from pydantic import BaseModel

class TaskSchema(BaseModel):
    cpu: int
    memory: int
    sla: int