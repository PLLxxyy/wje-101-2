from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.types.schemas.user_schema import UserPublic


class BrewStep(BaseModel):
    step_number: int = Field(ge=1, le=20)
    description: str = Field(min_length=2, max_length=300)
    duration_seconds: int = Field(ge=0, le=3600)


class RecipeBase(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    device: str = Field(min_length=2, max_length=50)
    water_temp: float = Field(ge=60, le=100)
    grind_size: str = Field(min_length=1, max_length=50)
    ratio: str = Field(min_length=3, max_length=20)
    steps: list[BrewStep] = Field(min_length=1, max_length=20)

    @field_validator("steps")
    @classmethod
    def validate_step_order(cls, value: list[BrewStep]) -> list[BrewStep]:
        numbers = [step.step_number for step in value]
        if len(numbers) != len(set(numbers)):
            raise ValueError("步骤序号不能重复")
        return value


class RecipeCreate(RecipeBase):
    model_config = ConfigDict(extra="forbid")


class RecipeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    device: str | None = Field(default=None, min_length=2, max_length=50)
    water_temp: float | None = Field(default=None, ge=60, le=100)
    grind_size: str | None = Field(default=None, min_length=1, max_length=50)
    ratio: str | None = Field(default=None, min_length=3, max_length=20)
    steps: list[BrewStep] | None = Field(default=None, min_length=1, max_length=20)


class RecipeOut(RecipeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    user: UserPublic | None = None
