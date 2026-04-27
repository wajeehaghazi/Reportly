from state.state import State


def synthesizer(state: State):
    """Combine all sections into final report"""

    completed_sections = state["completed_sections"]

    completed_report_sections = "\n\n---\n\n".join(completed_sections)

    return {"final_report": completed_report_sections}

