from pydantic import BaseModel, ConfigDict, Field

from app.types.enums import ProcessMethod


class BeanBase(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    origin: str = Field(min_length=2, max_length=100)
    process_method: ProcessMethod
    flavor_tags: list[str] = Field(min_length=1, max_length=12)
    description: str = Field(min_length=10, max_length=1000)


class BeanCreate(BeanBase):
    model_config = ConfigDict(extra="forbid")


class BeanUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    origin: str | None = Field(default=None, min_length=2, max_length=100)
    process_method: ProcessMethod | None = None
    flavor_tags: list[str] | None = Field(default=None, min_length=1, max_length=12)
    description: str | None = Field(default=None, min_length=10, max_length=1000)


class BeanOut(BeanBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
