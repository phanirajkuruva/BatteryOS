def calculate_health_score(
    voltage: float,
    temperature: float,
    cycle_count: int,
) -> float:
    """
    Calculate battery health score (0-100).

    The score starts at 100 and penalties are applied based on:
    - Voltage
    - Temperature
    - Charge cycle count
    """

    score = 100.0

    # Voltage penalty
    if voltage < 350:
        score -= 20
    elif voltage < 370:
        score -= 10

    # Temperature penalty
    if temperature > 50:
        score -= 25
    elif temperature > 45:
        score -= 15
    elif temperature > 40:
        score -= 5

    # Cycle count penalty
    if cycle_count > 2500:
        score -= 25
    elif cycle_count > 2000:
        score -= 15
    elif cycle_count > 1500:
        score -= 10
    elif cycle_count > 1000:
        score -= 5

    # Keep score between 0 and 100
    return max(0, min(round(score, 2), 100))


def calculate_health_status(
    health_score: float,
) -> str:
    """
    Convert health score into a readable battery health status.
    """

    if health_score >= 90:
        return "Excellent"

    if health_score >= 80:
        return "Good"

    if health_score >= 70:
        return "Warning"

    if health_score >= 50:
        return "Poor"

    return "Critical"