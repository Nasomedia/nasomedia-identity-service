from typing import Optional
from pydantic import BaseModel

# Shared properties
class ConsumerBase(BaseModel):
    cash: Optional[int] = 0

# Properties to receive on creation
class ConsumerCreate(ConsumerBase):
    pass

# Properties to receive on update
class ConsumerUpdate(ConsumerBase):
    pass

# Properties shared by models stored in DB
class ConsumerInDBBase(ConsumerBase):
    id: int
    
    cash: int

    class Config:
        orm_mode = True

# Properties to return to client
class Consumer(ConsumerInDBBase):
    pass

# Properties properties stored in DB
class ConsumerInDB(ConsumerInDBBase):
    pass