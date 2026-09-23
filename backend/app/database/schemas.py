from datetime import datetime
from pydantic import BaseModel, Field

class LocationOut(BaseModel):
    id: str
    name: str
    state: str
    latitude: float
    longitude: float
    riskLevel: str
    probability: float
    rainfall: float
    slope: float
    elevation: float
    landCover: str
    geology: str
    historicalLandslides: int
    trend: str
    modelSource: str = "demo"

class SimulationIn(BaseModel):
    locationId: str
    rainfall: float = Field(ge=0, le=1000)

class PredictionOut(BaseModel):
    probability: float
    riskLevel: str
    modelSource: str
    factors: list[str] = []
    simulated: bool = False
    features: dict[str, float] = {}

class LoginIn(BaseModel):
    name: str = "User"
    email: str

class UserOut(BaseModel):
    name: str
    email: str
    authenticated: bool = True
