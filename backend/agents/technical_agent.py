from backend.technical.technical_agent import run_technical_agent as core_run


def run_technical_agent(nlp_output: dict) -> dict:
    """
    Wrapper agent.
    Responsible ONLY for:
    - Receiving orchestrator input
    - Calling core technical engine
    - Returning output
    """

    print("\n===== TECHNICAL AGENT START =====")
    print("INPUT:", nlp_output)

    if not isinstance(nlp_output, dict):
        raise ValueError("Invalid NLP output format")

    # -------- CALL CORE ENGINE --------
    result = core_run(nlp_output)

    print("OUTPUT:", result)
    print("===== TECHNICAL AGENT END =====\n")

    return result