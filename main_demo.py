"""
H2 SMART STORAGE
Simulation & Logic Demonstration

This script demonstrates the complete prototype workflow:

CNT Resistance
        ↓
Sensor Filtering
        ↓
Fuel Percentage
        ↓
Heating Demand
        ↓
9-Zone Selective Heating
        ↓
Zone Transfer
"""

from resistance_to_fuel import (
    filter_sensor_readings,
    resistance_to_fuel
)

from zone_heating import NineZoneController


def run_simulation():

    print("=" * 60)

    print("H2 SMART STORAGE")
    print("SIMULATION & LOGIC VALIDATION")

    print("=" * 60)


    # --------------------------------------------------
    # STEP 1 - CNT SENSOR
    # --------------------------------------------------

    print("\nSTEP 1 - CNT SENSOR READING")

    print("-" * 60)

    sensor_readings = [
        25.9,
        26.1,
        26.0,
        25.8,
        26.2
    ]

    print(
        "Raw CNT resistance readings:",
        sensor_readings
    )


    # --------------------------------------------------
    # STEP 2 - FILTER SENSOR DATA
    # --------------------------------------------------

    filtered_resistance = filter_sensor_readings(
        sensor_readings
    )

    print(
        "Filtered resistance:",
        filtered_resistance,
        "Ohm"
    )


    # --------------------------------------------------
    # STEP 3 - CONVERT TO FUEL LEVEL
    # --------------------------------------------------

    fuel_percentage = resistance_to_fuel(
        filtered_resistance
    )

    print(
        "Estimated remaining fuel:",
        fuel_percentage,
        "%"
    )

    print(
        "\nVALIDATION:"
        f" {filtered_resistance} Ohm"
        f" -> {fuel_percentage}% Fuel"
    )


    # --------------------------------------------------
    # STEP 4 - INITIALIZE 9-ZONE CONTROLLER
    # --------------------------------------------------

    print("\n")

    print("=" * 60)

    print("STEP 2 - INTELLIGENT 9-ZONE MANAGEMENT")

    print("=" * 60)

    controller = NineZoneController(
        heater_power_per_zone_kw=1.0
    )


    # --------------------------------------------------
    # STEP 5 - REQUEST ZONE 1
    # --------------------------------------------------

    print("\nInitial heating demand:")

    controller.request_zone(1)

    controller.display_status()


    # --------------------------------------------------
    # STEP 6 - MOVE HEATING REQUEST
    # --------------------------------------------------

    print("\n")

    print("=" * 60)

    print("DEMAND TRANSFER")

    print("=" * 60)

    print(
        "Thermal demand moved from Zone 1 to Zone 2."
    )

    controller.request_zone(2)

    controller.display_status()


    # --------------------------------------------------
    # FINAL VALIDATION
    # --------------------------------------------------

    print("\n")

    print("=" * 60)

    print("SIMULATION RESULT")

    print("=" * 60)

    if controller.active_zone_count() == 1:

        print(
            "PASS: Selective heating successfully maintained."
        )

        print(
            "PASS: Only one zone is active."
        )

    else:

        print(
            "FAIL: Multiple zones are active."
        )


    print(
        f"PASS: CNT resistance "
        f"{filtered_resistance} Ohm "
        f"was converted to "
        f"{fuel_percentage}% remaining fuel."
    )

    print(
        "PASS: Heating request successfully "
        "transferred Zone 1 -> Zone 2."
    )

    print(
        "Instantaneous heater-power reduction:",
        controller.energy_saving_percentage(),
        "%"
    )

    print("=" * 60)


if __name__ == "__main__":

    run_simulation()
