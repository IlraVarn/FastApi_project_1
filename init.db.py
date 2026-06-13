from sqlmodel import SQLModel

import models
from db import engine


SQLModel.metadata.create_all(engine)

