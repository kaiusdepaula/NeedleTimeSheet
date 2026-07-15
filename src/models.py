from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Literal


# ---------------------------------
# HTTP RESPONSE AND REQUEST CLASSES
# ---------------------------------
@dataclass
class Task:
    codTarefa: int 
    descricaoTarefa: str
    codAtividade: int


@dataclass
class Hour:
    hourEntry: str
    hourDeparture: str
    seq: Optional[int] = None
    type: Optional[str] = None
    origem: Optional[str] = None
    seqJornadaReal: Optional[int] = None


@dataclass
class Appropriation:
    data: str
    dataFormated: str
    hours: list[Hour]
    totalHours: str


@dataclass
class AppropriationsResponse:
    items: list[Appropriation]


@dataclass
class CreateAppropriation:
    hourEntry: str
    hourDeparture: str
    projectId: int
    taskId: int
    observation: str
    date: date
    hourType: Optional[Literal["Normal"]] = None
    origem: Optional[str] = None
    segmentoId: Optional[int] = None
    seqJornadaReal: Optional[int] = None

@dataclass
class CreateAppropriationRequest:
    appropriationsFirstPeriod: list[CreateAppropriation]
    appropriationsSecondPeriod: list[CreateAppropriation]
    appropriationsThirdPeriod: list[CreateAppropriation] = field(default_factory=list)
    appropriationsFourthPeriod: list[CreateAppropriation] = field(default_factory=list)

# ---------------------------------
# Compute related Classes
# ---------------------------------
@dataclass
class Project:
    id: int
    name: str


@dataclass
class Period:
    start: datetime
    end: datetime

    @property
    def minutes(self):
        return int((self.end - self.start).total_seconds() // 60)


@dataclass
class Allocation:
    project: Project
    minutes: int


@dataclass
class Interval:
    project: Project
    start: datetime
    end: datetime
    taskid: int
    period_index: int