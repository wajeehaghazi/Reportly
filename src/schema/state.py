from typing import Annotated, List, TypedDict
import operator

from pydantic import BaseModel, Field


# -----------------------------------------
# Section Schema
# -----------------------------------------

class Section(BaseModel):

    name: str = Field(
        description="Name for this section of the report"
    )

    description: str = Field(
        description="Short description of the section"
    )


class Sections(BaseModel):

    sections: List[Section]


# -----------------------------------------
# Main Graph State
# -----------------------------------------

class State(TypedDict):

    topic: str

    sections: List[Section]

    completed_sections: Annotated[
        list,
        operator.add
    ]

    final_report: str


# -----------------------------------------
# Worker State
# -----------------------------------------

class WorkerState(TypedDict):

    section: Section

    completed_sections: Annotated[
        list,
        operator.add
    ]