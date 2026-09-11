"""
CNT Resistance to Fuel Level Simulation

This module converts Carbon Nanotube (CNT) sensor resistance
into an estimated remaining fuel percentage.

NOTE:
The calibration points are prototype/simulation values.
Real hardware calibration must be obtained experimentally.
"""

from statistics import median


# ---------------------------------------------------------
# CNT SENSOR CALIBRATION CURVE
# (Resistance in Ohms, Remaining Fuel %)
# ---------------------------------------------------------

CALIBRATION_CURVE = [
    (10.0, 100.0),
    (26.0, 74.0),   # Prototype validation point
    (50.0, 38.0),
    (72.0, 0.0),
]


def clamp(value, minimum, maximum):
    """Keep a value inside the allowed range."""
    return max(minimum, min(value, maximum))


def filter_sensor_readings(readings):
    """
    Remove sensor noise using median filtering.
    """
    if not readings:
        raise ValueError("Sensor readings cannot be empty.")

    return round(median(readings), 2)


def resistance_to_fuel(resistance_ohm):
    """
    Convert CNT resistance into remaining fuel percentage
    using piecewise linear interpolation.
    """

    points = sorted(CALIBRATION_CURVE)

    # Resistance below minimum calibration point
    if resistance_ohm <= points[0][0]:
        return 100.0

    # Resistance above maximum calibration point
    if resistance_ohm >= points[-1][0]:
        return 0.0

    # Find the two calibration points surrounding the reading
    for i in range(len(points) - 1):

        r1, fuel1 = points[i]
        r2, fuel2 = points[i + 1]

        if r1 <= resistance_ohm <= r2:

            ratio = (resistance_ohm - r1) / (r2 - r1)

            fuel_percentage = fuel1 + ratio * (fuel2 - fuel1)

            return round(
                clamp(fuel_percentage, 0.0, 100.0),
                1
            )

    return 0.0


if __name__ == "__main__":

    # Example sensor measurements around 26 Ohms
    sensor_readings = [
        25.9,
        26.1,
        26.0,
        25.8,
        26.2
    ]

    filtered_resistance = filter_sensor_readings(sensor_readings)

    fuel_percentage = resistance_to_fuel(filtered_resistance)

    print("CNT SENSOR SIMULATION")
    print("---------------------")
    print("Raw readings:", sensor_readings)
    print("Filtered resistance:", filtered_resistance, "Ohm")
    print("Remaining fuel:", fuel_percentage, "%")
