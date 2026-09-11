"""
9-Zone Selective Heating Controller

The system contains 9 heating zones.

Main rule:
Only ONE zone can be actively heated at any time.

Example:
Zone 1 ON
then when demand moves:
Zone 1 OFF -> Zone 2 ON

This demonstrates selective localized heating
instead of heating the entire storage system.
"""


class NineZoneController:

    def __init__(self, heater_power_per_zone_kw=1.0):

        self.total_zones = 9

        self.heater_power_per_zone_kw = heater_power_per_zone_kw

        self.zones = {
            zone: "OFF"
            for zone in range(1, self.total_zones + 1)
        }

        self.active_zone = None


    def request_zone(self, zone_number):
        """
        Activate one requested zone.

        If another zone is already active,
        it will be turned OFF first.
        """

        if zone_number < 1 or zone_number > 9:
            raise ValueError("Zone must be between 1 and 9.")

        print(f"\nHeating request received for Zone {zone_number}")

        # Turn off current active zone
        if self.active_zone is not None:

            if self.active_zone != zone_number:

                print(
                    f"Zone {self.active_zone} -> HEATING OFF"
                )

                self.zones[self.active_zone] = "OFF"

        # Safety: force every other zone OFF
        for zone in self.zones:

            if zone != zone_number:
                self.zones[zone] = "OFF"

        # Activate requested zone
        self.zones[zone_number] = "HEATING"

        self.active_zone = zone_number

        print(
            f"Zone {zone_number} -> HEATING ON"
        )

        self.safety_check()


    def safety_check(self):
        """
        Ensure that no more than one zone
        is heating at the same time.
        """

        active_zones = [
            zone
            for zone, state in self.zones.items()
            if state == "HEATING"
        ]

        if len(active_zones) > 1:

            raise RuntimeError(
                "SAFETY ERROR: More than one heating zone is active!"
            )

        return True


    def active_zone_count(self):

        return sum(
            1
            for state in self.zones.values()
            if state == "HEATING"
        )


    def current_power(self):
        """
        Current instantaneous heater power.
        """

        return (
            self.active_zone_count()
            * self.heater_power_per_zone_kw
        )


    def full_system_power(self):
        """
        Power required if all 9 zones were heated simultaneously.
        """

        return (
            self.total_zones
            * self.heater_power_per_zone_kw
        )


    def energy_saving_percentage(self):
        """
        Relative instantaneous power reduction
        compared with heating all 9 zones.
        """

        full_power = self.full_system_power()

        current_power = self.current_power()

        saving = (
            1 - (current_power / full_power)
        ) * 100

        return round(saving, 1)


    def display_status(self):

        print("\n9-ZONE STATUS")
        print("--------------------")

        for zone, state in self.zones.items():

            print(
                f"Zone {zone}: {state}"
            )

        print("--------------------")

        print(
            "Active zones:",
            self.active_zone_count(),
            "/ 9"
        )

        print(
            "Current heater power:",
            self.current_power(),
            "kW"
        )

        print(
            "Relative power reduction:",
            self.energy_saving_percentage(),
            "%"
        )


if __name__ == "__main__":

    controller = NineZoneController()

    # First demand
    controller.request_zone(1)

    controller.display_status()

    # Demand moves to second zone
    controller.request_zone(2)

    controller.display_status()
