from state.state import State


def synthesizer(state: State):
    """Combine all sections into final report"""
    try:
        completed_sections = state["completed_sections"]
        completed_report_sections = "\n\n---\n\n".join(completed_sections)
        return {"final_report": completed_report_sections}
    except Exception as e:
        print(f"Error in synthesizer: {e}")
        return {"final_report": ""}
