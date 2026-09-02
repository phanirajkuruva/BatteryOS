def calculate_health_score(
    voltage: float,
    temperature: float,
    cycle_count: int,
) -> tuple[float, str]:
    """
    Calculate battery health score and health status.

    Returns:
        (health_score, health_status)
    """

    score = 100.0

    # Voltage penalty
    if voltage < 350:
        score -= 30
    elif voltage < 370:
        score -= 20
    elif voltage < 390:
        score -= 10

    # Temperature penalty
    if temperature > 50:
        score -= 30
    elif temperature > 45:
        score -= 20
    elif temperature > 40:
        score -= 10

    # Cycle count penalty
    if cycle_count > 2000:
        score -= 30
    elif cycle_count > 1500:
        score -= 20
    elif cycle_count > 1000:
        score -= 10

    score = max(score, 0)

    # Health status
    if score >= 90:
        status = "Excellent"
    elif score >= 75:
        status = "Good"
    elif score >= 60:
        status = "Warning"
    else:
        status = "Critical"

    return score, status